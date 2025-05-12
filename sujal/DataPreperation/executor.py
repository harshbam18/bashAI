import os
import time
import logging
from dataIngest import load_documents, split_documents
from dataPreprocess import chunk_embeddings
from langchain_community.vectorstores import FAISS 
from langchain_ollama import OllamaEmbeddings

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def get_pdf_files(directory):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(".pdf")
    ]

if __name__ == "__main__":
    start_time = time.time()
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(base_dir, "../data"))
    embeddings_dir = os.path.abspath(os.path.join(base_dir, "../../embeddings"))

    os.makedirs(embeddings_dir, exist_ok=True)
    pdf_files = get_pdf_files(data_dir)

    if not pdf_files:
        log.warning(f"No PDF files found in {data_dir}. Exiting.")
        exit(0)

    all_documents = []
    for pdf_file in pdf_files:
        try:
            docs = load_documents(pdf_file)
            all_documents.extend(docs)
            log.info(f"Loaded {len(docs)} pages from {pdf_file}")
        except Exception as e:
            log.warning(f"Failed to load {pdf_file}: {e}")

    if not all_documents:
        log.warning("No valid documents were loaded. Exiting.")
        exit(0)

    chunks = split_documents(all_documents)
    log.info(f"Split into {len(chunks)} chunks.")

    index_path = os.path.join(embeddings_dir, "index.faiss")
    if os.path.exists(index_path):
        log.info("Loading existing FAISS index...")
        embeddings = OllamaEmbeddings(model="llama2")
        vectorstore = FAISS.load_local(embeddings_dir, embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = chunk_embeddings(chunks, save_dir=embeddings_dir)
        log.info("FAISS index created and saved.")

    log.info(f"Processed {len(pdf_files)} PDFs, {len(all_documents)} documents, {len(chunks)} chunks.")
    log.info(f"Total execution time: {time.time() - start_time:.2f} seconds")