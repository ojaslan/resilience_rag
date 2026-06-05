import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from chaos.engine import ChaosEngine
from chaos.faults.latency import inject_latency
from chaos.faults.bad_data import corrupt_documents
from chaos.faults.api_failure import maybe_raise_api_error, SimulatedAPIError
from langchain.schema import Document

st.set_page_config(page_title="Chaos Panel | ResilienceAI", page_icon="💥", layout="wide")

st.title("💥 Chaos Engineering Control Panel")
st.markdown("Inject faults and observe how the system responds.")

if "chaos" not in st.session_state:
    st.session_state.chaos = ChaosEngine()

chaos: ChaosEngine = st.session_state.chaos

# --- Status ---
col1, col2 = st.columns(2)
col1.metric("Chaos Status", "🔥 ENABLED" if chaos.enabled else "🟢 DISABLED")
col2.metric("Active Faults", ", ".join(chaos.active_faults) or "none")

st.markdown("---")

# --- Individual Fault Tests ---
st.subheader("🧪 Manual Fault Injection")

tab1, tab2, tab3 = st.tabs(["⏱️ Latency", "💾 Bad Data", "❌ API Failure"])

with tab1:
    st.markdown("Simulate slow API responses.")
    min_d = st.slider("Min delay (s)", 0.1, 5.0, 1.0)
    max_d = st.slider("Max delay (s)", 1.0, 10.0, 3.0)
    prob = st.slider("Probability", 0.0, 1.0, 1.0)
    if st.button("Inject Latency Now"):
        with st.spinner("Injecting latency..."):
            inject_latency({"min_delay": min_d, "max_delay": max_d, "probability": prob})
        st.success("✅ Latency injected successfully! System handled it.")

with tab2:
    st.markdown("Corrupt retrieved documents from the knowledge base.")
    rate = st.slider("Corruption Rate", 0.0, 1.0, 0.5)
    mode = st.selectbox("Corruption Mode", ["append", "replace", "empty"])
    if st.button("Corrupt Documents"):
        sample_docs = [
            Document(page_content="This is a normal document.", metadata={"source": "test.pdf"}),
            Document(page_content="Another clean document.", metadata={"source": "test.pdf"}),
        ]
        from chaos.faults.bad_data import corrupt_documents
        corrupted = corrupt_documents(sample_docs, {"corruption_rate": rate, "mode": mode})
        st.subheader("Result:")
        for i, doc in enumerate(corrupted):
            st.text_area(f"Doc {i+1}", doc.page_content, height=80)

with tab3:
    st.markdown("Simulate LLM/API outage.")
    fail_prob = st.slider("Failure Probability", 0.0, 1.0, 0.5)
    if st.button("Trigger API Failure"):
        try:
            maybe_raise_api_error({"probability": fail_prob})
            st.success("✅ No failure this time (based on probability).")
        except SimulatedAPIError as e:
            st.error(f"💥 Simulated API Error: {e}")

st.markdown("---")

# --- Event Log ---
st.subheader("📋 Chaos Event Log")
log = chaos.get_log()
if log:
    for evt in reversed(log[-20:]):
        st.warning(f"[{evt['fault'].upper()}] {evt['description']} — {evt['timestamp']}")
    if st.button("Clear Log"):
        chaos.clear_log()
        st.rerun()
else:
    st.info("No chaos events recorded yet.")
