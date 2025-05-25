import os
from pathlib import Path
from dataIngest import load_documents, split_documents
from dataPreprocess import chunk_embeddings

# Define input and output directories
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EMBEDDING_DIR = Path(__file__).resolve().parent.parent / "embeddings"

def main():
    all_documents = []
    print(f"[INFO] Reading PDFs from: {DATA_DIR}")

    # Loop over all PDF files in the data directory
    for pdf_file in DATA_DIR.glob("*.pdf"):
        print(f"[INFO] Loading: {pdf_file.name}")
        docs = load_documents(str(pdf_file))
        all_documents.extend(docs)

    print(f"[INFO] Total documents loaded: {len(all_documents)}")

    print(f"[INFO] Splitting documents...")
    chunks = split_documents(all_documents, chunk_size=300, chunk_overlap=50)
    print(f"[INFO] Total chunks created: {len(chunks)}")

    print(f"[INFO] Saving FAISS vectorstore to: {EMBEDDING_DIR}")
    EMBEDDING_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore = chunk_embeddings(chunks, save_dir=str(EMBEDDING_DIR))

    if vectorstore:
        print("[SUCCESS] Vectorstore saved successfully.")
    else:
        print("[FAILURE] Vectorstore creation failed.")

if __name__ == "__main__":
    main()
