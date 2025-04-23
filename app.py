import streamlit as st
from scripts.resume_parser import extract_text_from_pdf
from scripts.text_processing import preprocess_text
from scripts.matcher import calculate_match_score
from scripts.gemini_matcher import get_llm_feedback

import spacy
import subprocess
from dotenv import load_dotenv
import os
import time
from sentence_transformers import SentenceTransformer

import asyncio
import sys

if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

# Load SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Removed use_auth_token

# Download spaCy model if needed
try:
    spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])

# Title
st.title("Samarth - Resume Matcher")

# File upload
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file and "resume_text" not in st.session_state:
    st.success("Resume uploaded!", icon="✅")
    st.session_state.resume_text = extract_text_from_pdf(uploaded_file)

# Show resume text if available
if "resume_text" in st.session_state:
    with st.expander("Show Resume Content"):
        st.write(st.session_state.resume_text)

# Job Description input
st.subheader("Job Description")
jd_option = st.radio(
    "How would you like to provide the job description?",
    ("Text Input", "URL (LinkedIn/Naukri/Foundit)"),
)

if jd_option == "Text Input":
    job_description = st.text_area("Paste the job description here")
    if job_description:
        st.session_state.job_description = job_description
elif jd_option == "URL (LinkedIn/Naukri/Foundit)":
    jd_url = st.text_input("Enter the job posting URL")
    if jd_url:
        st.error("Scraping from URLs is not supported yet. Please use text input.")

# Processing logic
if st.button("Process Resume"):
    if not uploaded_file:
        st.error("Please upload a resume.")
    elif "job_description" not in st.session_state:
        st.error("Please provide a job description.")
    else:
        st.success("Resume and JD received! Processing...")
        processed_resume = preprocess_text(st.session_state.resume_text)
        processed_jd = preprocess_text(st.session_state.job_description)

        start_time = time.time()
        with st.spinner("Matching in progress..."):
            st.session_state.scores = calculate_match_score(
                processed_resume, processed_jd
            )
        end_time = time.time()

        st.session_state.time_taken = round(end_time - start_time, 2)
        st.success("Done!", icon="✅")

# Results display
if "scores" in st.session_state:
    scores = st.session_state.scores

    st.subheader("Match Score Summary")
    st.write(f"**Final Match Score:** {scores['final_score']}%")
    st.write(f"**Time Taken:** {st.session_state.time_taken} seconds")

    with st.expander("See Detailed Breakdown"):
        st.write(f"**Semantic Similarity Score:** {scores['semantic_score']}%")
        st.write(f"**Keyword Match Score:** {scores['keyword_score']}%")
        st.write(f"**Skill Match:** {scores['skill_match_ratio']:.2f}%")
        st.write(f"**Education Match:** {scores['edu_match_ratio']:.2f}%")
        st.write(f"**Role Match:** {'✅ Yes' if scores['role_match'] else '❌ No'}")
        st.write(f"**Experience Match:** {scores['exp_match_ratio']:.2f}%")
        st.caption(f"Resume Experience: {scores['resume_exp']} years")
        st.caption(f"JD Required Experience: {scores['jd_exp']} years")

    # Toggle for AI insights
    if st.toggle("💡 Get AI Insights"):
        with st.spinner("Generating insights..."):
            insights = get_llm_feedback(
                st.session_state.resume_text, st.session_state.job_description
            )
        st.markdown("#### Gemini LLM Insights")
        st.markdown(f"**Score:** {insights['score']}/100")
        st.markdown("**Feedback:**")
        for point in insights["feedback"]:
            st.markdown(f"- {point}")


# Footer
st.markdown(
    "Built by [Ujjwal Tyagi](https://ujjwaltyagi2000.github.io/) | [GitHub](https://github.com/ujjwaltyagi2000/samarth.ai)"
)
