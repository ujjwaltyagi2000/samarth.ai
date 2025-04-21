import streamlit as st
from scripts.resume_parser import extract_text_from_pdf
from scripts.text_processing import preprocess_text
import time

from scripts.matcher import calculate_match_score

st.title("Samarth - Resume Matcher")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("Resume uploaded!", icon="✅")
    resume_text = extract_text_from_pdf(uploaded_file)
    with st.expander("Show Resume Content"):
        st.write(resume_text)

# Job Description Input
st.subheader("Job Description")
jd_option = st.radio(
    "How would you like to provide the job description?",
    ("Text Input", "URL (LinkedIn/Naukri/Foundit)"),
)

job_description = None
jd_url = None

if jd_option == "Text Input":
    job_description = st.text_area("Paste the job description here")
elif jd_option == "URL (LinkedIn/Naukri/Foundit)":
    jd_url = st.text_input("Enter the job posting URL (LinkedIn/Foundit/Naukri)")
    if jd_url:
        st.error(
            "Scraping from job URLs is not yet supported. Please paste the JD manually for now."
        )

# Display warnings only after clicking the "Process" button
if st.button("Process Resume"):
    if not uploaded_file:
        st.error("Please upload a resume.")
    elif jd_option == "Text Input" and not job_description:
        st.error("Please provide the job description.")
    elif jd_option == "URL (LinkedIn/Naukri/Foundit)":
        st.error("This feature is not available yet. Please use the text input option.")
    else:
        st.success("Resume and Job Description received! Processing...")

        # Extract and preprocess text
        processed_resume = preprocess_text(resume_text)
        processed_job_desc = preprocess_text(job_description)

        start_time = time.time()
        with st.spinner("Wait for it..."):

            # Compute match scores and breakdown
            scores = calculate_match_score(processed_resume, processed_job_desc)

        end_time = time.time()
        st.success("Done!", icon="✅")

        # Display results
        st.subheader("Match Score Summary")
        st.write(f"**Final Match Score:** {scores['final_score']}%")
        st.write(f"**Time Taken:** {round(end_time - start_time, 2)} seconds")

        with st.expander("See Detailed Breakdown"):
            st.write(f"**Semantic Similarity Score:** {scores['semantic_score']}%")
            st.write(f"**Keyword Match Score:** {scores['keyword_score']}%")
            st.write(f"**Skill Match:** {scores['skill_match_ratio']:.2f}%")
            st.write(f"**Education Match:** {scores['edu_match_ratio']:.2f}%")
            st.write(f"**Role Match:** {'✅ Yes' if scores['role_match'] else '❌ No'}")
            st.write(f"**Experience Match:** {scores['exp_match_ratio']:.2f}%")
            st.caption(f"Resume Experience: {scores['resume_exp']} years")
            st.caption(f"JD Required Experience: {scores['jd_exp']} years")


# Footer
st.markdown(
    "Built by [Ujjwal Tyagi](https://ujjwaltyagi2000.github.io/) | [GitHub](https://github.com/ujjwaltyagi2000/samarth.ai)"
)
