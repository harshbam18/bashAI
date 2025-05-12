from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OllamaEmbeddings(model="llama2")


def chunk_embeddings(chunks, save_dir="faiss_index"):
    """
    Generate embeddings for a list of document chunks and save them to FAISS.
    
    Args:
        chunks (list): A list of document objects to be embedded.
        save_dir (str): Directory to save the FAISS index.
    
    Returns:
        FAISS: The FAISS vector store containing the embeddings.
    """
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    try:
        vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
        vectorstore.save_local(save_dir)
        return vectorstore
    except Exception as e:
        print(f"Error creating FAISS vectorstore: {e}")
        return None
