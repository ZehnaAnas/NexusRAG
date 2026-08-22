from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.config import CHUNK_SIZE,CHUNK_OVERLAP,EMBEDDING_MODEL,VECTORSTORE_DIR
from dotenv import load_dotenv
from pydantic import SecretStr
import os
import tiktoken
from unstructured.chunking.title import chunk_by_title
from pathlib import Path
load_dotenv()

def token_length(file):
    tokeniser = tiktoken.get_encoding(encoding_name="cl100k_base")
    tokens = tokeniser.encode(file)
    token_len = len(tokens)
    return token_len

def get_embeddings():
    client = os.getenv("OPENAI_API_KEY")
    if not client:
        raise ValueError("API KEY not found")
    api_key = SecretStr(client)
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,api_key=api_key
    )
    return embeddings

def split_text(file,file_name):
    section = chunk_by_title(file)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        length_function = token_length,
        separators=["\n\n","\n"," ",""]
    )
    documents = [
        Document(
            page_content=element.text,
            metadata=dict(element.metadata.to_dict()) if element.metadata else {},
        )
        for element in section
    ]
    chunks = text_splitter.split_documents(documents)
    for chunk in chunks:
        print(chunk.metadata)
        chunk.metadata["document_id"] = Path(file_name).stem
        chunk.metadata["filename"] = file_name
    return chunks

def create_vectorstore(file,file_name):
    docs = Path(file_name).stem
    vs = Chroma.from_documents(
        documents=split_text(file,file_name),
        embedding=get_embeddings(),
        persist_directory=f"{VECTORSTORE_DIR}/{docs}"
    )
    return vs