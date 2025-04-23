import os
import json
import re

# Try to import Google's Generative AI library, but don't crash if it's not available
try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI library not available. Using fallback method.")


def get_llm_feedback(resume_text, job_description):
    """Get feedback from an LLM on how well a resume matches a job description."""

    if GEMINI_AVAILABLE:
        try:
            # Set up the API key
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print(
                    "GEMINI_API_KEY not found in environment variables. Using fallback."
                )
                return _fallback_feedback(resume_text, job_description)

            genai.configure(api_key=api_key)

            # Your original Gemini code here
            # For example:
            model = genai.GenerativeModel("gemini-pro")

            prompt = f"""
            You are an expert HR professional. Analyze the resume and job description provided below.
            
            RESUME:
            {resume_text}
            
            JOB DESCRIPTION:
            {job_description}
            
            Provide feedback in JSON format with the following structure:
            {{
                "match_score": <score from 0-100>,
                "feedback": "<detailed feedback>",
                "strengths": ["<strength 1>", "<strength 2>", ...],
                "improvements": ["<improvement 1>", "<improvement 2>", ...]
            }}
            
            Only return the JSON, no additional text.
            """

            response = model.generate_content(prompt)
            response_text = response.text

            # Clean up the response to extract just the JSON
            response_text = re.sub(r"^```json", "", response_text)
            response_text = re.sub(r"```$", "", response_text)
            response_text = response_text.strip()

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                print("Failed to parse JSON from Gemini response. Using fallback.")
                return _fallback_feedback(resume_text, job_description)

        except Exception as e:
            print(f"Error using Gemini API: {e}")
            return _fallback_feedback(resume_text, job_description)
    else:
        return _fallback_feedback(resume_text, job_description)


def _fallback_feedback(resume_text, job_description):
    """Provide a basic fallback when the LLM is not available."""
    # Simple keyword matching algorithm
    job_keywords = set(_extract_keywords(job_description.lower()))
    resume_keywords = set(_extract_keywords(resume_text.lower()))

    # Find matching keywords
    matching_keywords = job_keywords.intersection(resume_keywords)

    # Calculate a basic match score
    if len(job_keywords) > 0:
        match_score = min(int(len(matching_keywords) / len(job_keywords) * 100), 100)
    else:
        match_score = 50  # Default score if no keywords found

    # Generate basic feedback
    strengths = list(matching_keywords)[:5]  # Limit to 5 strengths

    missing_keywords = list(job_keywords - resume_keywords)
    improvements = [
        f"Consider adding experience with {kw}" for kw in missing_keywords[:5]
    ]

    return {
        "match_score": match_score,
        "feedback": "This is an automated analysis based on keyword matching. For best results, run the application locally with full LLM capabilities.",
        "strengths": strengths if strengths else ["Basic qualifications match"],
        "improvements": (
            improvements
            if improvements
            else [
                "Consider tailoring your resume more specifically to the job description"
            ]
        ),
    }


def _extract_keywords(text):
    """Extract important keywords from text."""
    # Remove common words and keep only significant terms
    common_words = {
        "and",
        "or",
        "the",
        "a",
        "an",
        "in",
        "on",
        "at",
        "to",
        "for",
        "with",
        "by",
        "of",
        "about",
    }
    words = text.split()
    return [word for word in words if len(word) > 3 and word not in common_words]
