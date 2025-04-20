import constants
import re


def extract_contact_number_from_resume(text):
    contact_number = None

    # Use regex pattern to find a potential contact number
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()

    return contact_number


def extract_email_from_resume(text):
    email = None

    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()

    return email


def extract_skills_from_resume(text, skills_list):
    skills = []

    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)

    return skills


def extract_education_from_resume(text):

    education = []
    education_keywords = constants.EDUCATION_KEYWORDS

    for keyword in education_keywords:
        pattern = r"(?i)\b{}\b".format(re.escape(keyword))
        match = re.search(pattern, text)
        if match:
            education.append(match.group())

    return education


if __name__ == "__main__":
    with open("../sample-resume.txt", "r") as file:
        resume_text = file.read()

    print("Contact Number:", extract_contact_number_from_resume(resume_text))
    print("Email:", extract_email_from_resume(resume_text))

    extracted_skills = extract_skills_from_resume(resume_text, constants.COMMON_SKILLS)

    if extracted_skills:
        print("Skills:", extracted_skills)
    else:
        print("No skills found")

    print("Education:", extract_education_from_resume(resume_text))
