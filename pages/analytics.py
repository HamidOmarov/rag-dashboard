import os, pandas as pd, streamlit as st, requests
import datetime as dt

st.set_page_config(page_title="Analytics • RAG Dashboard", page_icon="📈", layout="wide")
API_BASE = st.secrets.get("API_BASE", os.getenv("API_BASE","").strip())

st.title("Analytics")
if not API_BASE:
    st.error("API_BASE not configured.")
    st.stop()

colA, colB, colC = st.columns(3)
try:
    s = requests.get(f"{API_BASE}/stats", timeout=15).json()

    # Top metriklər — mövcud açarlara görə elastik oxuma
    total_chunks = s.get("total_chunks") or s.get("faiss_ntotal") or 0
    questions_answered = s.get("questions_answered") or 0
    avg_ms = s.get("avg_ms") or 0
    colA.metric("Total Chunks", total_chunks)
    colB.metric("Questions Answered", questions_answered)
    colC.metric("Avg Latency (ms)", avg_ms)

    # Last 7 — iki formatdan birini dəstəklə:
    # 1) [{"date":"2025-08-10","questions":5}, ...]
    # 2) [5,8,12,7,0,0,3]  → bu halda tarixləri lokaldan generasiya edirik
    st.subheader("Last 7 days — Questions")
    today = dt.date.today()
    dates = [(today - dt.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    series = None
    if isinstance(s.get("last7"), list) and len(s["last7"]) and isinstance(s["last7"][0], dict):
        series = s["last7"]
        df = pd.DataFrame(series).set_index("date")
    elif isinstance(s.get("last7_questions"), list):
        counts = s["last7_questions"]
        # uzunluğu 7-yə uyğunlaşdır
        if len(counts) < 7: counts = [0]*(7-len(counts)) + counts
        if len(counts) > 7: counts = counts[-7:]
        df = pd.DataFrame({"date": dates, "questions": counts}).set_index("date")
    else:
        df = pd.DataFrame({"date": dates, "questions": [0]*7}).set_index("date")

    st.bar_chart(df["questions"])

    # Last N Questions — backend iki variantdan birini verə bilər
    st.subheader("Last N Questions")
    lastN = s.get("lastN_questions")
    if not lastN:
        try:
            h = requests.get(f"{API_BASE}/get_history", timeout=10).json()
            lastN = h.get("history", [])
        except Exception:
            lastN = []
    st.json(lastN)
except Exception as e:
    st.error(f"Failed to load stats: {e}")
