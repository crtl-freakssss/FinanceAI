def format_citation(result: dict) -> str:
    """
    Formats a single retrieved evidence item into a standardized citation format.
    
    Format:
    SOURCE:
    Reliance Quarterly Results

    PAGE:
    4

    EXCERPT:
    "Revenue increased..."

    RELEVANCE:
    0.91
    """
    if not result or not isinstance(result, dict):
        return "SOURCE:\nUnknown\n\nPAGE:\nN/A\n\nEXCERPT:\n\"\"\n\nRELEVANCE:\n0.00"

    source = result.get("source") or result.get("document") or "Financial Document"
    page = result.get("page")
    page_str = str(page) if (page is not None and page != -1 and str(page) != "-1") else "N/A"
    
    raw_text = result.get("text", "").strip()
    # Clean excerpt formatting
    excerpt = " ".join(raw_text.split())
    if len(excerpt) > 300:
        excerpt = excerpt[:297] + "..."

    score = result.get("score", 0.0)
    score_str = f"{float(score):.2f}"

    return (
        f"SOURCE:\n{source}\n\n"
        f"PAGE:\n{page_str}\n\n"
        f"EXCERPT:\n\"{excerpt}\"\n\n"
        f"RELEVANCE:\n{score_str}"
    )

def format_all_citations(results: list) -> str:
    """
    Formats a list of retrieved evidence passages into a clean numbered citation block.
    """
    if not results:
        return "No reliable evidence was found for this query."

    blocks = []
    for idx, item in enumerate(results, 1):
        blocks.append(f"[{idx}]\n{format_citation(item)}")
    
    return "\n\n" + ("=" * 50) + "\n\n".join([""] + blocks) + "\n" + ("=" * 50)
