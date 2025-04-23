from scripts.resume_parser import extract_text_from_pdf
from sentence_transformers import SentenceTransformer
from scripts.text_processing import preprocess_text

# Comment out the problematic import for now
# from scripts.gemini_matcher import get_llm_feedback
from scripts.matcher import calculate_match_score
from dotenv import load_dotenv
import streamlit as st


# Add a temporary placeholder function
def get_llm_feedback(resume_text, job_description):
    return {
        "match_score": 80,
        "feedback": "LLM integration temporarily disabled for cloud deployment.",
    }
