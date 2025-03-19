import streamlit as st
from scripts.resume_parser import extract_text_from_pdf
from scripts.text_processing import preprocess_text
from scripts.matcher import calculate_match_score

st.title("Samarth.AI - Resume Matcher")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

# Job Description Input
st.subheader("Job Description")
jd_option = st.radio(
    "How would you like to provide the job description?",
    ("Text Input", "URL (LinkedIn/Naukri/Foundit)")
)

job_description = None
jd_url = None

if jd_option == "Text Input":
    job_description = st.text_area("Paste the job description here")
elif jd_option == "URL (LinkedIn/Naukri/Foundit)":
    jd_url = st.text_input("Enter the job posting URL (LinkedIn/Foundit/Naukri)")

# Display warnings only after clicking the "Process" button
if st.button("Process Resume"):
    if not uploaded_file:
        st.error("Please upload a resume.")
    elif not job_description:
        st.error("Please provide the job description.")
    else:
        st.success("Resume uploaded! Processing...")

        # Extract and preprocess text
        resume_text = extract_text_from_pdf(uploaded_file)
        processed_resume = preprocess_text(resume_text)
        processed_job_desc = preprocess_text(job_description)

        # Compute match score
        match_score = calculate_match_score(processed_resume, processed_job_desc)

        st.write(f"**Match Score:** {match_score}%")
