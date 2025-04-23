import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import tempfile

# Import core functionality with fallback options
from scripts.resume_parser import extract_text_from_pdf
from scripts.text_processing import preprocess_text
from sentence_transformers import SentenceTransformer
from scripts.matcher import calculate_match_score

# Handle potential import issues with the LLM module
try:
    from scripts.gemini_matcher import get_llm_feedback, GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False

    # Define fallback function if import fails
    def get_llm_feedback(resume_text, job_description):
        return {
            "match_score": 50,
            "feedback": "LLM functionality not available in this deployment. For full features, check repository details.",
            "strengths": ["Basic matching functionality available"],
            "improvements": ["Deploy locally with API keys for detailed analysis"],
        }


# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Samarth.AI - Resume Job Matcher", page_icon="📄", layout="wide"
)

# Check if API keys are available from environment or secrets
has_api_keys = False
try:
    if "GEMINI_API_KEY" in os.environ or (
        "GEMINI_API_KEY" in st.secrets if hasattr(st, "secrets") else False
    ):
        has_api_keys = True
except Exception:
    pass

# Initialize app state if needed
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_desc_text" not in st.session_state:
    st.session_state.job_desc_text = ""
if "match_results" not in st.session_state:
    st.session_state.match_results = None
if "model" not in st.session_state:
    try:
        # Load the model when the app starts to avoid reloading it on each interaction
        st.session_state.model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    except Exception as e:
        st.error(f"Failed to load embedding model: {e}")
        st.session_state.model = None

# App title and description
st.title("Samarth.AI - Resume Job Matcher")
st.markdown(
    """
Upload your resume and a job description to see how well they match. 
Get personalized feedback and improve your chances of landing that interview!
"""
)

# Status indicator for LLM integration
with st.sidebar:
    st.header("App Status")
    if GEMINI_AVAILABLE and has_api_keys:
        st.success("✓ LLM integration active (full features available)")
    else:
        st.warning("⚠ Running in limited mode (basic matching only)")
        st.info("For full features, set up API keys locally. See README for details.")

    st.divider()
    st.header("About")
    st.markdown(
        """
    Samarth.AI helps job seekers match their resumes to job descriptions using:
    
    - PDF text extraction
    - Natural language processing
    - Semantic matching
    - AI-powered feedback (when available)
    
    Made with ❤️ by Ujjwal Tyagi
    """
    )

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.header("Upload Resume")
    uploaded_resume = st.file_uploader("Choose a resume PDF file", type="pdf")

    if uploaded_resume is not None:
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_resume.getvalue())
            tmp_path = tmp_file.name

        try:
            # Extract text from the resume PDF
            st.session_state.resume_text = extract_text_from_pdf(tmp_path)

            # Display the extracted text
            with st.expander("View Extracted Resume Text"):
                st.text_area("Resume Content", st.session_state.resume_text, height=300)

            # Clean up the temporary file
            os.unlink(tmp_path)

        except Exception as e:
            st.error(f"Error processing resume: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # Option to manually enter resume text
    st.divider()
    st.subheader("Or enter resume text manually")
    manual_resume = st.text_area(
        "Paste resume text here", height=200, value=st.session_state.resume_text
    )
    if manual_resume:
        st.session_state.resume_text = manual_resume

with col2:
    st.header("Enter Job Description")
    job_desc = st.text_area(
        "Paste the job description here",
        height=300,
        value=st.session_state.job_desc_text,
    )
    if job_desc:
        st.session_state.job_desc_text = job_desc

# Match button
if st.button(
    "Match Resume with Job Description", type="primary", use_container_width=True
):
    if not st.session_state.resume_text or not st.session_state.job_desc_text:
        st.error("Please provide both a resume and a job description.")
    else:
        with st.spinner("Analyzing your resume against the job description..."):
            try:
                # Preprocess the texts
                processed_resume = preprocess_text(st.session_state.resume_text)
                processed_job = preprocess_text(st.session_state.job_desc_text)

                # Basic matching using sentence transformers
                if st.session_state.model is not None:
                    similarity_score = calculate_match_score(
                        processed_resume, processed_job, st.session_state.model
                    )
                    basic_score = round(similarity_score * 100)
                else:
                    basic_score = None

                # Get feedback from LLM when available
                if GEMINI_AVAILABLE and has_api_keys:
                    llm_feedback = get_llm_feedback(
                        st.session_state.resume_text, st.session_state.job_desc_text
                    )
                else:
                    # Use fallback with basic info when LLM is not available
                    llm_feedback = {
                        "match_score": basic_score if basic_score is not None else 50,
                        "feedback": "Analysis based on keyword and semantic matching only. For detailed AI feedback, run the application locally with API keys.",
                        "strengths": [
                            "Automated analysis completed",
                            "Basic matching provided",
                        ],
                        "improvements": [
                            "Set up LLM integration for detailed feedback",
                            "Refer to the documentation for full feature setup",
                        ],
                    }

                # Store results in session state
                st.session_state.match_results = {
                    "basic_score": basic_score,
                    "llm_feedback": llm_feedback,
                }

            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.exception(e)

# Display results if available
if st.session_state.match_results:
    st.header("Match Results")

    results = st.session_state.match_results
    llm_feedback = results["llm_feedback"]

    # Create columns for scores and feedback
    score_col, feedback_col = st.columns([1, 2])

    with score_col:
        # Display the score as a gauge
        if "match_score" in llm_feedback:
            match_score = llm_feedback["match_score"]
            st.subheader(f"Match Score: {match_score}%")

            # Color the gauge based on the score
            if match_score >= 80:
                color = "green"
            elif match_score >= 60:
                color = "orange"
            else:
                color = "red"

            # Create a simple gauge with HTML
            st.markdown(
                f"""
            <div style="margin: 20px auto; width: 150px; height: 150px; border-radius: 50%; background: conic-gradient({color} {match_score}%, #f0f0f0 0%); display: flex; align-items: center; justify-content: center;">
                <div style="width: 120px; height: 120px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 24px; font-weight: bold;">{match_score}%</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Show basic score if available and different
            if (
                results["basic_score"] is not None
                and abs(results["basic_score"] - match_score) > 5
            ):
                st.caption(f"Semantic similarity score: {results['basic_score']}%")

    with feedback_col:
        # Display feedback
        st.subheader("Analysis")
        st.write(llm_feedback.get("feedback", "No detailed feedback available."))

        # Display strengths and improvements
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Strengths")
            strengths = llm_feedback.get("strengths", [])
            if strengths:
                for strength in strengths:
                    st.markdown(f"✅ {strength}")
            else:
                st.write("No specific strengths identified.")

        with col2:
            st.markdown("#### Areas for Improvement")
            improvements = llm_feedback.get("improvements", [])
            if improvements:
                for improvement in improvements:
                    st.markdown(f"🔍 {improvement}")
            else:
                st.write("No specific improvements identified.")

    # Recommendations section
    st.divider()
    st.subheader("What's Next?")
    st.markdown(
        """
    1. **Tailor your resume** to better match the job description
    2. **Highlight relevant skills** and experiences more prominently
    3. **Use keywords** from the job description in your resume
    4. **Quantify your achievements** with numbers and metrics
    5. **Review and resubmit** to see if your score improves
    """
    )

# Add a footer
st.divider()
st.caption(
    "Samarth.AI - Resume Job Matcher © 2025 | [GitHub Repository](https://github.com/ujjwaltyagi2000/samarth.ai)"
)
