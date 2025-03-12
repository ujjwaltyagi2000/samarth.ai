import streamlit as st  
import pandas as pd  

st.title("Samarth - Resume Matcher")  
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])  

if uploaded_file:  
    st.success("Resume uploaded! Processing...")  
    # Placeholder for parsing and matching logic  
    st.write("Basic keyword match score: **75%**")  # Dummy score  
