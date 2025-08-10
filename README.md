# RAG Dashboard (Streamlit)

**Live:** https://huggingface.co/spaces/HamidOmarov/RAG-Dashboard  
**Back-end API:** https://huggingface.co/spaces/HamidOmarov/FastAPI-RAG-API

Upload a PDF > Ask a question > See answer + top contexts.

## How it works
- Frontend: Streamlit
- Backend API: FastAPI (FAISS + sentence-transformers)
- Robust to table-heavy docs; AZ>EN translation + fallbacks

## Local run
pip install -r requirements.txt
streamlit run app.py    # v? ya streamlit_app.py (repo v?ziyy?tin? gor?)

## Configure API endpoint
Create `.streamlit/secrets.toml`:
API_BASE = "https://HamidOmarov-FastAPI-RAG-API.hf.space"

[Watch demo (MP4)](assets/Recording 2025-08-10 182048.mp4)