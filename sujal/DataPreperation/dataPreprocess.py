from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import dotenv

# Load environment variables from .env file 
dotenv.load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def chunk_embeddings(chunks, save_dir="faiss_index"):
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]

    try:
        vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
        vectorstore.save_local(save_dir)
        return vectorstore
    except Exception as e:
        print(f"Error creating FAISS vectorstore: {e}")
        return None
