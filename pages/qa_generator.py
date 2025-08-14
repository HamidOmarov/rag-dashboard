# pages/qa_generator.py
import os, io, json, requests, streamlit as st
st.set_page_config(page_title="Q&A Generator", page_icon="🧩")

st.title("🧩 PDF → Q&A Dataset")

GEN_API = st.secrets.get(
    "GENERATOR_BASE",
    os.getenv("GENERATOR_BASE", "https://hamidomarov-pdf-qa-generator.hf.space").rstrip("/")
)

with st.sidebar:
    st.caption("Generator API")
    st.code(GEN_API, language="text")

pdf = st.file_uploader("PDF seç", type=["pdf"])
numq = st.number_input("Sual sayı", 1, 50, 10, 1)

col1, col2 = st.columns(2)
go = col1.button("Generate", type="primary", use_container_width=True, disabled=not pdf)
clear = col2.button("Clear", use_container_width=True)

if clear:
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun if hasattr(st, "experimental_rerun") else st.rerun()

if go:
    files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
    with st.spinner("Generating…"):
        try:
            r = requests.post(f"{GEN_API}/generate", files=files, data={"num_questions": str(numq)}, timeout=300)
            r.raise_for_status()
            st.session_state["qa"] = r.json()
        except Exception as e:
            st.error(f"API error: {e}")

data = st.session_state.get("qa")
if data:
    st.success(f"Generated {data.get('qa_count',0)} pairs from **{data.get('filename','?')}**")
    st.json({"qa_count": data.get("qa_count"), "export_formats": data.get("export_formats")})

    # Table
    rows = data.get("dataset", [])
    if rows:
        st.subheader("Preview")
        # kompakt cədvəl
        show = [{"id": r.get("id"), "question": r.get("question"), "answer": r.get("answer")} for r in rows]
        st.dataframe(show, use_container_width=True)

        # Downloads (JSON / JSONL / CSV client-side)
        buf_json = io.BytesIO(json.dumps(rows, ensure_ascii=False, indent=2).encode("utf-8"))
        st.download_button("Download JSON", buf_json, file_name="qa_dataset.json", mime="application/json")

        buf_jsonl = io.BytesIO("\n".join(json.dumps(r, ensure_ascii=False) for r in rows).encode("utf-8"))
        st.download_button("Download JSONL", buf_jsonl, file_name="qa_dataset.jsonl", mime="application/jsonl")

        # sadə CSV (client-side)
        import csv
        csv_io = io.StringIO()
        w = csv.writer(csv_io)
        w.writerow(["id","question","answer","source_excerpt"])
        for r in rows:
            w.writerow([r.get("id"), r.get("question"), r.get("answer"), r.get("source_excerpt","")])
        st.download_button("Download CSV", io.BytesIO(csv_io.getvalue().encode("utf-8")), file_name="qa_dataset.csv", mime="text/csv")
