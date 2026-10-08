"""Tools the agent can call. The docstrings tell the model when to use each one."""
import os
import sqlite3
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "chroma_store"
DB_PATH = os.path.join("data", "tickets.db")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # same model as ingest

_emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

def _store(name: str) -> Chroma:
    return Chroma(collection_name=name, embedding_function=_emb,
                  persist_directory=CHROMA_DIR)

_faq, _guide, _tickets = _store("faq"), _store("guide"), _store("tickets")


@tool
def search_faq(query: str) -> str:
    """Search the FAQ for common customer questions about plans, billing,
    recharge, roaming and policies. Try this first for general questions."""
    docs = _faq.similarity_search(query, k=3)
    return "\n\n".join(
        f"[FAQ {d.metadata['faq_id']} | {d.metadata['category']}]\n{d.page_content}"
        for d in docs) or "No FAQ results."


@tool
def search_guide(query: str) -> str:
    """Search the telecom guide PDF for detailed troubleshooting steps and
    procedures. Use when the FAQ does not fully answer the question."""
    docs = _guide.similarity_search(query, k=3)
    return "\n\n".join(
        f"[Guide page {d.metadata['page']}]\n{d.page_content}"
        for d in docs) or "No guide results."


@tool
def search_similar_tickets(query: str) -> str:
    """Find past support tickets with a similar problem and see how they were
    resolved. Use for questions like 'has this happened before?'."""
    docs = _tickets.similarity_search(query, k=3)
    return "\n\n".join(
        f"[Ticket {d.metadata['ticket_id']} | {d.metadata['category']} | {d.metadata['status']}]\n{d.page_content}"
        for d in docs) or "No similar tickets."


@tool
def lookup_ticket(ticket_id: str) -> str:
    """Get one support ticket by its ID, for example 'TK-001'."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)  # read-only
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM tickets WHERE ticket_id = ?",
                      (ticket_id.strip().upper(),)).fetchone()
    con.close()
    if not row:
        return f"Ticket {ticket_id} not found."
    return "\n".join(f"{k}: {row[k]}" for k in row.keys())


ALL_TOOLS = [search_faq, search_guide, search_similar_tickets, lookup_ticket]
