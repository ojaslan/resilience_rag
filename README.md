# 🤖 ResilienceAI — Agentic AI with Groq + Guardrails + Chaos Engineering

A production-grade agentic AI system using **Groq** (llama3-70b), **LangChain**, **RAG**, **Guardrails**, **Chaos Engineering**, and **Streamlit**.

---


## 🐍 Python Version

This project was developed and tested using:

```bash
Python 3.12.0
```



```bash
## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  Input Guardrail │  ← blocks harmful/malformed input
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangChain Agent │  ← Groq LLM (llama3-70b-8192)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAG Retriever  │  ← ChromaDB + HuggingFace Embeddings
└────────┬────────┘
         │
    [Chaos Engine]   ← optionally injects faults here
         │
         ▼
┌─────────────────┐
│  Output Guardrail│  ← validates LLM response
└────────┬────────┘
         │
         ▼
    Final Answer
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone <your-repo>
cd ResilienceAI
pip install -r requirements.txt
```

### 2. Get Groq API Key
- Sign up free at https://console.groq.com
- Create an API key

### 3. Configure Environment
```bash
# Edit .env and add your GROQ_API_KEY
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
GROQ_MODEL=llama3-70b-8192
```

### 4. Add Documents
Place PDF or `.txt` files in `data/raw/`.

### 5. Ingest Documents
```python
from rag.ingestor import DocumentIngestor
from rag.embedder import VectorEmbedder

ingestor = DocumentIngestor()
chunks = ingestor.ingest()

embedder = VectorEmbedder()
embedder.build_store(chunks)
```

### 6. Run the App
```bash
streamlit run app/main.py
```

---

## 🧪 Run Tests
```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
ResilienceAI/
├── app/                   # Streamlit UI
│   ├── main.py            # Home page
│   ├── pages/
│   │   ├── 01_chat.py     # RAG Q&A chat (Groq powered)
│   │   ├── 02_chaos.py    # Chaos control panel
│   │   └── 03_monitor.py  # Metrics dashboard
│   └── components/
├── agent/                 # LangChain agent (Groq LLM)
├── rag/                   # RAG pipeline (HuggingFace embeddings)
├── guardrails/            # Input/output validation
├── chaos/                 # Fault injection engine
├── data/                  # Knowledge base documents
├── tests/                 # Unit tests
└── config/                # Settings
```

---

## 🚀 Groq Models Available

| Model | Context | Speed |
|---|---|---|
| `llama3-70b-8192` | 8192 tokens | ~330 tokens/s |
| `llama3-8b-8192` | 8192 tokens | ~1250 tokens/s |
| `mixtral-8x7b-32768` | 32768 tokens | ~575 tokens/s |
| `gemma-7b-it` | 8192 tokens | ~950 tokens/s |

Change model in `.env`: `GROQ_MODEL=mixtral-8x7b-32768`

---

## 💥 Chaos Engineering Modes

| Fault | Description |
|---|---|
| `latency` | Injects 1–6s artificial delay |
| `bad_data` | Corrupts retrieved documents |
| `api_failure` | Simulates Groq API outage (503, 429, timeout) |

---

## 🛡️ Guardrail Rules

Configured in `guardrails/rules.yaml`:
- **Input**: blocks prompt injection, too-long inputs, harmful patterns
- **Output**: detects empty responses, hallucination phrases, oversized outputs

---

## 🔧 Tech Stack

- **Groq** — Ultra-fast LLM inference (llama3-70b-8192)
- **LangChain** 0.2 — agent, tools, memory, chains
- **HuggingFace Sentence Transformers** — local embeddings (no cost)
- **ChromaDB** — vector store for RAG
- **Streamlit** 1.35 — interactive UI
- **Pydantic** v2 — output schema validation
- **Pytest** — unit testing
