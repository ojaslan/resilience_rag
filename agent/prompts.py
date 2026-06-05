from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

RAG_SYSTEM_PROMPT = """You are ResilienceAI, a helpful and accurate assistant.
Answer the user's question using ONLY the context provided below.
If the context does not contain enough information, say so clearly.
Do not fabricate information.

Context:
{context}
"""

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", RAG_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

AGENT_SYSTEM_PROMPT = """You are ResilienceAI, an intelligent assistant with access to tools.
Use the retrieve_documents tool to search for relevant information before answering.
Always cite your sources. Be concise and factual.
"""

CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Given the conversation history and a follow-up question, rephrase the follow-up question to be standalone."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Follow-up question: {question}\nStandalone question:"),
])
