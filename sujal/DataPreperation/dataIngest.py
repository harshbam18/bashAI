from langchain_community.document_loaders import PyPDFium2Loader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(file_path):
    """
    Load documents from a given file path using PyPDFium2Loader.
    
    Args:
        file_path (str): The path to the document file.
        
    Returns:
        list: A list of loaded documents.
    """
    loader = PyPDFium2Loader(file_path)
    documents = loader.load()
    return documents

def split_documents(documents, chunk_size=50, chunk_overlap=10):
    """
    Split documents into smaller chunks using RecursiveCharacterTextSplitter.
    
    Args:
        documents (list): A list of documents to be split.
        chunk_size (int): The size of each chunk.
        chunk_overlap (int): The overlap between chunks.
        
    Returns:
        list: A list of split document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    split_docs = text_splitter.split_documents(documents)
    return split_docs
