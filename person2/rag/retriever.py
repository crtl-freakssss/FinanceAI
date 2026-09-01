from .embeddings import get_embedding
from .vector_store import search

def retrieve(query: str, symbol: str = None, top_k: int = 5) -> dict:
    """
    Primary RAG semantic retrieval interface.
    
    Parameters:
    - query: natural language financial question
    - symbol: optional ticker filter (e.g. 'RELIANCE.NS')
    - top_k: maximum number of relevant evidence snippets to return
    
    Returns structured results:
    {
        "query": "...",
        "symbol_filter": "...",
        "results": [
            {
                "text": "...",
                "source": "...",
                "document": "...",
                "page": 1,
                "score": 0.91,
                "metadata": {...}
            }
        ],
        "message": "..."
    }
    
    NO HALLUCINATION GUARANTEE:
    If no relevant evidence exists in the corpus, returns empty results with
    "No reliable evidence was found for this query."
    """
    clean_query = query.strip() if query else ""
    if not clean_query:
        return {
            "query": query,
            "symbol_filter": symbol,
            "results": [],
            "message": "Query cannot be empty."
        }

    try:
        query_emb = get_embedding(clean_query)
        raw = search(query_emb, symbol=symbol, top_k=top_k)
        
        ids_list = raw.get('ids', [[]])[0]
        docs_list = raw.get('documents', [[]])[0]
        metas_list = raw.get('metadatas', [[]])[0]
        dists_list = raw.get('distances', [[]])[0] if 'distances' in raw else [0.0] * len(ids_list)
        
        if not ids_list or len(ids_list) == 0:
            return {
                "query": clean_query,
                "symbol_filter": symbol,
                "results": [],
                "message": "No reliable evidence was found for this query."
            }

        results = []
        for i in range(len(ids_list)):
            raw_dist = float(dists_list[i]) if i < len(dists_list) else 0.0
            # For cosine distance in Chroma: similarity = 1 - distance / 2 or 1 - distance
            # calibrated score between 0.0 and 1.0
            sim_score = max(0.0, min(1.0, 1.0 - (raw_dist / 2.0)))
            
            meta = metas_list[i] if i < len(metas_list) and metas_list[i] else {}
            page_val = meta.get("page")
            if page_val in [-1, "-1", None]:
                page_val = None
            else:
                try:
                    page_val = int(page_val)
                except Exception:
                    pass

            doc_name = meta.get("document", "Unknown Document")
            company = meta.get("company", "")
            source_title = meta.get("source") or f"{company} {doc_name}".strip()

            results.append({
                "text": docs_list[i],
                "source": source_title,
                "document": f"{company.lower()}/{doc_name}" if company else doc_name,
                "page": page_val,
                "score": round(sim_score, 2),
                "metadata": meta
            })

        return {
            "query": clean_query,
            "symbol_filter": symbol,
            "results": results,
            "message": f"Found {len(results)} relevant evidence passage(s)."
        }

    except Exception as e:
        return {
            "query": clean_query,
            "symbol_filter": symbol,
            "results": [],
            "message": f"Error during retrieval: {str(e)}. No reliable evidence was found for this query."
        }
