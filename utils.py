import streamlit as st
from PIL import Image
import io

def load_image(uploaded_file):
    """Load and validate uploaded image"""
    try:
        image = Image.open(uploaded_file)
        return image
    except Exception as e:
        raise Exception("Error loading image. Please ensure it's a valid image file.")

def show_error(error_message):
    """Display error message in both English and Hindi"""
    st.error(f"""
    🚫 Error (त्रुटि):
    
    English: {error_message}
    
    Hindi: कृपया सही फ़ाइल अपलोड करें और पुनः प्रयास करें।
    """)
