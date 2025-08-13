# streamlit_app.py
# -*- coding: utf-8 -*-
import os
import time
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# Page config (ASCII-only to avoid encoding issues when pasting from terminals)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RAG Dashboard",
    page_icon="📄",
    layout="wide",
)

# -----------------------------------------------------------------------------
# API base resolver: ENV -> secrets -> default
# -----------------------------------------------------------------------------
DEFAULT_API = "https://hamidomarov-fastapi-rag-api.hf.space"

def _resolve_api_base() -> str:
    # 1) ENV
    env_val = os.getenv("API_BASE")
    if env_val:
        return env_val.rstrip("/")
    # 2) Streamlit secrets (ignore if missing)
    try:
        val = st.secrets["API_BASE"]
        if isinstance(val, str) and val.strip():
            return val.rstrip("/")
    except Exception:
        pass
    # 3) Default
    return DEFAULT_API

API_BASE = _resolve_api_base()

# -----------------------------------------------------------------------------
# HTTP helper
# -----------------------------------------------------------------------------
def fetch_json(path: str, method: str = "GET", *, json_body=None, files=None, timeout=60):
    """Simple fetch with cache-busting for GET and friendly error shape."""
    url = f"{API_BASE}{path}"
    try:
        if method.upper() == "GET":
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}t={int(time.time())}"
            r = requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            if files is not None:
                r = requests.post(url, files=files, timeout=timeout)
            else:
                r = requests.post(url, json=json_body, timeout=timeout)
        else:
            raise ValueError("Unsupported HTTP method")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}
    except requests.HTTPError as he:
        text = ""
        try:
            text = he.response.text
        except Exception:
            text = str(he)
        code = getattr(he.response, "status_code", "???")
        return {"_error": f"HTTP {code}: {text[:500]}", "_url": url}
    except Exception as e:
        return {"_error": str(e), "_url": url}

# -----------------------------------------------------------------------------
# Sidebar: API base, refresh/clear, health, quick stats
# -----------------------------------------------------------------------------
with st.sidebar:
    st.caption("API Base")
    st.code(API_BASE, language="text")

    c1, c2 = st.columns(2)
    if c1.button("Refresh", use_container_width=True):
        # modern Streamlit: use st.rerun()
        try:
            st.cache_data.clear()
        except Exception:
            pass
        try:
            st.cache_resource.clear()
        except Exception:
            pass
        st.rerun()

    if c2.button("Clear state", use_container_width=True):
        try:
            st.cache_data.clear()
        except Exception:
            pass
        try:
            st.cache_resource.clear()
        except Exception:
            pass
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.success("Session state cleared.")

    st.divider()
    st.subheader("Health")
    health = fetch_json("/health")
    if "_error" in health:
        st.error(f"Health error: {health['_error']}")
    else:
        ok = isinstance(health, dict) and health.get("status") == "ok"
        st.metric("Status", "Healthy ✓" if ok else "Degraded ⚠️")
        st.caption(
            f"Version: {health.get('version','n/a')} • "
            f"Summarizer: {health.get('summarizer','n/a')}"
        )

    st.divider()
    st.subheader("Quick Stats")
    stats = fetch_json("/stats")
    total_chunks = 0
    if isinstance(stats, dict) and "_error" not in stats:
        total_chunks = int(
            stats.get("total_chunks")
            or stats.get("faiss_ntotal")
            or 0
        )
        st.metric("Indexed Chunks", total_chunks)
        st.caption(
            f"FAISS ntotal: {stats.get('faiss_ntotal','n/a')} • "
            f"Model dim: {stats.get('model_dim','n/a')}"
        )
    else:
        # Fallback via /get_history if /stats unavailable
        hist = fetch_json("/get_history")
        if isinstance(hist, dict) and "_error" not in hist:
            total_chunks = int(hist.get("total_chunks", 0))
        st.metric("Indexed Chunks", total_chunks)
        if isinstance(stats, dict) and "_error" in stats:
            st.caption("`/stats` unavailable; using `/get_history` fallback.")

    st.info("Charts & more: open the **Analytics** page from the sidebar.")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("RAG Dashboard (Streamlit)")
st.caption("Upload a PDF, ask a question, and review retrieved contexts.")

# -----------------------------------------------------------------------------
# Main layout
# -----------------------------------------------------------------------------
left, right = st.columns([1, 1.2], gap="large")

# Left: Upload
with left:
    st.header("Upload PDF")
    up = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        accept_multiple_files=False,
        help="Limit ~200MB per file.",
    )
    if st.button("Upload", type="primary", use_container_width=True, disabled=not up):
        if not up:
            st.warning("Please select a PDF first.")
        else:
            try:
                files = {"file": (up.name, up.getvalue(), "application/pdf")}
                with st.spinner("Uploading & indexing…"):
                    res = fetch_json("/upload_pdf", method="POST", files=files, timeout=300)
                if "_error" in res:
                    st.error(f"Upload failed: {res['_error']}")
                else:
                    st.success(
                        f"Indexed {res.get('chunks_added','?')} chunk(s) from "
                        f"{res.get('filename', up.name)}"
                    )
                    with st.expander("Upload response"):
                        st.json(res)
            except Exception as e:
                st.error(f"Upload error: {e}")

    st.caption("Tip: Prefer text PDFs (not scans) for best results.")

# Right: Ask
with right:
    st.header("Ask a Question")
    q = st.text_input(
        "Type your question",
        placeholder="e.g., What is the main goal of the document?"
    )
    k = st.number_input("Top K", min_value=1, max_value=20, value=5, step=1)

    c1, c2 = st.columns([1, 1])
    if c1.button("Ask", type="primary", use_container_width=True):
        if not q.strip():
            st.warning("Please enter a question.")
        else:
            payload = {"question": q.strip(), "top_k": int(k), "nonce": str(time.time())}
            with st.spinner("Querying API…"):
                res = fetch_json("/ask_question", method="POST", json_body=payload, timeout=120)
            if "_error" in res:
                st.error(f"API error: {res['_error']}")
            else:
                st.session_state["last_answer"] = res

    if c2.button("Clear answer", use_container_width=True):
        st.session_state.pop("last_answer", None)

    ans = st.session_state.get("last_answer")
    if ans:
        st.subheader("Answer")
        # Render markdown so bullet points show nicely
        st.markdown(ans.get("answer", ""))

        ctxs = ans.get("contexts") or ans.get("top_contexts") or []
        if isinstance(ctxs, list) and ctxs:
            with st.expander("Top contexts"):
                preview = [str(x) for x in ctxs[:3]]
                st.code(("\n\n" + "-" * 24 + "\n\n").join(preview), language="text")
        else:
            st.caption("No contexts returned.")

        with st.expander("Debug: Raw response"):
            st.json(ans)

# -----------------------------------------------------------------------------
# History (best-effort)
# -----------------------------------------------------------------------------
st.divider()
st.subheader("History")
hist = fetch_json("/get_history")
if isinstance(hist, dict) and hist.get("history"):
    for row in hist["history"][:5]:
        ts = row.get("timestamp", "")
        qtxt = row.get("question", "(no question)")
        st.info(f"• {qtxt} — {ts}")
else:
    st.info("• What is the document about? — (just now)")
    st.info("• List key figures mentioned. — (2 min ago)")
    st.info("• Extract the main scope. — (10 min ago)")

# Footer
st.caption("Backend: FastAPI • Embeddings: all-MiniLM-L6-v2 • Vector DB: FAISS")
