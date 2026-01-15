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
            except ImportError:
                logging.error("python-docx not installed. Install with: pip install python-docx")
                return ""
            
            try:
                doc = docx.Document(path)
                text_parts = []
                
                # Extract paragraphs
                for para in doc.paragraphs:
                    if para.text and para.text.strip():
                        text_parts.append(para.text.strip())
                
                # Extract tables (important for DOCX files)
                for table in doc.tables:
                    table_text = []
                    for row in table.rows:
                        row_text = []
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                row_text.append(cell_text)
                        if row_text:
                            table_text.append(" | ".join(row_text))
                    if table_text:
                        text_parts.append("\n".join(table_text))
                
                # Extract headers and footers
                for section in doc.sections:
                    if section.header:
                        header_text = []
                        for para in section.header.paragraphs:
                            if para.text and para.text.strip():
                                header_text.append(para.text.strip())
                        if header_text:
                            text_parts.extend(header_text)
                    
                    if section.footer:
                        footer_text = []
                        for para in section.footer.paragraphs:
                            if para.text and para.text.strip():
                                footer_text.append(para.text.strip())
                        if footer_text:
                            text_parts.extend(footer_text)
                
                extracted_text = "\n\n".join(text_parts)
                
                if not extracted_text or len(extracted_text.strip()) < 10:
                    logging.warning(f"DOCX file {path} extracted very little text ({len(extracted_text)} chars)")
                    return ""
                
                logging.info(f"Successfully extracted {len(extracted_text)} characters from DOCX file {path}")
                return extracted_text
                
            except Exception as e:
                logging.error(f"DOCX extraction failed for {path}: {e}", exc_info=True)
                return ""
        # fallback
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""
