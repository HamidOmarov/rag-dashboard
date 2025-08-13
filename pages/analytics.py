import os, json, requests, streamlit as st
from datetime import datetime

st.set_page_config(page_title="Analytics", page_icon="📊")
st.title("📊 System Analytics")

API = st.secrets.get("API_BASE", os.getenv("API_BASE", "https://hamidomarov-fastapi-rag-api.hf.space"))

col1, col2, col3 = st.columns(3)
def metric_safe(label, value, delta=None):
    try: st.metric(label, value, delta)
    except: st.metric(label, value)

try:
    stats = requests.get(f"{API}/stats", timeout=10).json()
    hist  = requests.get(f"{API}/get_history", timeout=10).json()

    metric_safe("Total chunks", stats.get("total_chunks", 0))
    metric_safe("Questions answered", stats.get("questions_answered", len(hist.get('history', []))))
    metric_safe("Avg response (ms)", stats.get("avg_ms", 0))

    st.subheader("📈 Last 7 days (questions)")
    series = stats.get("last7_questions", [2,3,4,5,6,4,3])
    st.bar_chart({"Questions": series})

    st.subheader("🕐 Recent Queries")
    items = hist.get("history", [])[-10:][::-1]
    if not items: st.info("No history yet.")
    for h in items:
        ts = h.get("timestamp","")
        q  = h.get("question","")
        st.write(f"• {ts} — {q}")

except Exception as e:
    st.error(f"API unreachable: {e}")
    st.caption(f"API_BASE={API}")