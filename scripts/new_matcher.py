from sentence_transformers import SentenceTransformer, util
import re
import spacy

model = SentenceTransformer("all-MiniLM-L6-v2")
nlp = spacy.load("en_core_web_sm")

SECTION_WEIGHTS = {"skills": 0.4, "experience": 0.4, "education": 0.2}


def extract_section(text, section_name):
    pattern = rf"{section_name}.*?(?=\n[A-Z][^\n]*?:|\Z)"
    matches = re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return matches[0].strip() if matches else ""


def extract_skills(text):
    # very simple skill extractor based on common tech keywords
    keywords = [
        "python",
        "java",
        "c++",
        "sql",
        "tensorflow",
        "pandas",
        "numpy",
        "power bi",
        "tableau",
        "streamlit",
        "selenium",
        "opencv",
        "scikit-learn",
        "nlp",
        "llm",
        "bert",
        "supabase",
        "vscode",
        "git",
        "javascript",
    ]
    text = text.lower()
    found_skills = {kw for kw in keywords if kw in text}
    return found_skills


def calculate_section_score(resume_text, jd_text, section_name):
    resume_section = extract_section(resume_text, section_name)
    jd_section = extract_section(jd_text, section_name)

    if resume_section and jd_section:
        resume_emb = model.encode(resume_section, convert_to_tensor=True)
        jd_emb = model.encode(jd_section, convert_to_tensor=True)
        return util.cos_sim(resume_emb, jd_emb).item()
    return 0.0


def calculate_match_score(processed_resume, processed_jd):
    # Section-wise similarity score
    total_score = 0.0
    for section, weight in SECTION_WEIGHTS.items():
        section_score = calculate_section_score(processed_resume, processed_jd, section)
        total_score += weight * section_score

    # Skill overlap (Jaccard Similarity)
    resume_skills = extract_skills(processed_resume)
    jd_skills = extract_skills(processed_jd)

    if resume_skills and jd_skills:
        intersection = resume_skills.intersection(jd_skills)
        union = resume_skills.union(jd_skills)
        skill_overlap_score = len(intersection) / len(union)
    else:
        skill_overlap_score = 0.0

    # Combine both (weighted)
    final_score = 0.6 * total_score + 0.4 * skill_overlap_score
    return round(final_score * 100, 2)
