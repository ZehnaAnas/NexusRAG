from langchain_community.retrievers import BM25Retriever
from utils.vectorstore import split_text

def keyword(docs):
    chunks = split_text(docs)
    ks = BM25Retriever.from_documents(chunks)
    ks.k = 3
    return ks