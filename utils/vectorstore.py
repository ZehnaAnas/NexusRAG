from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config import CHUNK_SIZE,CHUNK_OVERLAP,EMBEDDING_MODEL,VECTORSTORE_DIR
from dotenv import load_dotenv
from pydantic import SecretStr
import os
import tiktoken

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

def split_text(file):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        length_function = token_length,
        separators=["\n\n","\n"," ",""]
    )
    chunks = text_splitter.split_documents(file)
    # Unstructured attaches rich per-chunk metadata (e.g. exact pixel
    # coordinates on the page, as a nested dict) that Chroma refuses
    # to store -- it only accepts flat values (str/int/float/bool/
    # list/None) per metadata field. filter_complex_metadata() strips
    # out anything Chroma can't store, keeping the chunk TEXT intact
    # and only dropping metadata fields that were never usable for
    # retrieval anyway.
    chunks = filter_complex_metadata(chunks)
    return chunks

def create_vectorstore(file,file_name):
    vs = Chroma.from_documents(
        documents=split_text(file),
        embedding=get_embeddings(),
        persist_directory=f"{VECTORSTORE_DIR}/{file_name}"
    )
    return vs