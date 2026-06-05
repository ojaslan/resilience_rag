import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agent.agent_runner import AgentRunner
from app.components.sidebar import render_sidebar
from app.components.chat_ui import render_chat_history

st.set_page_config(page_title="Chat | ResilienceAI", page_icon="💬", layout="wide")

if "agent" not in st.session_state:
    with st.spinner("Initializing Groq agent..."):
        st.session_state.agent = AgentRunner()

if "chaos" not in st.session_state:
    st.session_state.chaos = st.session_state.agent.chaos

if "messages" not in st.session_state:
    st.session_state.messages = []

session_id = render_sidebar(st.session_state.chaos)

st.title("💬 Chat with ResilienceAI")
st.caption("Powered by Groq (llama3-70b-8192) + LangChain + RAG + Guardrails")

render_chat_history(st.session_state.messages)

if prompt := st.chat_input("Ask anything from your knowledge base..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Groq is thinking..."):
            result = st.session_state.agent.run(prompt, session_id=session_id)

        st.markdown(result["answer"])

        cols = st.columns(4)
        cols[0].metric("Latency", f"{result['latency_ms']}ms")
        cols[1].metric("Model", result.get("model", "llama3-70b"))
        cols[2].metric("Chaos", "ON 🔥" if result["chaos_active"] else "OFF")
        cols[3].metric("Guardrail", "⚠️ Hit" if result["guardrail_triggered"] else "✅ OK")

        if result.get("chaos_events"):
            with st.expander("🔥 Chaos Events"):
                for evt in result["chaos_events"]:
                    st.warning(f"[{evt['fault']}] {evt['description']}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "meta": result,
    })
