# RAG Dashboard (Streamlit)

**Live UI:** https://huggingface.co/spaces/HamidOmarov/RAG-Dashboard  
**Back-end API:** https://huggingface.co/spaces/HamidOmarov/FastAPI-RAG-API

Upload a PDF → Ask a question → See answer + top contexts.  
Stack: Streamlit · FastAPI (FAISS + sentence-transformers)

---

## Quick demo

<!-- DİQQƏT: raw.githubusercontent.com istifadə olunur (blob deyil!) -->
<video src="https://raw.githubusercontent.com/HamidOmarov/rag-dashboard/main/assets/demo.mp4" controls width="720"></video>

> Əgər video brauzerində oynamasa, birbaşa fayl kimi aç:  
> https://raw.githubusercontent.com/HamidOmarov/rag-dashboard/main/assets/demo.mp4

---

## Configure API endpoint
Dashboard, API bazasını `secrets.toml` ilə oxuyur.

