from docling.document_converter import DocumentConverter
from typing import List

def ingest_pdf_content(pdf_path: str) -> str:
    """Converts PDF to Markdown for LLM readability."""
    if not pdf_path.endswith(".pdf"):
        return "Error: File is not a PDF."
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

def search_for_keywords(text: str, keywords: List[str]) -> dict:
    """Heuristic check for theoretical depth in the report."""
    findings = {}
    text_lower = text.lower()
    for kw in keywords:
        count = text_lower.count(kw.lower())
        findings[kw] = {
            "count": count,
            "is_substantive": count > 0
        }
    return findings