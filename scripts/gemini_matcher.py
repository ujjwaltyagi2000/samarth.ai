# scripts/gemini_matcher.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model (simple and clean)
model = genai.GenerativeModel("gemini-pro")


def get_llm_feedback(resume_text: str, job_description: str) -> dict:
    prompt = f"""
You are an AI resume evaluator.

Given the following job description and resume, analyze how well the resume matches the job description.
Please score the resume out of 100 and provide reasoning in 3-4 bullet points.

Job Description:
{job_description}

Resume:
{resume_text}

Give your response in the following JSON format:
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
        text_response = response.text.strip()

        # Extract and load JSON from response
        json_start = text_response.find("{")
        json_end = text_response.rfind("}") + 1
        json_str = text_response[json_start:json_end]

        return json.loads(json_str)

    except json.JSONDecodeError:
        return {"score": 0, "feedback": ["⚠️ LLM response was not valid JSON."]}

    except Exception as e:
        return {"score": 0, "feedback": [f"❌ Unexpected error: {str(e)}"]}
