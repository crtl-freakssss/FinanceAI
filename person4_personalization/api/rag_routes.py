"""
RAG & Document Intelligence API routes bridging Person 2 services into the unified FastAPI application.
Exposes endpoints for semantic vector search, corporate filing retrieval, and citations.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from data_bridge import (
    normalize_symbol_pair,
    p2_retrieve,
    p2_format_citation,
    SymbolNotFoundError,
)

rag_router = APIRouter(tags=["RAG & Document Intelligence"])


class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language financial query", min_length=2)
    symbol: Optional[str] = Field(None, description="Optional stock ticker filter (e.g. RELIANCE.NS)")
    top_k: int = Field(5, ge=1, le=20, description="Maximum number of citations to return")


class RAGPassage(BaseModel):
    text: str
    source: str
    document: str
    page: Optional[int] = None
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGQueryResponse(BaseModel):
    query: str
    symbol_filter: Optional[str] = None
    count: int = 0
    results: List[RAGPassage] = Field(default_factory=list)
    message: str = "ok"


@rag_router.post("/rag/query", response_model=RAGQueryResponse, summary="Query Financial Filings via RAG")
def query_rag_post(request: RAGQueryRequest):
    """
    Performs semantic similarity search across corporate filings and financial reports.
    """
    if not p2_retrieve:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG retrieval service is currently unavailable.",
        )

    norm_symbol = None
    if request.symbol:
        try:
            _, norm_symbol = normalize_symbol_pair(request.symbol)
        except SymbolNotFoundError:
            norm_symbol = request.symbol

    try:
        raw_result = p2_retrieve(
            query=request.query,
            symbol=norm_symbol,
            top_k=request.top_k,
        )

        passages = []
        for r in raw_result.get("results", []):
            passages.append(
                RAGPassage(
                    text=r.get("text", ""),
                    source=r.get("source", ""),
                    document=r.get("document", ""),
                    page=r.get("page"),
                    score=float(r.get("score", 0.0)),
                    metadata=r.get("metadata", {}),
                )
            )

        return RAGQueryResponse(
            query=raw_result.get("query", request.query),
            symbol_filter=raw_result.get("symbol_filter", norm_symbol),
            count=len(passages),
            results=passages,
            message=raw_result.get("message", "ok"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing RAG search: {str(exc)}",
        )


@rag_router.get("/rag/query", response_model=RAGQueryResponse, summary="Query Financial Filings (GET)")
def query_rag_get(
    query: str = Query(..., min_length=2, description="Natural language financial query"),
    symbol: Optional[str] = Query(None, description="Optional stock ticker filter"),
    top_k: int = Query(5, ge=1, le=20, description="Max results"),
):
    """
    GET version for quick URL-based financial RAG queries.
    """
    req = RAGQueryRequest(query=query, symbol=symbol, top_k=top_k)
    return query_rag_post(req)
