import pytesseract
import numpy as np
from PIL import Image


def extract_text(image):
    """Extract text from an image using Tesseract OCR"""
    try:
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image_array = np.array(image)
        else:
            image_array = image

        # Extract text using Tesseract
        text = pytesseract.image_to_string(image_array)
        return text.strip()
    except Exception as e:
        raise Exception(f"OCR Error: {str(e)}")
