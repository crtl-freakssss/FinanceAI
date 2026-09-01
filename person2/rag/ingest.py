import os
from filings.filing_parser import parse_filing
from .chunker import chunk_text
from .vector_store import add_to_store, reset_collection, count_documents
from .embeddings import get_embedding

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "documents")

SYMBOL_MAP = {
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS",
    "hdfcbank": "HDFCBANK.NS",
    "itc": "ITC.NS"
}

def ingest_documents(rebuild: bool = False) -> dict:
    """
    Scans the documents directory, parses TXT/PDF files, splits into chunks,
    generates embeddings, and stores vectors into ChromaDB.
    
    Metadata attached to every chunk:
    - company
    - symbol
    - document
    - document_type
    - source
    - page
    - section
    - chunk_id
    """
    if rebuild:
        print("[Ingestion] Rebuilding vector store collection from scratch...")
        reset_collection()

    if not os.path.exists(DOCS_DIR):
        return {"status": "error", "message": f"Documents directory '{DOCS_DIR}' not found.", "chunks_ingested": 0}

    all_chunks = []
    processed_files = 0

    for company_folder in os.listdir(DOCS_DIR):
        folder_path = os.path.join(DOCS_DIR, company_folder)
        if not os.path.isdir(folder_path):
            continue

        company_name = company_folder.upper()
        symbol = SYMBOL_MAP.get(company_folder.lower(), f"{company_folder.upper()}.NS")

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue

            # Determine document type
            doc_type = "Quarterly Results" if "q" in filename.lower() else (
                "Annual Report" if "annual" in filename.lower() else "Financial Filing"
            )
            
            parsed_pages = parse_filing(file_path)
            processed_files += 1

            for page_data in parsed_pages:
                page_text = page_data.get("text", "")
                page_num = page_data.get("page")
                section_title = page_data.get("section", "General")

                chunks = chunk_text(page_text, chunk_size=500, overlap=100)
                for idx, chunk_str in enumerate(chunks):
                    clean_chunk = chunk_str.strip()
                    if not clean_chunk:
                        continue

                    chunk_id = f"{symbol}_{filename}_{page_num or 'all'}_{idx}"
                    metadata = {
                        "company": company_name,
                        "symbol": symbol,
                        "document": filename,
                        "document_type": doc_type,
                        "source": f"{company_name} {filename.replace('_', ' ').replace('.txt', '').title()}",
                        "page": page_num if page_num is not None else -1,
                        "section": str(section_title),
                        "chunk_id": chunk_id
                    }

                    all_chunks.append({
                        "id": chunk_id,
                        "text": clean_chunk,
                        "metadata": metadata
                    })

    if not all_chunks:
        return {"status": "warning", "message": "No document chunks were generated.", "chunks_ingested": 0}

    print(f"[Ingestion] Generating embeddings for {len(all_chunks)} chunks across {processed_files} documents...")
    for chunk in all_chunks:
        emb = get_embedding(chunk["text"])
        chunk["embedding"] = emb

    add_to_store(all_chunks)
    total_in_db = count_documents()
    print(f"[Ingestion] Successfully stored {len(all_chunks)} chunks. Total vectors in DB: {total_in_db}")

    return {
        "status": "success",
        "files_processed": processed_files,
        "chunks_ingested": len(all_chunks),
        "total_documents_in_db": total_in_db
    }
