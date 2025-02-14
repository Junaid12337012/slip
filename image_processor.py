import cv2
import numpy as np
from PIL import Image, ImageEnhance

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

class ImageSettings:
    def __init__(self):
        # Updated default settings as per user preference
        self.clahe_clip_limit = 4.0
        self.clahe_grid_size = (8, 8)
        self.canny_low = 100
        self.canny_high = 200
        self.gaussian_kernel = (5, 5)
        self.max_dimension = 2000
        self.contrast = 1.0
        self.brightness = 1.9
        self.sharpness = 2.0

def enhance_image(image_array, settings=None):
    """Apply optimized image enhancement techniques"""
    if settings is None:
        settings = ImageSettings()
    
    # Convert to LAB color space
    lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel with optimized settings
    clahe = cv2.createCLAHE(clipLimit=settings.clahe_clip_limit, 
                           tileGridSize=settings.clahe_grid_size)
    cl = clahe.apply(l)
    
    # Merge channels
    limg = cv2.merge((cl, a, b))
    
    # Convert back to RGB
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # Optimize contrast and brightness
    enhanced = cv2.convertScaleAbs(enhanced, 
                                  alpha=settings.contrast,
                                  beta=settings.brightness * 10)
    
    # Ensure the image is in uint8 format
    enhanced = enhanced.astype(np.uint8)
    
    # Convert to PIL for sharpness
    enhanced_pil = Image.fromarray(enhanced)
    
    # Apply sharpness enhancement
    try:
        enhancer = ImageEnhance.Sharpness(enhanced_pil)
        enhanced_pil = enhancer.enhance(settings.sharpness)
        return np.array(enhanced_pil)
    except Exception:
        return enhanced

def detect_document_corners(image_array, settings=None):
    """Detect document corners using edge detection and contour finding"""
    if settings is None:
        settings = ImageSettings()

    # Convert to grayscale if needed
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_array

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, settings.gaussian_kernel, 0)
    
    # Adaptive thresholding for better text detection
    thresh = cv2.adaptiveThreshold(blurred, 255, 
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Edge detection with custom settings
    edges = cv2.Canny(thresh, settings.canny_low, settings.canny_high)
    
    # Dilate edges to connect components
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get the perimeter of the contour
    peri = cv2.arcLength(largest_contour, True)
    
    # Approximate the contour
    approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
    
    # If we found 4 points, return them
    if len(approx) == 4:
        return approx.reshape(4, 2)
    
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

def preprocess_image(pil_image, custom_settings=None, auto_crop=True):
    """Enhanced image processing with smart document detection"""
    if custom_settings is None:
        custom_settings = ImageSettings()
        
    # Convert PIL image to numpy array
    image_array = np.array(pil_image)
    
    if auto_crop:
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # Apply edge detection with optimized parameters
        edges = cv2.Canny(thresh, 50, 150)
        kernel = np.ones((5,5), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=3)
        edges = cv2.erode(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Filter contours by area to avoid noise
            valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000]
            if valid_contours:
                # Find the contour with largest area
                max_contour = max(valid_contours, key=cv2.contourArea)
                peri = cv2.arcLength(max_contour, True)
                approx = cv2.approxPolyDP(max_contour, 0.02 * peri, True)
                
                # If we have a rectangle (4 points), use it directly
                if len(approx) == 4:
                    box = np.float32(approx)
                else:
                    # Otherwise use minimum area rectangle
                    rect = cv2.minAreaRect(max_contour)
                    box = cv2.boxPoints(rect)
                    box = np.float32(box)
            
            # Get width and height of the detected rectangle
            width = int(rect[1][0])
            height = int(rect[1][1])
            
            src_pts = box.astype("float32")
            dst_pts = np.array([[0, height-1],
                              [0, 0],
                              [width-1, 0],
                              [width-1, height-1]], dtype="float32")
            
            # Apply perspective transform
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            image_array = cv2.warpPerspective(image_array, M, (width, height))
    if custom_settings is None:
        custom_settings = ImageSettings()
        
    # Convert PIL image to numpy array
    image_array = np.array(pil_image)
    
    # Store original dimensions
    original_height, original_width = image_array.shape[:2]
    
    # Resize if image is too large (helps with processing speed)
    if max(original_height, original_width) > custom_settings.max_dimension:
        scale = custom_settings.max_dimension / max(original_height, original_width)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        image_array = cv2.resize(image_array, (new_width, new_height))
    
    # Enhance the image with custom settings
    enhanced = enhance_image(image_array, custom_settings)
    enhanced_pil = Image.fromarray(enhanced)
    
    return [
        ("Enhanced", enhanced_pil),
        ("Original", pil_image)
    ]
