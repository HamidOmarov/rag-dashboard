# streamlit_dashboard/pages/qa_dataset.py
import os
import io
import json
import requests
import streamlit as st

st.set_page_config(page_title="PDF → Q&A Dataset", page_icon="🧩", layout="wide")
st.title("🧩 PDF → Q&A Dataset")

# ---- Config ----
PDF_QA_BASE = st.secrets.get(
    "PDF_QA_BASE",
    os.getenv("PDF_QA_BASE", "https://hamidomarov-pdf-qa-generator.hf.space")
).rstrip("/")

GENERATE_URL = f"{PDF_QA_BASE}/generate"            # backend-də alias var
HEALTH_URL    = f"{PDF_QA_BASE}/health"

# ---- Health check ----
health_col, cfg_col = st.columns([3,2], gap="large")
with health_col:
    try:
        r = requests.get(HEALTH_URL, timeout=8)
        r.raise_for_status()
        st.success(f"API OK: {PDF_QA_BASE}")
    except Exception as e:
        st.warning(f"API unavailable: {e}\nUsing configured base: {PDF_QA_BASE}")

with cfg_col:
    with st.expander("⚙️ Config"):
        st.write({"PDF_QA_BASE": PDF_QA_BASE})
        st.caption("Change via .streamlit/secrets.toml or environment variable.")

# ---- UI ----
uploaded = st.file_uploader("PDF seç", type=["pdf"], accept_multiple_files=False, help="Limit 200MB per file • PDF")
col_a, col_b, col_c = st.columns([1,1,2])
with col_a:
    num_q = st.number_input("Sual sayı", min_value=1, max_value=200, value=10, step=1)
with col_b:
    lang = st.selectbox("Dil", ["en", "az", "tr"], index=0)
with col_c:
    st.caption("Large PDFs can take longer. The backend will return JSON/CSV/JSONL download links.")

go = st.button("Generate Dataset", type="primary", use_container_width=True, disabled=(uploaded is None))

# ---- Action ----
if go and uploaded:
    try:
        file_bytes = uploaded.read()
        files = {
            "file": (uploaded.name, io.BytesIO(file_bytes), "application/pdf")
        }
        data = {
            "num_questions": str(num_q),
            "language": lang
        }

        with st.spinner("Generating Q&A pairs..."):
            resp = requests.post(GENERATE_URL, files=files, data=data, timeout=120)
            resp.raise_for_status()
            payload = resp.json()

        st.success(f"Dataset ready: {payload.get('count', 0)} Q&A")
        preview = payload.get("dataset_preview") or []
        formats = payload.get("formats") or {}

        # ---- Preview table ----
        if preview:
            st.subheader("Preview (first 3)")
            for i, row in enumerate(preview, 1):
                with st.expander(f"Q{i}: {row.get('question', '')[:80]}"):
                    st.markdown(f"**Question:** {row.get('question','')}")
                    st.markdown(f"**Answer:** {row.get('answer','')}")
                    if row.get("context"):
                        st.code(row["context"][:1200])

        # ---- Download links ----
        st.subheader("Downloads")
        dcols = st.columns(3)
        for j, (fmt, url) in enumerate(formats.items()):
            with dcols[j % 3]:
                st.markdown(f"[⬇️ {fmt.upper()}]({url})")

        # ---- Raw JSON (optional)
        with st.expander("Raw response"):
            st.code(json.dumps(payload, ensure_ascii=False, indent=2))

    except requests.HTTPError as he:
        st.error(f"API error: {he} — {getattr(he.response, 'text', '')}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
