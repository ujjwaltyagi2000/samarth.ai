import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text
