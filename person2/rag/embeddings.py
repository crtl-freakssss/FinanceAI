import os
import hashlib
import numpy as np

# Global cache for sentence transformer model to prevent re-instantiation
_st_model = None
_embedding_backend = None

def get_embedding(text: str) -> list:
    """
    Generates dense embeddings for a given text.
    
    Order of preference:
    1. OpenAI text-embedding-3-small (if OPENAI_API_KEY is configured in env)
    2. SentenceTransformer ('all-MiniLM-L6-v2') local model
    3. Deterministic Hashed Normalized Vector (384-dim) for offline demo resilience
    """
    global _st_model, _embedding_backend
    
    if not text or not text.strip():
        return [0.0] * 384

    # 1. Check OpenAI API Key
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.embeddings.create(
                input=text.replace("\n", " "),
                model="text-embedding-3-small"
            )
            _embedding_backend = "openai"
            return response.data[0].embedding
        except Exception:
            pass

    # 2. Check SentenceTransformers
    try:
        if _st_model is None:
            from sentence_transformers import SentenceTransformer
            _st_model = SentenceTransformer('all-MiniLM-L6-v2')
            _embedding_backend = "sentence-transformers"
        
        emb = _st_model.encode(text)
        return emb.tolist()
    except Exception as e:
        _embedding_backend = "deterministic_offline_hash"

    # 3. Deterministic Cosine-Compatible 384-dim Hash Fallback
    return _generate_deterministic_vector(text)

def _generate_deterministic_vector(text: str, dim: int = 384) -> list:
    """
    Generates a deterministic, normalized embedding vector using text hashing.
    Used exclusively as an unbreakable offline fallback when no external weights can be downloaded.
    """
    words = text.lower().split()
    vec = np.zeros(dim, dtype=np.float32)
    
    for i, word in enumerate(words):
        h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 4) % 2 == 0) else -1.0
        vec[idx] += sign * (1.0 / (1.0 + (i * 0.05)))
        
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    else:
        vec[0] = 1.0
        
    return vec.tolist()

def get_current_backend() -> str:
    global _embedding_backend
    return _embedding_backend or "sentence-transformers"
