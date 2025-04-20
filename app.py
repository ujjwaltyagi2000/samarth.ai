import streamlit as st
from scripts.resume_parser import extract_text_from_pdf
from scripts.text_processing import preprocess_text
from scripts.matcher import calculate_match_score

st.title("Samarth.AI - Resume Matcher")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste Job Description")

if uploaded_file and job_description:
    st.success("Resume uploaded! Processing...")

        # Extract and preprocess text
        resume_text = extract_text_from_pdf(uploaded_file)
        processed_resume = preprocess_text(resume_text)
        processed_job_desc = preprocess_text(job_description)

        # Compute match score
        match_score = calculate_match_score(processed_resume, processed_job_desc)

    st.write(f"**Match Score:** {match_score}%")
