import streamlit as st
from chaos.engine import ChaosEngine
from config.settings import settings


def render_sidebar(chaos: ChaosEngine):
    with st.sidebar:
        st.title("⚙️ ResilienceAI")
        st.markdown(f"🚀 **Groq** — `{settings.GROQ_MODEL}`")
        st.markdown("---")

        st.subheader("🔥 Chaos Engineering")
        chaos_on = st.toggle("Enable Chaos", value=chaos.enabled)
        if chaos_on != chaos.enabled:
            chaos.enable() if chaos_on else chaos.disable()

        if chaos_on:
            faults = st.multiselect(
                "Active Faults",
                ["latency", "bad_data", "api_failure"],
                default=chaos.active_faults,
            )
            chaos.set_faults(faults)

        st.markdown("---")
        st.subheader("💬 Session")
        session_id = st.text_input("Session ID", value="default")

        if st.button("🗑️ Clear Memory"):
            from agent.memory import SimpleMemory
            SimpleMemory.clear(session_id)
            st.success("Memory cleared!")

        st.markdown("---")
        st.caption("ResilienceAI — Agentic AI with Groq")
        return session_id
