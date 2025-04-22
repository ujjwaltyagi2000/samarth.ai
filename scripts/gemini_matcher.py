import os
import google.generativeai as genai
import json
import re

# Load Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-pro-latest")


def get_llm_feedback(resume_text: str, job_description: str) -> dict:
    prompt = f"""
You are an AI resume evaluator.

Given the following job description and resume, analyze how well the resume matches the job description.
Please score the resume out of 100 and provide reasoning in 3-4 bullet points.

Job Description:
{job_description}

Resume:
{resume_text}

Respond in this JSON format:
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

        # Remove markdown-style code block formatting
        if raw_text.startswith("```"):
            raw_text = re.sub(
                r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.IGNORECASE
            )

        return json.loads(raw_text)
    except Exception as e:
        return {"score": 0, "feedback": [f"❌ Unexpected error: {str(e)}"]}
