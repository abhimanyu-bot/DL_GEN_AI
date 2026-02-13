import streamlit as st
import sys
import os

# 1. Setup path to find the backend files
# This allows app.py to import engine and auth from the backend folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from auth import check_login
from engine import generate_response
from config import TEMP_MAP, MODEL_NAME

# 2. Page Configuration
st.set_page_config(
    page_title="Nike AI Consultant | Policy Auditor",
    page_icon="🛡️",
    layout="wide"
)

# 3. Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 4. Sidebar - Parameter Benchmarking
def draw_sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg", width=100)
        st.title("⚙️ RAG Settings")
        st.write("Experiment with parameters to see impact on hallucinations and latency.")
        
        mode = st.selectbox(
            "Select Auditor Persona", 
            list(TEMP_MAP.keys()),
            help="Strict uses Temp 0.0 (factual), Creative uses Temp 0.8 (risky)."
        )
        
        st.divider()
        st.info(f"**Architecture:** Llama-3.3-70B + ChromaDB\n\n**Mode:** {mode}")
        return TEMP_MAP[mode]

# 5. Main Logic - Login vs. App
if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    st.container()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Consultant Portal")
        st.subheader("Nike Brand Integrity System")
        with st.form("login_form"):
            user = st.text_input("Username (admin)")
            pw = st.text_input("Password (nike123)", type="password")
            if st.form_submit_button("Login"):
                if check_login(user, pw):
                    st.session_state.logged_in = True
                    st.success("Access Granted.")
                    st.rerun()
                else:
                    st.error("Unauthorized. Please check credentials.")
else:
    # --- MAIN AUDITOR APP ---
    selected_temp = draw_sidebar()

    st.title("🛡️ Nike Brand Integrity Auditor")
    st.markdown("---")

    # Input Section
    description = st.text_area(
        "Enter Product/Campaign Description:", 
        placeholder="e.g., A new shoe featuring recycled lead-based dyes for toddlers...",
        height=150
    )

    if st.button("🚀 Run Compliance Audit"):
        if not description.strip():
            st.warning("Please enter a description to analyze.")
        else:
            with st.spinner("Retrieving Internal Policies & Benchmarking Response..."):
                # Call the engine with the selected temperature from the sidebar
                result = generate_response(description, temperature=selected_temp)

            # A. Performance Dashboard (Benchmarking Deliverable)
            st.subheader("📊 Performance Benchmarks")
            m1, m2, m3 = st.columns(3)
            m1.metric("Retrieval + Gen Latency", result["latency"])
            
            # Faithfulness logic: 1.0 is high, <0.7 is a hallucination risk
            f_score = result["faithfulness"]
            m2.metric("Faithfulness Score", f"{int(f_score * 100)}%", delta="High Accuracy" if f_score > 0.8 else "Hallucination Risk")
            m3.metric("Primary Model", MODEL_NAME)

            # B. Final Evaluation (Brand Voice & CoT)
            st.subheader("📋 Auditor Final Report")
            st.markdown(result["answer"])

            # C. Evidence Verification (UI Requirement)
            st.divider()
            st.subheader("🔍 Source Verification (Retrieved Chunks)")
            
            tab1, tab2 = st.tabs(["Semantic (Vector) Results", "Keyword (BM25) Results"])
            
            with tab1:
                st.caption("Context retrieved based on conceptual meaning.")
                for doc in result["semantic_chunks"]:
                    with st.expander(f"📄 {doc.metadata.get('source_file', 'Unknown Source')}"):
                        st.write(doc.page_content)
                        st.caption(f"Metadata: {doc.metadata}")

            with tab2:
                st.caption("Context retrieved based on exact keyword matches.")
                for doc in result["keyword_chunks"]:
                    with st.expander(f"📄 {doc.metadata.get('source_file', 'Unknown Source')}"):
                        st.write(doc.page_content)
                        st.caption(f"Metadata: {doc.metadata}")

    # Logout Button at the bottom
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()