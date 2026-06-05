import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from agent.memory import SessionMemory
from config.settings import settings

st.set_page_config(page_title="Monitor | ResilienceAI", page_icon="📊", layout="wide")
st.title("📊 System Monitor")
st.caption(f"Model: Groq / {settings.GROQ_MODEL}")

messages = st.session_state.get("messages", [])
assistant_msgs = [m for m in messages if m["role"] == "assistant"]

if not assistant_msgs:
    st.info("No conversations yet. Go to the Chat page and ask some questions!")
    st.stop()

rows = []
for i, m in enumerate(assistant_msgs):
    meta = m.get("meta", {})
    rows.append({
        "Turn": i + 1,
        "Latency (ms)": meta.get("latency_ms", 0),
        "Chaos Active": meta.get("chaos_active", False),
        "Guardrail Triggered": meta.get("guardrail_triggered", False),
        "Chaos Events": len(meta.get("chaos_events", [])),
    })

df = pd.DataFrame(rows)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Turns", len(df))
col2.metric("Avg Latency", f"{int(df['Latency (ms)'].mean())}ms")
col3.metric("Guardrails Hit", int(df["Guardrail Triggered"].sum()))
col4.metric("Chaos Events", int(df["Chaos Events"].sum()))

st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Response Latency per Turn")
    fig = px.bar(df, x="Turn", y="Latency (ms)", color_discrete_sequence=["#7F77DD"])
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Guardrail & Chaos Events")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["Turn"], y=df["Guardrail Triggered"].astype(int),
                              name="Guardrail", line=dict(color="#D85A30")))
    fig2.add_trace(go.Scatter(x=df["Turn"], y=df["Chaos Events"],
                              name="Chaos Events", line=dict(color="#EF9F27")))
    fig2.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Conversation Log")
st.dataframe(df, use_container_width=True)

st.subheader("Memory State")
sessions = SessionMemory.all_sessions()
if sessions:
    sel = st.selectbox("Session", sessions)
    history = SessionMemory.get_history(sel)
    for msg in history:
        role = getattr(msg, "type", "unknown")
        st.markdown(f"**{role.upper()}:** {msg.content}")
else:
    st.info("No session memory recorded.")
