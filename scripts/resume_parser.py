import fitz


def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


if __name__ == "__main__":
    with open("../uploads/Ujjwal Tyagi Resume.pdf", "rb") as pdf_file:
        resume_text = extract_text_from_pdf(pdf_file)
    print(resume_text)
