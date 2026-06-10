import streamlit as st

st.set_page_config(
    page_title="ResilienceAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 ResilienceAI — Agentic AI Dashboard")
st.markdown("""
Welcome to **ResilienceAI**, a self-healing agentic system powered by **Groq**:



### 👈 Navigate using the sidebar:
- **💬 Chat** — Ask questions with RAG + Guardrails
- **💥 Chaos Panel** — Run chaos experiments  
- **📊 Monitor** — View metrics & logs
""")

st.info("💡 Make sure your `GROQ_API_KEY` is set in the `.env` file before starting.")
