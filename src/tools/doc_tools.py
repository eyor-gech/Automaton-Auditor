from typing import List, Dict
import os
import pypdf

def ingest_pdf_semantically(pdf_path: str) -> Dict:
    """
    RAG-lite ingestion:
    - Page extraction
    - Paragraph chunking
    - Sliding window merge
    """

    if not os.path.exists(pdf_path):
        return {"error": "File not found"}

    try:
        reader = pypdf.PdfReader(pdf_path)
        chunks = []

        chunk_id = 0

        for page_index, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]

            # Sliding window chunking (semantic grouping)
            for i in range(len(paragraphs)):
                window = " ".join(paragraphs[i:i+2])
                if len(window) < 50:
                    continue

                chunks.append({
                    "id": f"{page_index}-{chunk_id}",
                    "content": window,
                    "page": page_index,
                    "confidence": 0.95
                })
                chunk_id += 1

        return {"chunks": chunks, "metadata": {"total_chunks": len(chunks)}}

    except Exception as e:
        return {"error": f"Ingestion failed: {str(e)}"}


def query_pdf_chunks(chunks: List[Dict], query: str) -> List[Dict]:
    q = query.lower()
    scored = []

    for c in chunks:
        content = c["content"].lower()
        score = content.count(q)
        if score > 0:
            scored.append((score, c))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored]