import pytest
from rag.retriever import retrieve
from rag.citations import format_citation, format_all_citations

def test_retrieval_reliance_query():
    result = retrieve("What was Reliance EBITDA growth?", symbol="RELIANCE.NS", top_k=3)
    assert result is not None
    assert "query" in result
    assert "results" in result
    if len(result["results"]) > 0:
        top_match = result["results"][0]
        assert "text" in top_match
        assert "source" in top_match
        assert "score" in top_match
        assert top_match["score"] >= 0.0

def test_retrieval_empty_query():
    result = retrieve("")
    assert result["results"] == []
    assert "Query cannot be empty" in result["message"]

def test_retrieval_company_filter():
    res_tcs = retrieve("revenue and operating margin", symbol="TCS.NS", top_k=3)
    for r in res_tcs.get("results", []):
        assert "TCS" in r.get("metadata", {}).get("company", "") or "TCS" in r.get("source", "")

def test_citation_formatting():
    mock_result = {
        "text": "Reliance delivered robust EBITDA of INR 44,678 crore.",
        "source": "Reliance Q3 Financial Results",
        "document": "reliance/q3_fy25_financial_results.txt",
        "page": 1,
        "score": 0.94
    }
    citation = format_citation(mock_result)
    assert "SOURCE:\nReliance Q3 Financial Results" in citation
    assert "PAGE:\n1" in citation
    assert "RELEVANCE:\n0.94" in citation
    assert "Reliance delivered robust EBITDA" in citation

def test_citation_formatting_missing_page():
    mock_result = {
        "text": "General overview text without page number.",
        "source": "Company Overview",
        "document": "overview.txt",
        "page": None,
        "score": 0.85
    }
    citation = format_citation(mock_result)
    assert "PAGE:\nN/A" in citation
    assert "RELEVANCE:\n0.85" in citation

def test_format_all_citations_empty():
    assert format_all_citations([]) == "No reliable evidence was found for this query."
