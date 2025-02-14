import json
from fpdf import FPDF
import io

def export_to_txt(text):
    """Export extracted text to TXT format"""
    return text.encode()

def export_to_pdf(text):
    """Export extracted text to PDF format"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split text into lines and add to PDF
    lines = text.split('\n')
    for line in lines:
        pdf.cell(0, 10, txt=line, ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

def export_to_json(text):
    """Export extracted text to JSON format"""
    # Split text into lines and create a structured format
    lines = text.split('\n')
    data = {
        "receipt_text": lines,
        "full_text": text
    }
    return json.dumps(data, ensure_ascii=False, indent=2).encode()
