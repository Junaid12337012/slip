import cv2
import numpy as np
from PIL import Image, ImageEnhance

class ImageSettings:
    def __init__(self):
        # Image enhancement settings
        self.clahe_clip_limit = 3.0
        self.clahe_grid_size = (8, 8)
        self.canny_low = 50
        self.canny_high = 150
        self.gaussian_kernel = (3, 3)
        self.max_dimension = 2000
        self.contrast = 1.6
        self.brightness = 1.5
        self.sharpness = 1.4
        self.shadow_reduction = 0.25
        self.noise_reduction = True
        self.auto_rotate = True
        
        # New advanced settings
        self.denoise_strength = 10
        self.saturation = 1.2
        self.gamma = 1.0
        self.color_balance = {
            'red': 1.0,
            'green': 1.0,
            'blue': 1.0
        }
        self.edge_enhancement = 1.0
        self.deskew_angle = 0
        self.bw_mode = False
        self.detail_enhancement = 1.0

def order_points(pts):
    """Order points in clockwise order: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    """Apply perspective transform to get top-down view"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Compute width of new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Compute height of new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Construct set of destination points
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # Calculate perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def enhance_image(image_array, settings=None):
    if settings is None:
        settings = ImageSettings()

    # Convert to PIL Image for enhancement chain
    image_pil = Image.fromarray(image_array)
    
    # Apply denoising if enabled
    if settings.noise_reduction:
        image_array = cv2.fastNlMeansDenoisingColored(
            np.array(image_pil), 
            None, 
            settings.denoise_strength, 
            settings.denoise_strength
        )
        image_pil = Image.fromarray(image_array)

    # Apply color balance
    r, g, b = image_pil.split()
    r = r.point(lambda x: x * settings.color_balance['red'])
    g = g.point(lambda x: x * settings.color_balance['green'])
    b = b.point(lambda x: x * settings.color_balance['blue'])
    image_pil = Image.merge('RGB', (r, g, b))

    # Apply basic enhancements
    enhancers = {
        'Contrast': ImageEnhance.Contrast(image_pil),
        'Brightness': ImageEnhance.Brightness(image_pil),
        'Sharpness': ImageEnhance.Sharpness(image_pil),
        'Color': ImageEnhance.Color(image_pil)
    }
    
    image_pil = enhancers['Contrast'].enhance(settings.contrast)
    image_pil = enhancers['Brightness'].enhance(settings.brightness)
    image_pil = enhancers['Sharpness'].enhance(settings.sharpness)
    image_pil = enhancers['Color'].enhance(settings.saturation)

    # Convert to LAB for CLAHE
    image_array = np.array(image_pil)
    lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(
        clipLimit=settings.clahe_clip_limit, 
        tileGridSize=settings.clahe_grid_size
    )
    cl = clahe.apply(l)
    
    # Merge back
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # Convert to black and white if enabled
    if settings.bw_mode:
        enhanced_pil = Image.fromarray(enhanced).convert('L')
        enhanced = np.array(enhanced_pil)
        
    # Apply edge enhancement if needed
    if settings.edge_enhancement > 1.0:
        edge_enhanced = cv2.Laplacian(enhanced, cv2.CV_8U)
        enhanced = cv2.addWeighted(
            enhanced, 1, 
            edge_enhanced, settings.edge_enhancement - 1, 
            0
        )
    
    return enhanced

def detect_document_corners(image_array, settings=None):
    """Detect document corners using edge detection and contour finding"""
    try:
        if settings is None:
            settings = ImageSettings()

        # Input validation
        if image_array is None or not isinstance(image_array, np.ndarray):
            return None

        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array.astype(np.uint8)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Use Canny edge detection with automatic threshold
        median = np.median(blurred)
        sigma = 0.33
        lower = int(max(0, (1.0 - sigma) * median))
        upper = int(min(255, (1.0 + sigma) * median))
        edges = cv2.Canny(blurred, lower, upper) 
        #The following lines were causing an error and were removed as they were not present in the original code
        #cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #cv2.THRESH_BINARY, 11, 2)

        # Edge detection with custom settings
        edges = cv2.Canny(blurred, settings.canny_low, settings.canny_high)

        # Dilate edges to connect components
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        # Dilate edges to connect components
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get the minimum area rectangle
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        
        # Convert to float32 for perspective transform
        return box.astype(np.float32)

    except Exception as e:
        print(f"Error during contour processing: {e}")
        return None


def auto_process_image(image_path):
    """Automatically process an image and save with the same filename"""
    try:
        # Read the image
        pil_image = Image.open(image_path)

        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Process image with optimized settings
        image_array = np.array(pil_image)

        # Auto-detect if it's a document
        corners = detect_document_corners(image_array)

        if corners is not None:
            # It's a document - apply perspective transform
            warped = four_point_transform(image_array, corners)
            enhanced = enhance_image(warped)
        else:
            # Not a document - just enhance
            enhanced = enhance_image(image_array)

        # Convert back to PIL Image
        result_image = Image.fromarray(enhanced)

        # Save with same filename
        result_image.save(image_path)
        return True

    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return False

def preprocess_image(pil_image, settings=None, auto_crop=True):
    if settings is None:
        settings = ImageSettings()

    # Convert PIL image to numpy array
    image_array = np.array(pil_image)

    # Store original dimensions
    original_height, original_width = image_array.shape[:2]

    # Resize if image is too large
    if max(original_height, original_width) > settings.max_dimension:
        scale = settings.max_dimension / max(original_height, original_width)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        image_array = cv2.resize(image_array, (new_width, new_height))

    # Enhance the image
    enhanced = enhance_image(image_array, settings)
    enhanced_pil = Image.fromarray(enhanced)

    return [
        ("Enhanced", enhanced_pil),
        ("Original", pil_image)
    ]