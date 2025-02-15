import pytesseract
import numpy as np
import cv2
from PIL import Image

# Set Tesseract executable path for Replit environment
pytesseract.pytesseract.tesseract_cmd = '/nix/store/rvl3l4hy1k12vwvvzh0n9l2lz6pww92h-tesseract-5.3.3/bin/tesseract'

def preprocess_for_ocr(image):
    """Preprocess image for better OCR results"""
    # Convert PIL Image to numpy array if needed
    if isinstance(image, Image.Image):
        image = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gray = cv2.dilate(gray, kernel, iterations=1)

    return gray

def extract_text(image):
    """Extract text from an image using Tesseract OCR"""
    try:
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Remove noise
        denoised = cv2.fastNlMeansDenoising(binary)

        # Scale up image for better OCR
        scaled = cv2.resize(denoised, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Configure tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!@#$%^&*()_+-=[]{}|;:"<>?/~ '

        # Try OCR with different settings
        configs = [
            custom_config,
            '--oem 3 --psm 1',  # Automatic page segmentation
            '--oem 3 --psm 3',  # Fully automatic page segmentation
            '--oem 3 --psm 4',  # Assume single column of text
            '--oem 3 --psm 6'   # Assume uniform block of text
        ]

        results = []
        for config in configs:
            try:
                text = pytesseract.image_to_string(scaled, config=config, lang='eng')
                if text and text.strip():
                    results.append(text.strip())
            except Exception as e:
                print(f"OCR error with config {config}: {str(e)}")
                continue

        if results:
            # Use the result with the most alphanumeric characters
            best_result = max(results, key=lambda x: sum(c.isalnum() for c in x))
            return best_result

        return pytesseract.image_to_string(scaled)  # Try one last time with default settings

    except Exception as e:
        print(f"OCR Error details: {str(e)}")
        return "Error: Could not extract text. Please try again with a clearer image."