from docling.document_converter import DocumentConverter
import os

def count_pdf_images(pdf_path: str) -> int:
    """
    Forensic Tool: Locally extracts and counts images without API calls.
    Proves that a visual architecture diagram exists.
    """
    if not os.path.exists(pdf_path):
        return 0
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        
        image_count = sum(len(page.images) for page in result.document.pages)
        return image_count
    except Exception:
        return 0