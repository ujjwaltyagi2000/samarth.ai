# scripts/matcher.py

from sentence_transformers import SentenceTransformer, util
from scripts.constants import (
    GENERAL_SKILLS,
    EDUCATION_KEYWORDS,
    JOB_ROLES,
    TOOL_SYNONYMS,
)

import re

model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_keywords(text, keywords):
    text = text.lower()
    found = [kw for kw in keywords if kw in text]
    return set(found)


def normalize_tools(tools):
    normalized = set(tools)
    for base, synonyms in TOOL_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in normalized:
                normalized.discard(synonym)
                normalized.add(base)
    return normalized


def extract_years_of_experience(text):
    """Extracts the number of years of experience from the text using regex."""
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years|yrs)", text.lower())
    if matches:
        years = [
            float(match) for match in matches if float(match) < 40
        ]  # avoid false positives
        return max(years) if years else 0
    return 0


def calculate_match_score(processed_resume: str, processed_job_desc: str) -> dict:
    # SBERT semantic similarity
    resume_embedding = model.encode(processed_resume, convert_to_tensor=True)
    jd_embedding = model.encode(processed_job_desc, convert_to_tensor=True)
    semantic_score = util.cos_sim(resume_embedding, jd_embedding).item()

    # Keyword-based scoring
    # Loop through all categories of skills
    resume_skills = set()
    jd_skills = set()

    for category in GENERAL_SKILLS:
        resume_skills.update(
            extract_keywords(processed_resume, GENERAL_SKILLS[category])
        )
        jd_skills.update(extract_keywords(processed_job_desc, GENERAL_SKILLS[category]))

    resume_edu = extract_keywords(processed_resume, EDUCATION_KEYWORDS)
    jd_edu = extract_keywords(processed_job_desc, EDUCATION_KEYWORDS)

    resume_roles = extract_keywords(processed_resume, JOB_ROLES)
    jd_roles = extract_keywords(processed_job_desc, JOB_ROLES)

    normalized_resume_skills = normalize_tools(resume_skills)
    normalized_jd_skills = normalize_tools(jd_skills)

    skill_match_ratio = len(normalized_resume_skills & normalized_jd_skills) / max(
        len(normalized_jd_skills), 1
    )
    edu_match_ratio = len(resume_edu & jd_edu) / max(len(jd_edu), 1)
    role_match = 1 if resume_roles & jd_roles else 0

    # Experience matching
    resume_exp = extract_years_of_experience(processed_resume)
    jd_exp = extract_years_of_experience(processed_job_desc)
    if jd_exp > 0:
        exp_match_ratio = min(resume_exp / jd_exp, 1.0)  # Cap at 100%
    else:
        exp_match_ratio = 1.0  # No specific experience asked

    # Weighted scoring
    skill_weight = 0.5
    edu_weight = 0.2
    role_weight = 0.1
    exp_weight = 0.2

    keyword_score = (
        skill_weight * skill_match_ratio
        + edu_weight * edu_match_ratio
        + role_weight * role_match
        + exp_weight * exp_match_ratio
    )

    final_score = round((0.6 * semantic_score + 0.4 * keyword_score) * 100, 2)

    return {
        "final_score": final_score,
        "semantic_score": round(semantic_score * 100, 2),
        "keyword_score": round(keyword_score * 100, 2),
        "skill_match_ratio": round(skill_match_ratio * 100, 2),
        "edu_match_ratio": round(edu_match_ratio * 100, 2),
        "role_match": role_match,
        "exp_match_ratio": round(exp_match_ratio * 100, 2),
        "resume_exp": resume_exp,
        "jd_exp": jd_exp,
    }
