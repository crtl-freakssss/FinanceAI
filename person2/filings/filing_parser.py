import os
import re

def parse_filing(file_path: str) -> list:
    """
    Parses financial documents (TXT, PDF) into structured page/section records.
    
    Returns list of dicts:
    [
        {
            "text": "clean text content...",
            "page": 1 (or None if unavailable),
            "section": "Corporate Overview & Financial Highlights"
        }
    ]
    
    Never fabricates page numbers.
    """
    if not os.path.exists(file_path):
        return []
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return _parse_txt_file(file_path)
    elif ext == '.pdf':
        return _parse_pdf_file(file_path)
    else:
        # Default text fallback
        return _parse_txt_file(file_path)

def _parse_txt_file(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Check if text file contains structured "Page X:" markers
    page_splits = re.split(r'\n(?=Page\s+\d+:)', content)
    
    if len(page_splits) > 1:
        results = []
        for segment in page_splits:
            match = re.match(r'Page\s+(\d+):\s*(.*)', segment.strip())
            if match:
                page_num = int(match.group(1))
                section_title = match.group(2).split('\n')[0].strip()
                text_body = segment.strip()
                results.append({
                    "text": text_body,
                    "page": page_num,
                    "section": section_title or f"Page {page_num}"
                })
            else:
                results.append({
                    "text": segment.strip(),
                    "page": None,
                    "section": "General"
                })
        return results

    # If no explicit page markers exist, return as single document with page=None
    return [{
        "text": content.strip(),
        "page": None,
        "section": os.path.basename(file_path)
    }]

def _parse_pdf_file(file_path: str) -> list:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[WARNING] PyMuPDF (fitz) is not available. Falling back to plain text reading.")
        return _parse_txt_file(file_path)

    try:
        doc = fitz.open(file_path)
        pages = []
        for idx in range(len(doc)):
            page_obj = doc.load_page(idx)
            text = page_obj.get_text("text").strip()
            if text:
                pages.append({
                    "text": text,
                    "page": idx + 1,
                    "section": f"Page {idx + 1}"
                })
        return pages
    except Exception as e:
        print(f"[ERROR] Failed to parse PDF {file_path}: {e}")
        return []
