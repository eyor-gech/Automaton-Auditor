from docling.document_converter import DocumentConverter
import os

async def vision_inspector_node(state: AgentState):
    from src.state import Evidence
    from src.tools.vision_tools import count_pdf_images

    count = count_pdf_images(state["pdf_path"])

    evidence = Evidence(
        id="VISION_1",
        source="VisionInspector",
        fact=f"{count} images detected in PDF.",
        confidence=1.0,
        location=state["pdf_path"],
        rationale="PDF image extraction confirms presence of diagrams."
    )

    return {"evidences": {"vision": [evidence]}}