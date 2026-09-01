import pytest
from rag.chunker import chunk_text
from rag.embeddings import get_embedding, get_current_backend
from filings.filing_parser import parse_filing

def test_chunker_basic():
    text = "Short sentence 1. Short sentence 2.\n\nParagraph 2 with more financial data."
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) >= 1
    for c in chunks:
        assert len(c) > 0

def test_chunker_large_text():
    long_text = "Reliance reported gross revenue of INR 248,160 crore. " * 50
    chunks = chunk_text(long_text, chunk_size=500, overlap=100)
    assert len(chunks) > 1

def test_chunker_empty():
    assert chunk_text("") == []
    assert chunk_text(None) == []

def test_embeddings_generation():
    emb = get_embedding("Reliance consolidated EBITDA growth")
    assert emb is not None
    assert len(emb) == 384 or len(emb) == 1536
    assert isinstance(emb[0], float)

def test_filing_parser_txt(tmp_path):
    txt_file = tmp_path / "sample_filing.txt"
    txt_file.write_text("Page 1: Overview\nRevenue was 100 Cr.\nPage 2: Balance Sheet\nDebt was 20 Cr.")
    
    parsed = parse_filing(str(txt_file))
    assert len(parsed) == 2
    assert parsed[0]["page"] == 1
    assert "Revenue" in parsed[0]["text"]
    assert parsed[1]["page"] == 2
    assert "Debt" in parsed[1]["text"]

def test_filing_parser_nonexistent():
    assert parse_filing("nonexistent_path_123.txt") == []
