import streamlit as st
import json
import statistics
from src.graph import graph


# --- UI CONFIGURATION ---
st.set_page_config(page_title="Forensic Auditor Pro", page_icon="⚖️", layout="wide")

# Custom CSS for a "Command Center" feel
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2900/2900198.png", width=100) # Gavel Icon
    st.title("Audit Settings")
    st.divider()
    
    repo_url = st.text_input("📁 Repository URL", placeholder="https://github.com/...")
    pdf_path = st.text_input("📄 Architecture PDF Path", placeholder="C:/Users/...")
    
    st.subheader("⚖️ Grading Rubric")
    default_rubric = {
        "Parallelism": "Score 5 if graph shows fan-out/fan-in patterns.",
        "State Management": "Score 5 if Pydantic and Reducers are implemented.",
        "Git History": "Score 5 if commits are atomic and descriptive."
    }
    rubric_json = st.text_area("JSON Schema", value=json.dumps(default_rubric, indent=2), height=200)
    
    st.divider()
    run_audit = st.button("⚖️ COMMENCE FORENSIC AUDIT", type="primary", use_container_width=True)

# --- MAIN INTERFACE ---
st.title("⚖️ Automaton Auditor: Supreme Court Edition")
st.caption("Local Multi-Agent Forensic System | Powered by LangGraph & Ollama")

if not run_audit:
    st.info("👈 Enter the repository and PDF details in the sidebar to begin the trial.")
    # Placeholder for a professional "Waiting" state
    st.image("https://miro.medium.com/v2/resize:fit:1400/1*m_S9_m0K6O5kE7-hU8O4mw.png", caption="System Architecture Visualization")

else:
    # 1. INITIALIZATION
    initial_state = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric": json.loads(rubric_json),
        "evidences": {},
        "opinions": [],
        "human_approved": False,
        "instructor_feedback": ""
    }

    # 2. EXECUTION WITH STATUS UPDATES
    with st.status("🏛️ Court is in Session...", expanded=True) as status:
        st.write("🔍 Detectives: Scanning AST and PDF semantic chunks...")
        final_state = graph.invoke(initial_state)
        st.write("⚖️ Judges: Engaging in adversarial debate...")
        status.update(label="✅ Audit Complete", state="complete", expanded=False)

    # 3. TOP-LEVEL METRICS (The "Quick Look")
    report = final_state["final_report"]
    opinions = final_state["opinions"]
    scores = [o.score for o in opinions]
    variance = statistics.variance(scores) if len(scores) > 1 else 0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Final Verdict Score", f"{report.overall_score:.1f} / 5.0")
    with m2:
        confidence = "High" if variance < 1 else "Contested"
        st.metric("Forensic Confidence", confidence, delta=f"-{variance:.2f} Variance", delta_color="inverse")
    with m3:
        st.metric("Evidence Points", len(final_state["evidences"].get("repo_investigator", []) + final_state["evidences"].get("doc_analyst", [])))

    st.divider()

    # 4. TABS: THE RESULTS HUB
    tab_verdict, tab_debate, tab_evidence = st.tabs(["📜 Executive Verdict", "🗣️ Judicial Debate", "🔍 Raw Evidence"])

    with tab_verdict:
        st.header("📜 Chief Justice's Executive Summary")
    
    # Check if report exists before rendering
    if report:
        st.markdown(report.executive_summary)
        
        st.subheader("🛠️ Remediation Mandate")
        st.info(report.remediation_plan)
        
        if variance > 2:
            st.warning("⚠️ **High Judicial Dissent:** Significant conflict detected between Prosecutor and Defense. Manual review of the 'Judicial Debate' tab is highly recommended.")
    else:
        st.error("No report generated. Please check the logs for agent errors.")

    with tab_debate:
        st.header("Adversarial Dissent & Arguments")
        for op in opinions:
            with st.expander(f"{op.judge} — Score: {op.score}/5"):
                st.write(f"**Argument:** {op.argument}")
                st.caption(f"**Citations:** {', '.join(op.cited_evidence)}")

    with tab_evidence:
        st.header("Forensic Evidence Logs")
        col_repo, col_doc = st.columns(2)
        with col_repo:
            st.subheader("Repository Findings")
            st.write(final_state["evidences"].get("repo_investigator", []))
        with col_doc:
            st.subheader("Document Findings")
            st.write(final_state["evidences"].get("doc_analyst", []))

    # 5. THE SUPREME COURT GAVEL (Human-in-the-Loop)
    st.divider()
    st.header("👨‍⚖️ Final Judicial Review")
    with st.container():
        instr_feedback = st.text_area("Add Instructor Comments (for Student Feedback Report)")
        final_decision = st.radio("Final Ruling:", ["Uphold AI Verdict", "Modify Grade", "Overturn & Request Resubmission"], horizontal=True)
        
        if st.button("⚖️ SIGN & SEAL VERDICT", type="primary"):
            st.balloons()
            st.success("Verdict Finalized. Report archived.")