import pypdf

def extract_text_from_pdf(uploaded_file):
    """Extract all text from an uploaded PDF file"""
    
    pdf_reader = pypdf.PdfReader(uploaded_file)
    
    full_text = ""
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            full_text += f"\n--- Page {page_num + 1} ---\n{text}"
    
    return full_text


def build_system_prompt(clinic_data, pdf_text=None):
    """Build the system prompt combining clinic data + PDF content"""
    
    base_prompt = clinic_data
    
    if pdf_text:
        base_prompt += f"""

=== ADDITIONAL INFORMATION FROM UPLOADED DOCUMENT ===
{pdf_text}

IMPORTANT: Use the above document information to answer patient queries accurately.
If information exists in both the document and base clinic info, prefer the document.
"""
    
    return base_prompt