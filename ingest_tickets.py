"""
Ingests data/tickets.db into the 'tickets' Chroma collection.
Run once: python ingest_tickets.py
"""
import os
import sqlite3
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "chroma_store"
COLLECTION = "tickets"
DB_PATH    = os.path.join("data", "tickets.db")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_ticket_documents(db_path: str) -> list[Document]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM tickets").fetchall()
    con.close()
    docs = []
    for r in rows:
        content = (f"Issue: {r['issue_type']}\n"
                   f"Description: {r['description']}\n"
                   f"Resolution: {r['resolution']}")
        docs.append(Document(
            page_content=content,
            metadata={"source": "ticket", "ticket_id": r["ticket_id"],
                      "category": r["category"], "status": r["status"]},
        ))
    return docs

def main():
    print("Loading tickets...")
    docs = load_ticket_documents(DB_PATH)
    print(f"  {len(docs)} tickets loaded.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    store = Chroma(collection_name=COLLECTION, embedding_function=embeddings,
                   persist_directory=CHROMA_DIR)
    store.reset_collection()
    store.add_documents(docs)
    print(f"  Done. {store._collection.count()} vectors stored.")

if __name__ == "__main__":
    main()
