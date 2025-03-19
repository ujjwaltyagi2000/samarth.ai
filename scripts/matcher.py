from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(resume_text, job_description):
    """Computes similarity score using TF-IDF & Cosine Similarity."""
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_description])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]

    return round(score * 100, 2)  # Convert to percentage
