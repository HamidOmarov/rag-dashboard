import base64, requests, streamlit as st

st.set_page_config(page_title="RAG Dashboard", page_icon="📄")

DEFAULT_API = st.secrets.get("API_BASE", "https://HamidOmarov-FastAPI-RAG-API.hf.space")
st.sidebar.header("⚙️ Settings")
API_BASE = st.sidebar.text_input("API Base URL", value=DEFAULT_API, help="Məs: https://username-fastapi-rag-api.hf.space")
if API_BASE.endswith("/"):
    API_BASE = API_BASE[:-1]

if "session_id" not in st.session_state:
    st.session_state.session_id = None

page = st.sidebar.radio("Pages", ["Home", "PDF Viewer", "Chat", "Analytics"])

def _req(method, path, **kw):
    url = f"{API_BASE}{path}"
    r = requests.request(method, url, timeout=90, **kw)
    r.raise_for_status()
    return r.json()

def show_pdf_inline(file_bytes: bytes, height: int = 600):
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    html = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{height}" type="application/pdf"></iframe>'
    st.components.v1.html(html, height=height)

if page == "Home":
    st.title("📄 RAG Dashboard")
    try:
        st.success(_req("GET", "/health"))
    except Exception as e:
        st.error(f"API-ya qoşulmaq olmur: {e}")

elif page == "PDF Viewer":
    st.title("📄 PDF Upload & Preview")
    pdf = st.file_uploader("PDF seç", type=["pdf"])
    if pdf:
        with st.expander("Preview", expanded=True):
            show_pdf_inline(pdf.getvalue(), 600)
        if st.button("API-yə yüklə"):
            try:
                files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                st.success(_req("POST", "/upload_pdf", files=files))
            except Exception as e:
                st.error(f"Yükləmə xətası: {e}")

elif page == "Chat":
    st.title("💬 Chat with RAG")
    q = st.text_input("Sualını yaz")
    top_k = st.number_input("Top-K", 1, 10, 5)
    if st.button("Sor"):
        if not q.strip():
            st.warning("Sual boş ola bilməz.")
        else:
            try:
                payload = {"question": q, "session_id": st.session_state.session_id, "top_k": int(top_k)}
                data = _req("POST", "/ask_question", json=payload)
                st.session_state.session_id = data.get("session_id", st.session_state.session_id)
                st.subheader("Cavab")
                st.write(data.get("answer", ""))
                with st.expander("Contexts"):
                    for c in data.get("contexts", []):
                        st.write(c)
            except Exception as e:
                st.error(f"Sual zamanı xəta: {e}")

elif page == "Analytics":
    st.title("📈 Session Analytics")
    sid = st.text_input("Session ID", value=st.session_state.get("session_id") or "")
    if st.button("Tarixçəni gətir"):
        if not sid:
            st.warning("Session ID daxil et.")
        else:
            try:
                data = _req("GET", "/get_history", params={"session_id": sid})
                hist = data.get("history", [])
                st.write(f"Mesaj sayı: {len(hist)}")
                for item in hist:
                    role, content = item.get("role"), item.get("content")
                    st.markdown(f"**{'👤 User' if role=='user' else '🤖 Assistant'}:** {content}")
            except Exception as e:
                st.error(f"Analytics xətası: {e}")
