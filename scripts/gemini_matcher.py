import os
import json
import re

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI library not available. Using fallback method.")

def get_llm_feedback(resume_text, job_description, use_fallback=False):
    if GEMINI_AVAILABLE and not use_fallback:
        # Your original Gemini code here
        # ...
    else:
        # Fallback method that doesn't require external APIs
        # This could be a simpler rule-based approach or using a different model
        # ...
        return {"match_score": 70, "feedback": "Fallback method used. Please check locally for detailed feedback."}