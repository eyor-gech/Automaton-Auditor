from typing import List, Dict
import os


# -----------------------------
# CHUNKING
# -----------------------------

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# -----------------------------
# PDF INGESTION (CHUNKED)
# -----------------------------

def ingest_pdf_content(pdf_path: str) -> Dict:
    if not pdf_path.endswith(".pdf"):
        return {"error": "File is not a PDF."}

    if not os.path.exists(pdf_path):
        return {"error": "File does not exist."}

    try:
        # ✅ Lazy import (THIS is the fix)
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        markdown = result.document.export_to_markdown()

        chunks = chunk_text(markdown)

        return {
            "full_markdown": markdown[:2000],  # safe preview only
            "num_chunks": len(chunks),
            "chunks": [
                {"id": i, "content": chunk}
                for i, chunk in enumerate(chunks)
            ]
        }

    except Exception as e:
        return {"error": f"Error parsing PDF: {str(e)}"}


# -----------------------------
# QUERY INTERFACE
# -----------------------------

def query_pdf_chunks(chunks: List[Dict], query: str):
    query_lower = query.lower()
    matches = []

    for chunk in chunks:
        if query_lower in chunk["content"].lower():
            matches.append(chunk)

    return matches

# -----------------------------
# KEYWORD HEURISTIC ANALYSIS
# -----------------------------

def search_for_keywords(text: str, keywords: List[str]) -> Dict:
    findings = {}
    text_lower = text.lower()

    for kw in keywords:
        count = text_lower.count(kw.lower())
        findings[kw] = {
            "count": count,
            "is_substantive": count > 0
        }

    return findings