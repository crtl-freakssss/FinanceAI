import os
import numpy as np

try:
    import chromadb
except ImportError:
    chromadb = None

DB_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
COLLECTION_NAME = "finai_financial_docs"

_client = None

# In-memory store fallback when chromadb is not installed
_memory_store = []


class _InMemoryCollection:
    """Lightweight in-memory vector store matching ChromaDB collection interface."""

    def __init__(self):
        self.name = COLLECTION_NAME

    def count(self) -> int:
        return len(_memory_store)

    def upsert(self, ids: list, documents: list, metadatas: list, embeddings: list):
        global _memory_store
        for i in range(len(ids)):
            # Update or append
            entry = {
                "id": str(ids[i]),
                "document": str(documents[i]),
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "embedding": np.array(embeddings[i], dtype=np.float32)
            }
            # Remove old if exists
            _memory_store = [e for e in _memory_store if e["id"] != entry["id"]]
            _memory_store.append(entry)

    def query(self, query_embeddings: list, n_results: int = 5, where: dict = None) -> dict:
        if not _memory_store or not query_embeddings:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        q_vec = np.array(query_embeddings[0], dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        candidates = _memory_store
        if where and "symbol" in where:
            sym_filter = str(where["symbol"]).strip().upper()
            candidates = [c for c in candidates if str(c.get("metadata", {}).get("symbol", "")).upper() == sym_filter]

        if not candidates:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        scored = []
        for c in candidates:
            c_vec = c["embedding"]
            c_norm = np.linalg.norm(c_vec)
            if c_norm > 0:
                c_vec = c_vec / c_norm
            cos_sim = float(np.dot(q_vec, c_vec))
            # Cosine distance = 1 - cos_sim
            dist = max(0.0, 1.0 - cos_sim)
            scored.append((dist, c))

        scored.sort(key=lambda x: x[0])
        top = scored[:n_results]

        return {
            "ids": [[item[1]["id"] for item in top]],
            "documents": [[item[1]["document"] for item in top]],
            "metadatas": [[item[1]["metadata"] for item in top]],
            "distances": [[item[0] for item in top]]
        }


def get_client():
    global _client
    if chromadb is not None:
        if _client is None:
            try:
                os.makedirs(DB_DIR, exist_ok=True)
                _client = chromadb.PersistentClient(path=DB_DIR)
            except Exception:
                _client = None
    return _client


def get_collection():
    client = get_client()
    if client is not None:
        try:
            return client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            pass
    return _InMemoryCollection()


def reset_collection():
    """Deletes and recreates the ChromaDB collection or resets in-memory collection."""
    global _memory_store
    client = get_client()
    if client is not None:
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
    _memory_store = []
    return get_collection()


def add_to_store(chunks_data: list):
    """
    Upserts chunk records into ChromaDB or in-memory fallback.
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
    Performs similarity search in ChromaDB or in-memory fallback.
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
