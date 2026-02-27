from typing import List, Dict
import os

def ingest_pdf_semantically(pdf_path: str) -> Dict:
    """
    Forensic Tool: Converts PDF to markdown and applies semantic labels 
    to chunks for targeted judicial review.
    """
    if not os.path.exists(pdf_path):
        return {"error": "File not found"}
    
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        
        chunks = []
        # We use Docling's internal labels to categorize evidence
        for i, element in enumerate(result.document.texts):
            label = "[TEXT]"
            if element.label in ["heading", "title"]: 
                label = "[STRUCTURE]"
            elif any(k in element.text.lower() for k in ["parallel", "graph", "node", "edge"]):
                label = "[ARCH_CLAIM]"
            
            chunks.append({
                "id": i,
                "label": label,
                "content": element.text
            })

        return {
            "chunks": chunks,
            "metadata": {"total_elements": len(chunks)}
        }
    except Exception as e:
        return {"error": f"Semantic Ingestion Failed: {str(e)}"}

def query_pdf_chunks(chunks: List[Dict], query: str) -> List[Dict]:
    """
    Helper function to filter chunks based on search terms.
    Satisfies the import requirement in the detective node.
    """
    query_lower = query.lower()
    return [c for c in chunks if query_lower in c["content"].lower()]