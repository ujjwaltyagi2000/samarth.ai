import streamlit as st
import pandas as pd  
import os

st.title("Samarth - Resume Matcher")  

# Upload the file
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    # Save the file to a temporary location
    save_path = os.path.join("uploads", uploaded_file.name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File saved at {save_path}")
