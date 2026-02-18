import streamlit as st
import cv2
import numpy as np
import easyocr
import re
from db import DatabaseManager

# Page Config for Mobile
st.set_page_config(page_title="Car Inspector", layout="centered")

# Initialize OCR and DB
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()
db = DatabaseManager()

st.title("🚗 Vehicle Inspection")
st.markdown("---")

# 1. Vehicle Identity
plate = st.text_input("License Plate Number", placeholder="e.g. ABC-1234").upper()

# 2. Scanning Section
st.subheader("Step 1: Capture Data")
mode = st.radio("Choose what to scan:", ["Mileage (Odometer)", "Engine Number"])

# Camera Input Widget (Opens mobile camera automatically)
img_file = st.camera_input("Take Photo")

if img_file is not None:
    # Convert image to OpenCV format
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    with st.spinner('AI is reading text...'):
        # OCR Processing
        results = reader.readtext(image, detail=0)
        raw_text = " ".join(results).upper()
        
        # Clean data based on mode
        if "Mileage" in mode:
            digits = re.findall(r'\d+', raw_text)
            final_value = "".join(digits) if digits else "No numbers found"
            st.session_state['last_mileage'] = final_value
        else:
            st.session_state['last_engine'] = raw_text

# 3. Review Section
st.subheader("Step 2: Review & Save")

col1, col2 = st.columns(2)
with col1:
    mileage_val = st.text_input("Verified Mileage", value=st.session_state.get('last_mileage', ""))
with col2:
    engine_val = st.text_input("Verified Engine #", value=st.session_state.get('last_engine', ""))

if st.button("💾 SAVE TO DATABASE", use_container_width=True):
    if plate and (mileage_val or engine_val):
        db.save_entry(plate, mileage_val, engine_val)
        st.success(f"Successfully logged {plate}!")
        # Clear fields for next car
        st.session_state.clear()
    else:
        st.error("Please provide at least a Plate and one scan value.")