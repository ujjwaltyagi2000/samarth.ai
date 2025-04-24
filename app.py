from scripts.resume_parser import extract_text_from_pdf
from sentence_transformers import SentenceTransformer
from scripts.text_processing import preprocess_text
from scripts.gemini_matcher import get_llm_feedback
from scripts.matcher import calculate_match_score
from dotenv import load_dotenv
import streamlit as st
import subprocess
import asyncio
import spacy
import time
import sys
import os

st.set_page_config(
    page_title="Samarth – Resume Matcher",
    page_icon="📝",  # Optional: pick an emoji or a favicon path
    layout="centered",  # or "wide"
    initial_sidebar_state="auto",
)

# Compatibility for Windows + asyncio
if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

# Initialize model only once
if "model" not in st.session_state:
    st.session_state.model = SentenceTransformer("all-MiniLM-L6-v2")

# Load spaCy model if not already loaded
if "spacy_loaded" not in st.session_state:
    nlp = spacy.load("en_core_web_sm")


# App title
st.title("Samarth - Resume Matcher")

# Upload resume
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
if uploaded_file and "resume_text" not in st.session_state:
    with st.spinner("Extracting text from resume..."):
        st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
    st.success("Resume uploaded ✅")

# Show resume content
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
    st.text_input("Enter the job posting URL")
    st.error("Scraping from URLs is not supported yet. Please use text input.")


# Resume processing function
def process_resume(resume_text, job_description):
    start_time = time.time()

    processed_resume = preprocess_text(resume_text)
    processed_jd = preprocess_text(job_description)
    scores = calculate_match_score(processed_resume, processed_jd)

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    return scores, time_taken


# Button: Process Resume
if st.button("Process Resume"):
    if not uploaded_file:
        st.error("Please upload a resume.")
    elif "job_description" not in st.session_state:
        st.error("Please provide a job description.")
    else:
        with st.spinner("Matching in progress..."):
            scores, time_taken = process_resume(
                st.session_state.resume_text, st.session_state.job_description
            )
            st.session_state.scores = scores
            st.session_state.time_taken = time_taken
        st.success("Matching complete ✅")

# Results Display
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

    # AI Insights
    if st.toggle("💡 Get AI Insights"):
        with st.spinner("Generating insights with Gemini..."):
            insights = get_llm_feedback(
                st.session_state.resume_text, st.session_state.job_description
            )
        st.markdown("#### Gemini LLM Insights")
        st.markdown(f"**Score:** {insights['score']}/100")
        st.markdown("**Feedback:**")
        for point in insights["feedback"]:
            st.markdown(f"- {point}")

        feedback_text = f"Score: {insights['score']}/100\n\nFeedback:\n" + "\n".join(
            f"- {pt}" for pt in insights["feedback"]
        )

        st.write("🔐 Gemini API Key exists:", "GEMINI_API_KEY" in st.secrets)

        # Download insights as .txt button
        st.download_button(
            label="📄 Download Feedback",
            data=feedback_text,
            file_name="samarth_feedback.txt",
            mime="text/plain",
        )

# Footer
st.markdown(
    "Built by [Ujjwal Tyagi](https://ujjwaltyagi2000.github.io/) | [GitHub](https://github.com/ujjwaltyagi2000/samarth.ai)"
)
