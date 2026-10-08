"""
Ingests data/telecom_guide.pdf into the 'guide' Chroma collection.
Run once: python ingest_pdf.py
"""
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "chroma_store"
COLLECTION = "guide"
PDF_PATH   = os.path.join("data", "telecom_guide.pdf")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_guide_chunks(pdf_path: str) -> list[Document]:
    reader = PdfReader(pdf_path)
    pages = [
        Document(page_content=p.extract_text() or "",
                 metadata={"source": "guide", "page": i + 1})
        for i, p in enumerate(reader.pages)
    ]
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_documents(pages)

def main():
    print("Loading PDF...")
    chunks = load_guide_chunks(PDF_PATH)
    print(f"  {len(chunks)} chunks created.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    store = Chroma(collection_name=COLLECTION, embedding_function=embeddings,
                   persist_directory=CHROMA_DIR)
    store.reset_collection()   # no duplicates if you run it twice
    store.add_documents(chunks)
    print(f"  Done. {store._collection.count()} vectors stored.")

if __name__ == "__main__":
    main()
