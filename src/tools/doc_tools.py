from typing import List, Dict
import os

def ingest_pdf_semantically(pdf_path: str) -> Dict:
    """
    Converts PDF to structured, queryable evidence chunks.
    Labels include architecture claims, headings, and generic text.
    """
    if not os.path.exists(pdf_path):
        return {"error": "File not found"}
    
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        chunks = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text: continue
            
            # extract basic paragraphs
            lines = text.split('\n')
            for j, line in enumerate(lines):
                p = line.strip()
                if len(p) < 10: continue
                
                label = "[TEXT]"
                if any(k in p.lower() for k in ["parallel", "fan-out", "fan-in", "state", "graph", "node", "edge"]):
                    label = "[ARCH_CLAIM]"
                
                chunks.append({
                    "id": f"{i}-{j}",
                    "label": label,
                    "content": p,
                    "confidence": 1.0  # fixed confidence for Master Thinker
                })
        return {"chunks": chunks, "metadata": {"total_elements": len(chunks)}}
    
    except Exception as e:
        return {"error": f"Semantic ingestion failed: {str(e)}"}

def query_pdf_chunks(chunks: List[Dict], query: str) -> List[Dict]:
    """Search chunks for query, preserving evidence structure."""
    q = query.lower()
    results = []
    for c in chunks:
        if q in c["content"].lower():
            results.append(c)
    return results