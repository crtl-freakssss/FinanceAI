import re

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> list:
    """
    Splits text into context-preserving chunks respecting sentence and paragraph boundaries.
    Avoids extremely tiny chunks (< 50 chars) and overly huge chunks.
    """
    if not text or not text.strip():
        return []

    # Clean text
    clean_text = text.strip()
    
    # Split into paragraphs first
    paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [clean_text]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            # If current chunk has enough content, save it
            if current_chunk:
                chunks.append(current_chunk)
            
            # If paragraph itself is larger than chunk_size, split by sentences
            if len(para) > chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                temp_sent_chunk = ""
                for sent in sentences:
                    if len(temp_sent_chunk) + len(sent) + 1 <= chunk_size:
                        temp_sent_chunk = f"{temp_sent_chunk} {sent}".strip()
                    else:
                        if temp_sent_chunk:
                            chunks.append(temp_sent_chunk)
                        temp_sent_chunk = sent
                if temp_sent_chunk:
                    current_chunk = temp_sent_chunk
                else:
                    current_chunk = ""
            else:
                current_chunk = para

    if current_chunk and len(current_chunk) >= 30:
        chunks.append(current_chunk)

    # Fallback to sliding window if chunking produced nothing
    if not chunks and clean_text:
        start = 0
        while start < len(clean_text):
            end = min(start + chunk_size, len(clean_text))
            chunk_slice = clean_text[start:end].strip()
            if chunk_slice:
                chunks.append(chunk_slice)
            start += max(1, chunk_size - overlap)

    return chunks
