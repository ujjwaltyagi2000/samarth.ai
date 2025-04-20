from sentence_transformers import SentenceTransformer, util

# Load a pre-trained SBERT model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_match_score(processed_resume: str, processed_job_desc: str) -> float:
    """
    Calculate the match score between a resume and a job description using SBERT.

    Args:
        processed_resume (str): Cleaned and preprocessed resume text.
        processed_job_desc (str): Cleaned and preprocessed job description text.

    Returns:
        float: Match score between 0 and 100 (percentage similarity).
    """
    # Encode both documents into embeddings
    resume_embedding = model.encode(processed_resume, convert_to_tensor=True)
    jd_embedding = model.encode(processed_job_desc, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_score = util.cos_sim(resume_embedding, jd_embedding).item()

    # Convert to percentage for better readability
    match_score = round(similarity_score * 100, 2)

    return match_score
