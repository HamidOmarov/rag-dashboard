# streamlit_app.py
import requests
import streamlit as st

st.set_page_config(page_title="RAG Dashboard", page_icon="📄")

API_BASE = st.secrets.get("API_BASE", "https://HamidOmarov-FastAPI-RAG-API.hf.space")

st.title("RAG Dashboard")
st.caption("Upload a PDF, ask a question, and view context hits.")

with st.sidebar:
    st.header("Actions")
    api_url = st.text_input("API Base URL", API_BASE)
    if st.button("Health Check"):
        r = requests.get(f"{api_url}/health", timeout=30)
        st.write(r.json())

st.subheader("Upload PDF")
pdf_file = st.file_uploader("Choose PDF", type=["pdf"])
if st.button("Upload PDF"):
    if not pdf_file:
        st.warning("Please select a PDF first.")
    else:
        files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
        r = requests.post(f"{api_url}/upload_pdf", files=files, timeout=120)
        st.success(r.json())

st.subheader("Ask a Question")
question = st.text_input("Type your question")
top_k = st.number_input("Top K", min_value=1, max_value=10, value=5, step=1)
if st.button("Ask"):
    if not question.strip():
        st.warning("Please type a question.")
    else:
        payload = {"question": question.strip(), "top_k": int(top_k)}
        r = requests.post(f"{api_url}/ask_question", json=payload, timeout=60)
        data = r.json()
        st.markdown("### Answer")
        st.code(data.get("answer", ""), language="markdown")
        with st.expander("Contexts"):
            for i, ctx in enumerate(data.get("contexts", []), 1):
                st.markdown(f"**Context {i}:**")
                st.write(ctx)

st.subheader("History")
if st.button("Show History"):
    r = requests.get(f"{api_url}/get_history", timeout=30)
    st.write(r.json())
