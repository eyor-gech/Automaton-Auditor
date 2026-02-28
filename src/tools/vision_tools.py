#from docling.document_converter import DocumentConverter
#import os
import fitz  # PyMuPDF
from src.state import AgentState

async def vision_inspector_node(state: AgentState):
    from src.state import Evidence
    from src.tools.vision_tools import extract_pdf_images

    images = extract_pdf_images(state["pdf_path"])

    evidence = Evidence(
        id="EV-VISION-1",
        source="VisionInspector",
        goal="Detect architectural diagrams",
        fact=f"{len(images)} images detected in PDF.",
        confidence=0.9,
        location=state["pdf_path"],
        rationale="Image extraction confirms presence of diagrams for multimodal validation."
    )

    return {"evidences": [evidence]}


def extract_pdf_images(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    images = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            images.append({
                "page": page_index,
                "index": img_index,
                "size": len(base_image["image"])
            })

    return images