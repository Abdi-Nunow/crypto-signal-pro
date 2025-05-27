import streamlit as st
from google.cloud import vision
import io
import os
import json

# Ku dar key JSON (streamlit secrets)
vision_key = st.secrets["vision-key"]
with open("temp_key.json", "w") as f:
    f.write(vision_key)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_key.json"

def extract_text_google_vision(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    else:
        return "No text found"

st.title("📈 Crypto Signal Pro with Google OCR")

uploaded_file = st.file_uploader("Upload Chart", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    img_bytes = uploaded_file.read()
    st.image(uploaded_file, caption="Uploaded Chart", use_container_width=True)
    text = extract_text_google_vision(img_bytes)
    st.text(f"🔍 Extracted Text:\n{text}")
else:
    st.info("📂 Please upload a chart image.")
