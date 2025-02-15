
import json
from fpdf import FPDF
import io
from PIL import Image

def export_to_txt(text):
    """Export extracted text to TXT format"""
    return text.encode()

def export_to_pdf(text, image=None):
    """Export extracted text and image to PDF format"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)

        # Add image if provided
        if image:
            # Save image to temporary file
            temp_img_path = "temp_image.png"
            image.save(temp_img_path, format='PNG')

            # Calculate image dimensions to fit page
            page_width = pdf.w - 2 * pdf.l_margin
            page_height = pdf.h - 2 * pdf.t_margin

            # Get image size
            img_width, img_height = image.size

            # Calculate scaling factor to fit full page while maintaining aspect ratio
            width_ratio = page_width / img_width
            height_ratio = page_height / img_height
            scale = min(width_ratio, height_ratio) * 0.95  # 95% of page size for margins

            # Calculate new dimensions
            new_width = img_width * scale
            new_height = img_height * scale

            # Add image to PDF, centered both horizontally and vertically
            x = (page_width - new_width) / 2 + pdf.l_margin
            y = (page_height - new_height) / 2 + pdf.t_margin
            pdf.image(temp_img_path, x=x, y=y, w=new_width, h=new_height)

            # Clean up temporary file
            import os
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)

            # Move cursor below image
            pdf.ln(new_height + 10)

        # Add text
        lines = text.split('\n')
        for line in lines:
            try:
                clean_line = ''.join(char for char in line if ord(char) < 128)
                if clean_line:
                    pdf.cell(0, 10, txt=clean_line, ln=True)
            except Exception:
                continue

        return pdf.output(dest='S').encode('latin-1', errors='ignore')
    except Exception as e:
        raise Exception(f"PDF Generation Error: {str(e)}")

def export_to_json(text):
    """Export extracted text to JSON format"""
    lines = text.split('\n')
    data = {
        "receipt_text": lines,
        "full_text": text
    }
    return json.dumps(data, ensure_ascii=False, indent=2).encode()

def export_to_excel(text):
    """Export extracted text to Excel format"""
    import pandas as pd
    import io
    
    # Split text into lines and create a DataFrame
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    df = pd.DataFrame({'Extracted Text': lines})
    
    # Create Excel file in memory
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Extracted Text')
    
    return excel_buffer.getvalue()

def merge_images_to_pdf(images):
    """Merge multiple images into a single PDF"""
    try:
        pdf = FPDF()
        import os
        
        # Create unique temporary files for each image
        temp_files = []
        for idx, image in enumerate(images):
            temp_img_path = f"temp_image_{idx}.png"
            temp_files.append(temp_img_path)
            image.save(temp_img_path, format='PNG')
            
            pdf.add_page()
            
            # Calculate dimensions
            page_width = pdf.w - 2 * pdf.l_margin
            page_height = pdf.h - 2 * pdf.t_margin

            img_width, img_height = image.size
            width_ratio = page_width / img_width
            height_ratio = page_height / img_height
            scale = min(width_ratio, height_ratio)

            new_width = img_width * scale
            new_height = img_height * scale

            # Center image on page
            x = (page_width - new_width) / 2 + pdf.l_margin
            y = (page_height - new_height) / 2 + pdf.t_margin

            pdf.image(temp_img_path, x=x, y=y, w=new_width)

        # Clean up all temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return pdf.output(dest='S').encode('latin-1', errors='ignore')
    except Exception as e:
        raise Exception(f"PDF Merge Error: {str(e)}")
