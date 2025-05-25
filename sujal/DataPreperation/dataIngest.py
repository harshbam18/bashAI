from langchain_community.document_loaders import PyPDFium2Loader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(file_path):
    loader = PyPDFium2Loader(file_path)
    documents = loader.load()
    return documents

def split_documents(documents, chunk_size=50, chunk_overlap=10):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    split_docs = text_splitter.split_documents(documents)
    return split_docs
