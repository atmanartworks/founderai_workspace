# app/services/text_extraction.py
import os
from typing import Optional

def extract_text_from_file(path: str) -> str:
    """
    Basic extraction:
     - .txt -> read
     - .pdf -> PyPDF2
     - .docx -> python-docx
     - .html/.htm -> read and strip tags minimally
    """
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        if ext in [".html", ".htm"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        if ext == ".pdf":
            # Try pdfplumber first (better extraction)
            try:
                import pdfplumber
                text = []
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        try:
                            txt = page.extract_text()
                            if txt and txt.strip():
                                text.append(txt.strip())
                        except:
                            continue
                if text:
                    return "\n\n".join(text)
            except Exception:
                pass
            
            # Fallback to PyPDF2 if pdfplumber fails
            try:
                import PyPDF2
                text = []
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for p in reader.pages:
                        try:
                            txt = p.extract_text()
                            if txt and txt.strip():
                                text.append(txt.strip())
                        except:
                            continue
                if text:
                    return "\n\n".join(text)
            except Exception:
                pass
            
            return ""
        if ext == ".docx":
            try:
                import docx
            except Exception:
                return ""
            doc = docx.Document(path)
            paras = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(paras)
        # fallback
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""
