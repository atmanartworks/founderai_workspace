"""
Text Extractor - Extract text from various file formats

This is part of infrastructure since it depends on external libraries.
"""
import os
import logging

# Optional imports for different file types
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None


class TextExtractor:
    """
    Extract text from various file formats.
    
    Supports: .txt, .pdf, .docx, .md, .html, .htm, .json
    """
    
    @staticmethod
    def extract_text_from_file(path: str) -> str:
        """
        Extract text from file.
        
        Args:
            path: Path to file
        
        Returns:
            Extracted text
        
        Raises:
            ValueError: If file type not supported
        """
        ext = os.path.splitext(path)[1].lower()
        
        try:
            if ext in [".txt", ".md", ".json"]:
                return TextExtractor._extract_text_file(path)
            
            elif ext in [".html", ".htm"]:
                return TextExtractor._extract_html_file(path)
            
            elif ext == ".pdf":
                return TextExtractor._extract_pdf_file(path)
            
            elif ext == ".docx":
                return TextExtractor._extract_docx_file(path)
            
            else:
                # Try as text file fallback
                logging.warning(f"Unknown file type {ext}, trying as text file")
                return TextExtractor._extract_text_file(path)
                
        except Exception as e:
            logging.error(f"Text extraction error for {path}: {e}")
            return ""
    
    @staticmethod
    def _extract_text_file(path: str) -> str:
        """Extract from text files"""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    @staticmethod
    def _extract_html_file(path: str) -> str:
        """Extract from HTML files (basic - just read content)"""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    @staticmethod
    def _extract_pdf_file(path: str) -> str:
        """Extract from PDF files"""
        # Try pdfplumber first (better quality)
        if pdfplumber:
            try:
                with pdfplumber.open(path) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                        except Exception:
                            pass
                    return "\n".join(text_parts)
            except Exception as e:
                logging.warning(f"pdfplumber failed, trying PyPDF2: {e}")
        
        # Fallback to PyPDF2
        if PyPDF2:
            try:
                text_parts = []
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                return "\n".join(text_parts)
            except Exception as e:
                logging.error(f"PyPDF2 extraction failed: {e}")
                return ""
        
        raise ValueError("No PDF extraction library available. Install pdfplumber or PyPDF2")
    
    @staticmethod
    def _extract_docx_file(path: str) -> str:
        """Extract from DOCX files - includes paragraphs, tables, headers, and footers"""
        if not docx:
            raise ValueError("python-docx not installed. Run: pip install python-docx")
        
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

