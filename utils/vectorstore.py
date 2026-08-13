from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config import CHUNK_SIZE,CHUNK_OVERLAP,EMBEDDING_MODEL,VECTORSTORE_DIR
from dotenv import load_dotenv
from pydantic import SecretStr
import os
import tiktoken

load_dotenv()

def token_length(pdf):
    tokeniser = tiktoken.get_encoding(encoding_name="cl100k-base")
    tokens = tokeniser.encode(pdf)
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

def split_text(pdf):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        length_function = token_length,
        separators=["\n\n","\n"," ",""]
    )
    chunks = text_splitter.split_documents(pdf)
    return chunks

def create_vectorstore(pdf,pdf_name):
    file_name = pdf_name.removesuffix(".pdf")
    vs = Chroma.from_documents(
        documents=split_text(pdf),
        embedding=get_embeddings(),
        persist_directory=f"{VECTORSTORE_DIR}/{file_name}"
    )
    return vs