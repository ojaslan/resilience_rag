import streamlit as st
from typing import List, Dict


def render_chat_history(messages: List[Dict]):
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        meta = msg.get("meta", {})

        with st.chat_message(role):
            st.markdown(content)

            if role == "assistant" and meta:
                cols = st.columns(3)
                cols[0].metric("Latency", f"{meta.get('latency_ms', 0)}ms")
                cols[1].metric("Chaos", "ON 🔥" if meta.get("chaos_active") else "OFF")
                guardrail = meta.get("guardrail_triggered", False)
                cols[2].metric("Guardrail", "⚠️ Triggered" if guardrail else "✅ Passed")

                if meta.get("chaos_events"):
                    with st.expander("Chaos Events"):
                        for evt in meta["chaos_events"]:
                            st.warning(f"[{evt['fault']}] {evt['description']} @ {evt['timestamp']}")
