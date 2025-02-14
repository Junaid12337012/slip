import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Document Scanner Pro Max",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/SlipTextConverter',
        'Report a bug': "https://github.com/yourusername/SlipTextConverter/issues",
        'About': "# Document Scanner Pro Max\nConvert and enhance your documents with AI."
    }
)

from PIL import Image
from image_processor import preprocess_image, ImageSettings
from utils import load_image, show_error
import io
import zipfile
import time
import base64
from datetime import datetime
import os

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #1E88E5;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        color: #333;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #424242;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        margin: 0.5rem 0;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background-color: #1976D2;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30,136,229,0.2);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem !important;
        font-weight: 600;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #1E88E5;
    }
    
    /* Sliders */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* File uploader */
    .stFileUploader {
        padding: 1rem;
        border: 2px dashed #1E88E5;
        border-radius: 8px;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    
    /* Success message */
    .success {
        padding: 1rem;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        margin: 1rem 0;
    }
    
    /* Error message */
    .error {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f44336;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_image_download_link(img, filename, text):
    """Generate a download link for an image"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}" style="text-decoration:none;"><button style="background-color:#1E88E5;color:white;padding:0.5rem 1rem;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">{text}</button></a>'
    return href

def init_session_state():
    """Initialize all session state variables"""
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'processed_images' not in st.session_state:
        st.session_state.processed_images = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'upload'
    if 'processing_error' not in st.session_state:
        st.session_state.processing_error = None

def main():
    # Initialize all session state variables
    init_session_state()

    # Main title with animation
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>📷 Document Scanner Pro Max</h1>
            <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
                Convert and enhance your documents with advanced AI technology
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Animated introduction
    st.markdown("""
    <div style='text-align: center; padding: 2rem; animation: fadeIn 1s ease-in;'>
        <h3>🚀 Professional Document Scanner with AI-Powered Enhancement</h3>
        <p style='font-size: 1.2rem; color: #666;'>Transform your documents with cutting-edge technology!</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature showcase
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("### ✨ Auto Enhance")
        st.markdown("Smart image enhancement")
    with col2:
        st.markdown("### 📐 Smart Crop")
        st.markdown("Automatic edge detection")
    with col3:
        st.markdown("### 🎨 Color Correct")
        st.markdown("Advanced color processing")
    with col4:
        st.markdown("### 🔄 Batch Process")
        st.markdown("Handle multiple files")

    # Sidebar with custom styling
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h2 style='color: #1E88E5;'>⚙️ Settings</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Image format selection
        image_format = st.selectbox(
            "Select Output Format",
            ["PNG", "JPEG", "PDF"],
            index=0
        )
        
        # Quality settings based on format
        if image_format in ["JPEG", "PDF"]:
            export_quality = st.slider(
                "Quality",
                min_value=1,
                max_value=100,
                value=95,
                help="Higher quality means larger file size"
            )
        else:
            export_quality = 95

    # Advanced Settings Sidebar
    st.sidebar.title("⚙️ Advanced Settings")
    
    # Image Processing Settings
    st.sidebar.subheader("Image Processing")
    
    # CLAHE settings
    clahe_limit = st.sidebar.slider(
        "Contrast Limit",
        min_value=1.0,
        max_value=5.0,
        value=3.5,
        step=0.5,
        help="Adjust contrast enhancement level"
    )
    
    # Contrast and Brightness
    contrast = st.sidebar.slider(
        "Contrast",
        min_value=0.5,
        max_value=2.0,
        value=1.3,
        step=0.1,
        help="Adjust image contrast"
    )
    
    brightness = st.sidebar.slider(
        "Brightness",
        min_value=0.5,
        max_value=2.0,
        value=1.15,
        step=0.05,
        help="Adjust image brightness"
    )
    
    # Sharpness
    sharpness = st.sidebar.slider(
        "Sharpness",
        min_value=0.5,
        max_value=2.0,
        value=1.4,
        step=0.1,
        help="Adjust image sharpness"
    )
    
    # Edge Detection Settings
    st.sidebar.subheader("Edge Detection")
    canny_low = st.sidebar.slider(
        "Edge Detection Sensitivity",
        min_value=20,
        max_value=100,
        value=50,
        help="Lower value means more sensitive edge detection"
    )
    
    canny_high = st.sidebar.number_input(
        "Edge Detection Threshold",
        min_value=100,
        max_value=200,
        value=150,
        help="Higher value means stronger edges required"
    )
    
    # Main content area
    st.markdown("### 📤 Upload Documents")
    uploaded_files = st.file_uploader(
        "Drag and drop your files here",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Support for PNG, JPG, JPEG formats"
    )

    if uploaded_files:
        process_col1, process_col2, process_col3 = st.columns([1, 2, 1])
        with process_col2:
            process_btn = st.button("🔄 Process Documents", use_container_width=True)

        if process_btn:
            # Clear previous results and errors
            st.session_state.processed_files = []
            st.session_state.processed_images = []
            st.session_state.processing_error = None
            
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    # Check file size
                    if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
                        raise ValueError(f"File {uploaded_file.name} is too large. Maximum size is 10MB")
                        
                    # Create custom settings based on user input
                    custom_settings = ImageSettings()
                    custom_settings.clahe_clip_limit = clahe_limit
                    custom_settings.contrast = contrast
                    custom_settings.brightness = brightness
                    custom_settings.sharpness = sharpness
                    custom_settings.canny_low = canny_low
                    custom_settings.canny_high = canny_high
                    
                    # Load and process image with error handling
                    try:
                        image = load_image(uploaded_file)
                        if image.size[0] * image.size[1] > 25000000:  # Limit image dimensions
                            image = image.resize((int(image.size[0]/2), int(image.size[1]/2)))
                        enhanced_versions = preprocess_image(image, custom_settings)
                    except Exception as e:
                        raise ValueError(f"Error processing {uploaded_file.name}: {str(e)}")
                    
                    # Store processed image data with memory management
                    img_byte_arr = io.BytesIO()
                    try:
                        if image_format == "PDF":
                            enhanced_versions[0][1].save(
                                img_byte_arr,
                                format='PDF',
                                resolution=300,
                                quality=export_quality
                            )
                        else:
                            enhanced_versions[0][1].save(
                                img_byte_arr,
                                format=image_format,
                                quality=export_quality if image_format == "JPEG" else None
                            )
                    except Exception as e:
                        raise ValueError(f"Error saving {uploaded_file.name}: {str(e)}")
                        
                    file_name = f"{os.path.splitext(uploaded_file.name)[0]}.{image_format.lower()}"
                    mime_type = f"application/{image_format.lower()}" if image_format == "PDF" else f"image/{image_format.lower()}"
                    
                    # Store in session state
                    st.session_state.processed_files.append({
                        'name': file_name,
                        'data': img_byte_arr.getvalue(),
                        'mime': mime_type
                    })
                    
                    st.session_state.processed_images.append({
                        'name': uploaded_file.name,
                        'original': image,
                        'processed': enhanced_versions[0][1],
                        'type': enhanced_versions[0][0]
                    })
                    
                    # Update progress
                    progress = (idx + 1) / len(uploaded_files)
                    progress_bar = st.progress(progress)
                    
                except Exception as e:
                    st.session_state.processing_error = str(e)
                    st.error(f"Error: {str(e)}")
                    continue
            
            # Complete progress bar
            progress_bar.progress(1.0)
            
            if not st.session_state.processing_error:
                st.success("✅ All documents processed successfully!")
            else:
                st.warning("⚠️ Some files were processed with errors. See above for details.")

        # Display all processed images (always show if available)
        if st.session_state.processed_images:
            st.markdown("## 📄 Processed Documents")
            
            # Add tabs for better organization
            tab1, tab2 = st.tabs(["📸 Image Preview", "📥 Downloads"])
            
            with tab1:
                for img_data in st.session_state.processed_images:
                    with st.expander(f"📄 {img_data['name']}", expanded=True):
                        # Create columns for before/after comparison
                        comp_col1, comp_col2 = st.columns(2)
                        
                        with comp_col1:
                            st.markdown("**Original Document**")
                            st.image(img_data['original'], use_container_width=True, caption="Original")
                        
                        with comp_col2:
                            st.markdown(f"**{img_data['type']}**")
                            st.image(img_data['processed'], use_container_width=True, caption="Processed")
                            
                            # Add download button directly under the processed image
                            for file_data in st.session_state.processed_files:
                                if file_data['name'].startswith(os.path.splitext(img_data['name'])[0]):
                                    st.download_button(
                                        label="📥 Download This Image",
                                        data=file_data['data'],
                                        file_name=file_data['name'],
                                        mime=file_data['mime'],
                                        key=f"download_inline_{img_data['name']}_{time.time()}",
                                        use_container_width=True
                                    )
                                    break
            
            # Add batch download section at the bottom
            if st.session_state.processed_files:
                st.markdown("---")
                st.markdown("""
                    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;'>
                        <h2 style='margin-bottom: 10px;'>📦 Batch Download Options</h2>
                    </div>
                """, unsafe_allow_html=True)
                
                try:
                    # Create ZIP file with all processed documents
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
                        for file_data in st.session_state.processed_files:
                            zip_file.writestr(file_data['name'], file_data['data'])
                    
                    zip_buffer.seek(0)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 DOWNLOAD ALL AS ZIP",
                            data=zip_buffer.getvalue(),
                            file_name=f"all_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            key=f"download_all_zip_{time.time()}",
                            use_container_width=True
                        )
                    with col2:
                        st.markdown("""
                            <div style='background-color: #fff; padding: 10px; border-radius: 5px; text-align: center;'>
                                <p>Or download individually above under each processed image</p>
                            </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Download Error: {str(e)}")
            
            with tab2:
                if st.session_state.processed_files:
                    # Add prominent download all button
                    st.markdown("""
                        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                            <h3 style='margin-bottom: 10px;'>📦 Quick Download All</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        # Create ZIP file option
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
                            for file_data in st.session_state.processed_files:
                                zip_file.writestr(file_data['name'], file_data['data'])
                        
                        zip_buffer.seek(0)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 DOWNLOAD ALL AS ZIP",
                                data=zip_buffer.getvalue(),
                                file_name=f"all_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip",
                                key=f"download_all_zip_{time.time()}",
                                use_container_width=True,
                                help="Download all files in a ZIP archive"
                            )
                        
                        # Add batch download buttons for all images
                        with col2:
                            st.markdown("### Or download all individually:")
                            for file_data in st.session_state.processed_files:
                                st.download_button(
                                    label=f"📥 Download {file_data['name']}",
                                    data=file_data['data'],
                                    file_name=file_data['name'],
                                    mime=file_data['mime'],
                                    key=f"batch_download_{file_data['name']}_{time.time()}"
                                )
                        
                        # Divider
                        st.markdown("---")
                        
                        # Individual downloads section
                        st.markdown("""
                            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                                <h3 style='margin-bottom: 10px;'>📄 Download Individual Files</h3>
                                <p>Select and download files one by one</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Create a grid for individual downloads
                        for idx, file_data in enumerate(st.session_state.processed_files):
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"**{file_data['name']}**")
                                with col2:
                                    st.download_button(
                                        label="📥 Download",
                                        data=file_data['data'],
                                        file_name=file_data['name'],
                                        mime=file_data['mime'],
                                        key=f"download_file_{idx}_{time.time()}",
                                        use_container_width=True
                                    )
                                st.markdown("---")
                    except Exception as e:
                        st.error(f"❌ Download Error: {str(e)}\nPlease try again or contact support if the issue persists.")
                else:
                    st.warning("📝 No processed files yet! Please upload and process some documents first.")
                    st.markdown("""
                        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
                            <h4>How to get your downloads:</h4>
                            <ol>
                                <li>Upload your documents using the file uploader above</li>
                                <li>Click the 'Process Documents' button</li>
                                <li>Return to this tab to download your processed files</li>
                            </ol>
                        </div>
                    """, unsafe_allow_html=True)

    # Tips and Help Section
    with st.expander("💡 Pro Tips for Perfect Scans", expanded=False):
        st.markdown("""
        ### 📸 Capture Tips
        1. **Lighting**: Ensure even lighting across the document
        2. **Background**: Use a dark, contrasting background
        3. **Alignment**: Keep document edges parallel to frame edges
        4. **Stability**: Hold the camera steady or use a surface
        
        ### 🎯 Best Practices
        - Clean your camera lens for sharp images
        - Avoid shadows and reflections
        - Keep documents flat while scanning
        - Use auto-crop for perfect alignment
        
        ### 🚀 Processing Tips
        - Adjust enhancement level based on document type
        - Use higher export quality for important documents
        - Batch process similar documents together
        - Save in PDF format for official documents
        """)

    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #666; font-size: 0.8rem;'>
        Document Scanner Pro Max &copy; 2025 | Made with &hearts;
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
