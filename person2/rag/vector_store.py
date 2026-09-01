import chromadb
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
COLLECTION_NAME = "finai_financial_docs"

_client = None

def get_client():
    global _client
    if _client is None:
        os.makedirs(DB_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=DB_DIR)
    return _client

def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def reset_collection():
    """Deletes and recreates the ChromaDB collection for clean rebuilding."""
    client = get_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    return get_collection()

def add_to_store(chunks_data: list):
    """
    Upserts chunk records into ChromaDB.
    Expected chunk format:
    {
        "id": "chunk_id_str",
        "text": "text content...",
        "metadata": {"company": "...", "symbol": "...", "document": "...", "page": 1, ...},
        "embedding": [0.1, 0.2, ...]
    }
    """
    if not chunks_data:
        return
        
    collection = get_collection()
    
    ids = [str(c["id"]) for c in chunks_data]
    documents = [str(c["text"]) for c in chunks_data]
    metadatas = [c["metadata"] for c in chunks_data]
    embeddings = [c["embedding"] for c in chunks_data]
    
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

def search(query_embedding: list, symbol: str = None, top_k: int = 5) -> dict:
    """
    Performs similarity search in ChromaDB.
    Supports optional symbol filtering.
    """
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    where_filter = None
    if symbol:
        sym = symbol.strip().upper()
        normalized = sym if "." in sym else f"{sym}.NS"
        where_filter = {"symbol": normalized}
        
    effective_k = min(top_k, count)
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=effective_k,
            where=where_filter
        )
        return results
    except Exception as e:
        print(f"[VectorStore Search Error] {e}")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

def count_documents() -> int:
    try:
        return get_collection().count()
    except Exception:
        return 0
