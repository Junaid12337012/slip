import json
from fpdf import FPDF
import io

def export_to_txt(text):
    """Export extracted text to TXT format"""
    return text.encode()

def export_to_pdf(text):
    """Export extracted text to PDF format"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Handle encoding issues and split text into lines
        lines = text.split('\n')
        for line in lines:
            try:
                # Remove any problematic characters
                clean_line = ''.join(char for char in line if ord(char) < 128)
                if clean_line:
                    pdf.cell(0, 10, txt=clean_line, ln=True)
            except Exception:
                continue
        
        # Save to bytes buffer
        return pdf.output(dest='S').encode('latin-1', errors='ignore')
    except Exception as e:
        raise Exception(f"PDF Generation Error: {str(e)}")

def export_to_json(text):
    """Export extracted text to JSON format"""
    # Split text into lines and create a structured format
    lines = text.split('\n')
    data = {
        "receipt_text": lines,
        "full_text": text
    }
    return json.dumps(data, ensure_ascii=False, indent=2).encode()
