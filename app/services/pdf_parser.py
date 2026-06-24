import pdfplumber
import io

def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Parses a PDF file from bytes and extracts all text.
    """
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")
        
    return text.strip()
