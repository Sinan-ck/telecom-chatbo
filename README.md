# Telecom Support Agent

A RAG-based support agent that answers telecom questions from three data sources:
a FAQ (CSV), a telecom guide (PDF) and past support tickets (SQLite).
It uses ChromaDB for search, LangChain for the agent and a local Ollama model.

![Telecom Support Agent demo](docs/streamlit-demo.png)

## How it works
- `ingest_faq.py`, `ingest_pdf.py`, `ingest_tickets.py` load each source into ChromaDB
- `tools.py` has four tools: `search_faq`, `search_guide`, `search_similar_tickets`, `lookup_ticket`
- `agent.py` is the agent (terminal chat)
- `app.py` is the Streamlit web chat

## Run it
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b
python ingest_faq.py && python ingest_pdf.py && python ingest_tickets.py
streamlit run app.py
```
