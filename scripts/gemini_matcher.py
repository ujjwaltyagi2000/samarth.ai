import json
import re

try:
    import streamlit as st
    import google.generativeai as genai

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        GEMINI_AVAILABLE = True
    except Exception as e:
        print(f"Gemini config error: {e}")
        GEMINI_AVAILABLE = False

except ImportError as e:
    print(f"Import error: {e}")
    GEMINI_AVAILABLE = False


def get_llm_feedback(resume_text: str, job_description: str) -> dict:
    """Returns a relevance score and 3-point feedback from Gemini for resume matching."""
    if not GEMINI_AVAILABLE:
        return {
            "score": 0,
            "feedback": [
                "❌ Gemini model is unavailable. Check API key or package installation."
            ],
        }

    prompt = f"""
You are an AI resume evaluator.

Given the following job description and resume, analyze how well the resume matches the job description.
Please score the resume out of 100 and provide reasoning in exactly 3 concise bullet points. Do not give more than 3 points.

Job Description:
{job_description}

Resume:
{resume_text}

Respond in valid JSON format (no markdown code block, no extra characters):

{{
  "score": <score_out_of_100>,
  "feedback": [
    "point 1",
    "point 2",
    "point 3"
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Clean markdown formatting if present
        if raw_text.startswith("```"):
            raw_text = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.IGNORECASE
            )

        parsed = json.loads(raw_text)

        # Ensure feedback has at most 3 points
        parsed["feedback"] = parsed.get("feedback", [])[:3]

        return parsed

    except Exception as e:
        return {"score": 0, "feedback": [f"❌ Gemini error: {str(e)}"]}
