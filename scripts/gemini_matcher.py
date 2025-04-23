try:
    import streamlit as st
    import google.generativeai as genai
    import json
    import re

    # Configure Gemini
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
    except Exception as e:
        print(f"Error configuring Gemini: {e}")

except ImportError as e:
    print(f"Import error in gemini_matcher.py: {e}")

    # Fallback function that doesn't use missing modules
    def get_llm_feedback(resume_text: str, job_description: str) -> dict:
        return {
            "score": 0,
            "feedback": ["Failed to load Gemini module. Please check logs."],
        }


def get_llm_feedback(resume_text: str, job_description: str) -> dict:
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

        # Sanitize if Gemini adds markdown formatting (```json ... ```)
        if raw_text.startswith("```"):
            raw_text = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.IGNORECASE
            )

        parsed = json.loads(raw_text)

        # Extra check: truncate feedback to 3 if needed
        if isinstance(parsed, dict) and "feedback" in parsed:
            parsed["feedback"] = parsed["feedback"][:3]

        return parsed

    except Exception as e:
        return {"score": 0, "feedback": [f"❌ Unexpected error: {str(e)}"]}
