import os
import json

DOCUMENTS_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "documents")
MOCK_FILINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "mock_data", "filings.json")

SYMBOL_TO_FOLDER = {
    "RELIANCE.NS": "reliance",
    "RELIANCE": "reliance",
    "TCS.NS": "tcs",
    "TCS": "tcs",
    "INFY.NS": "infosys",
    "INFY": "infosys",
    "INFOSYS": "infosys",
    "HDFCBANK.NS": "hdfcbank",
    "HDFCBANK": "hdfcbank",
    "ITC.NS": "itc",
    "ITC": "itc"
}

def get_filings(symbol: str) -> dict:
    """
    Returns available local financial documents and filings for a given symbol.
    Uses local documents repository to ensure 100% offline reliability.
    """
    sym = symbol.strip().upper()
    normalized = sym if "." in sym else f"{sym}.NS"
    folder_name = SYMBOL_TO_FOLDER.get(normalized, SYMBOL_TO_FOLDER.get(sym, sym.lower().replace(".ns", "")))
    
    target_dir = os.path.join(DOCUMENTS_BASE_DIR, folder_name)
    found_docs = []
    
    if os.path.exists(target_dir):
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)
            if os.path.isfile(file_path):
                found_docs.append({
                    "title": filename.replace("_", " ").replace(".txt", "").replace(".pdf", "").title(),
                    "filename": filename,
                    "path": os.path.relpath(file_path, os.path.join(os.path.dirname(__file__), "..")),
                    "size_bytes": os.path.getsize(file_path)
                })

    # If no folder exists, check mock_data/filings.json
    if not found_docs and os.path.exists(MOCK_FILINGS_PATH):
        try:
            with open(MOCK_FILINGS_PATH, 'r', encoding='utf-8') as f:
                mock_data = json.load(f)
            if normalized in mock_data:
                found_docs = mock_data[normalized]
        except Exception:
            pass

    return {
        "symbol": normalized,
        "count": len(found_docs),
        "documents": found_docs,
        "source": "local_corpus"
    }
