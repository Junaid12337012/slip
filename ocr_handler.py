import pytesseract
from PIL import Image

def extract_text(image):
    """
    Extract text from the processed image using Tesseract OCR
    """
    try:
        # Configure Tesseract parameters
        custom_config = r'--oem 3 --psm 6'
        
        # Extract text
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Clean up the extracted text
        text = text.strip()
        
        if not text:
            return "No text was detected in the image. Please try with a clearer image."
        
        return text
    
    except Exception as e:
        raise Exception(f"Error in OCR processing: {str(e)}")
