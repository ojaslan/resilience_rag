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

| Component | Technology |
|---|---|
| 🚀 LLM | Groq — `llama3-70b-8192` (ultra-fast inference) |
| 🔗 Agent | LangChain — orchestration & tool use |
| 📚 RAG | ChromaDB + HuggingFace Embeddings |
| 🛡️ Guardrails | Input/output validation & safety |
| 💥 Chaos Engineering | Fault injection & resilience testing |
| 🖥️ UI | Streamlit |

### 👈 Navigate using the sidebar:
- **💬 Chat** — Ask questions with RAG + Guardrails
- **💥 Chaos Panel** — Run chaos experiments  
- **📊 Monitor** — View metrics & logs
""")

st.info("💡 Make sure your `GROQ_API_KEY` is set in the `.env` file before starting.")
