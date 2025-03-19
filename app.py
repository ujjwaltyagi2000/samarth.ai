import streamlit as st
import pandas as pd
import os
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Create a function to download NLTK data with caching
@st.cache_resource
def download_nltk_data():
    # Download required NLTK resources
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Call the download function at the start
download_nltk_data()

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Create upload directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

def parse_pdf(file_path):
    """
    Extract text from a PDF file
    """
    text = ""
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return None

def preprocess_text(text):
    """
    Preprocess the extracted text by:
    - Converting to lowercase
    - Removing special characters
    - Tokenizing
    - Removing stopwords
    - Lemmatizing
    """
    if not text:
        return []
    
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatize
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return lemmatized_tokens

def extract_skills(tokens):
    """
    Extract skills from preprocessed tokens
    This is a simple implementation that can be enhanced later
    """
    # Common tech skills - this list should be expanded
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular',
        'node', 'django', 'flask', 'mongodb', 'mysql', 'postgresql', 'aws', 'azure',
        'docker', 'kubernetes', 'git', 'machine learning', 'data science', 'ai',
        'nlp', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit', 'selenium',
        'automation', 'testing', 'ci/cd', 'agile', 'scrum', 'project management'
    ]
    
    # Extract skills from tokens
    skills = [token for token in tokens if token in common_skills]
    
    # Remove duplicates and sort
    unique_skills = sorted(list(set(skills)))
    
    return unique_skills

# Main app
st.title("Samarth - Resume Matcher")

# Upload the file
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    # Save the file to a temporary location
    save_path = os.path.join("uploads", uploaded_file.name)
    
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"File saved at {save_path}")
    
    # Parse the PDF
    with st.spinner("Parsing resume..."):
        resume_text = parse_pdf(save_path)
        
        if resume_text:
            st.subheader("Extracted Text")
            with st.expander("Show extracted text"):
                st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
            
            # Preprocess the text
            with st.spinner("Processing text..."):
                preprocessed_tokens = preprocess_text(resume_text)
                
                # Extract skills
                skills = extract_skills(preprocessed_tokens)
                
                st.subheader("Extracted Skills")
                if skills:
                    st.write(", ".join(skills))
                else:
                    st.write("No common skills detected. Consider enhancing the skill extraction algorithm.")

# Job Description Input
st.subheader("Job Description")
jd_option = st.radio(
    "How would you like to provide the job description?",
    ("Text Input", "URL (LinkedIn/Naukri/Foundit)")
)

if jd_option == "Text Input":
    job_description = st.text_area("Paste the job description here")
    if job_description:
        st.info("Job description received. Feature to analyze and compare with resume will be implemented next.")
else:
    jd_url = st.text_input("Enter the job posting URL")
    if jd_url:
        st.info("URL received. Web scraping functionality will be implemented next.")

# Placeholder for matching functionality
if uploaded_file is not None and ((jd_option == "Text Input" and job_description) or (jd_option == "URL (LinkedIn/Naukri/Foundit)" and jd_url)):
    st.subheader("Resume-Job Matching")
    st.info("Matching functionality will be implemented next.")