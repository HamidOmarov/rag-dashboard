# RAG Dashboard (Streamlit)

**Live:** https://huggingface.co/spaces/HamidOmarov/RAG-Dashboard  
**Back-end API:** https://huggingface.co/spaces/HamidOmarov/FastAPI-RAG-API

<video src="https://github.com/HamidOmarov/rag-dashboard/blob/main/assets/demo.mp4" controls width="720"></video>



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



<video src="https://raw.githubusercontent.com/HamidOmarov/rag-dashboard/main/assets/demo.mp4" controls width="720"></video>

