
import pytesseract
import numpy as np
from PIL import Image

# Set Tesseract executable path for Replit environment
pytesseract.pytesseract.tesseract_cmd = '/nix/store/rvl3l4hy1k12vwvvzh0n9l2lz6pww92h-tesseract-5.3.3/bin/tesseract'

def extract_text(image):
    """Extract text from an image using Tesseract OCR"""
    try:
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image_array = np.array(image)
        else:
            image_array = image
            
        # Apply OCR
        text = pytesseract.image_to_string(image_array)
        return text.strip()
    except Exception as e:
        print(f"OCR Error details: {str(e)}")
        return "Error: Could not extract text. Please try again with a clearer image."
