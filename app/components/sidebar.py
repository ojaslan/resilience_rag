import streamlit as st
from chaos.engine import ChaosEngine
from config.settings import settings


def render_sidebar(chaos: ChaosEngine):
    with st.sidebar:
        st.title("⚙️ ResilienceAI")

        # Model info
        st.markdown(f"""
        <div style='background:#f0f2f6;border-radius:8px;padding:8px 12px;margin-bottom:8px'>
        <small>🚀 <b>Groq</b> — {settings.GROQ_MODEL}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Chaos controls
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
            preset = st.selectbox("Scenario Preset", ["custom", "light", "heavy"])
            if preset != "custom":
                st.info(f"Preset '{preset}' loaded from scenarios.yaml")

        st.markdown("---")

        # Session controls
        st.subheader("💬 Session")
        session_id = st.text_input("Session ID", value="default")

        if st.button("🗑️ Clear Memory"):
            from agent.memory import SessionMemory
            SessionMemory.clear(session_id)
            st.success("Memory cleared!")

        st.markdown("---")
        st.caption("ResilienceAI — Agentic AI with Groq")

        return session_id
