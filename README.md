**Description**: Automated Auditor Swarms for QA: Multi-agent system that verifies code, evaluates architecture, and provides actionable feedback.

# 🕵️ **Automaton-Auditor**
## **Forensic Governance Swarm for AI-Generated Code**
- Automaton-Auditor is a multi-agent system built on LangGraph designed to perform high-integrity audits of software repositories. Moving beyond "vibe-based" reviews, it uses a Triple-Diamond architecture to cross-reference code (AST), documentation (OCR/Markdown), and visual diagrams (Vision) to identify hallucinations and architectural drift.
## **🏗️ Architecture: The Triple-Threat Fan-Out**
The system currently implements the **Detective Layer**. It utilizes a parallel fan-out pattern to gather multi-modal evidence before synchronizing at a metacognitive aggregator.
  - **RepoInvestigator**: Deep AST parsing to verify graph wiring and structural logic.
  - **DocAnalyst**: OCR-backed ingestion of PDF reports to extract theoretical claims.
  - **VisionInspector**: Heuristic image extraction to verify the presence of architectural diagrams.
  - **Evidence Aggregator**: A synchronization node that flags discrepancies (e.g., PDF claims "Parallelism" while AST shows "Linear").
## **🛠️ Setup Instructions**
1. Prerequisites
   - **Python 3.12+** (Optimized for 3.12)
   - **uv** (Fast Python package installer and resolver)
   - **Environment Variables**: Create a .env file in the root directory
```Bash
OPENAI_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here  # Optional: For graph tracing
LANGCHAIN_TRACING_V2=true
```

2. **Install Dependencies**
We use uv for deterministic dependency management. This ensures your environment matches the forensic lab's requirements perfectly.
```Bash
# Install uv if you haven't already
pip install uv

# Sync the environment (creates .venv and installs locked dependencies)
uv sync
```
3. **System Dependencies (OCR Support)**
The DocAnalyst uses Docling and RapidOCR. On some systems (Windows/Linux), you may need libmagic or poppler if not already present.
## **🚀 Running the Detective Graph**
To run a forensic audit against a target repository and its corresponding documentation, use the interim test runner:
```Bash
# Run the core detective logic
python -m tests.test_interim_logic
```
**Custom Audit Configuration**
You can modify the test script or pass arguments to the AgentState:
- **repo_url**: The GitHub/GitLab URL of the project to audit
- **pdf_path**: Local path to the student's architecture/interim report (PDF).
**Output Expectations**
The system will output a series of Evidence Objects in the terminal:
  - **✅ Success**: Artifact found (e.g., AST confirms Parallel wiring).
  - **❌ Forensic Violation**: Discrepancy found (e.g., Hallucination Alert
  - **⚠️ System Error**: Handled gracefully (e.g., 404 Repo URL detected).

## **📂 Project Structure**
```Plaintext
├── src/
│   ├── nodes/           # Agent "Brains" (detectives.py, judges.py)
│   ├── tools/           # Forensic tools (AST, OCR, Git)
│   ├── state.py         # Pydantic schemas & Graph state
│   └── graph.py         # LangGraph orchestration logic
├── tests/               # Stress tests & wiring verification
├── reports/             # Interim Report
├── pyproject.toml       # Locked dependency manifest
└── README.md            # This document
```
## **⚖️ Roadmap**
- Phase 1-2: Detective Swarm & Evidence Aggregation. (Completed)
- Phase 3: Judicial Debate (Prosecutor vs. Defense vs. Tech Lead).
- Phase 4: Chief Justice Synthesis & Remediation Planning.

## **General Architecture**
<img width="5406" height="4505" alt="image" src="https://github.com/user-attachments/assets/05100c0c-dd3f-4316-9f33-994e4c29a366" />

## Run Full Audit
```bash
uv lock
uv sync
uv run python main.py \
  --repo https://github.com/user/project.git \
  --pdf ./report.pdf
```