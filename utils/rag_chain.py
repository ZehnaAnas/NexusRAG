from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_classic.retrievers import EnsembleRetriever,ContextualCompressionRetriever
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_cohere import CohereRerank
from utils.llm import llm
from utils.prompts import prompt
from utils.vectorstore import get_embeddings
from utils.config import SEARCH_TYPE,TOPK,VECTORSTORE_DIR,UPLOAD_DIR
from utils.db import DB_PATH
from utils.keywordstore import keyword_store
from utils.history_prompt import history_prompt
from utils.loaders import file_loader
import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()
store = {}

co = os.getenv("COHERE_API_KEY")
if not co:
    raise ValueError("API key not found!")
api_key = SecretStr(co)

# --- The cache ---
# Keyed by file_name. Holds a fully-built conversational chain so we 
# never repeat the expensive load -> split -> index -> rerank -> chain
# build work for the same file twice.
# Safe to keep as a plain dict (see the lesson): if the server restarts,
# this is empty again, but NOTHING is LOST - the next 
# question for that file just pays the build cost once more and
# re-populates the cache. Compare that to store = {} for chat_history,
# where restarting genuinely erased conversations.

_chain_cache: dict[str,RunnableWithMessageHistory] ={}

def get_session_id(session_id:str)-> BaseChatMessageHistory:
    # Before: store[session_id] = ChatMessageHistory() kept every
    # conversation in a plain dict — gone on restart.
    #
    # Now: SQLChatMessageHistory writes each message straight to the
    # same SQLite file our file_uploads table lives in. It reuses
    # the four operations from the lesson (create table, insert,
    # select) internally — LangChain just did the SQL for us.
    
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite://{DB_PATH}"
    )

def _build_chain(file_name):
    """
    This is the expensive part: reload, re-split, rebuild BM25,
    rebuild the reranker, rebuild the whole chain. Same logic as
    before - the only difference is WHO calls this and HOW OFTEN.
    Previously: every single question. Now: only on a cache miss.
    """

    vs = Chroma(
        embedding_function=get_embeddings(),
        persist_directory=f"{VECTORSTORE_DIR}/{file_name}"
        )
    
    vs_retriever = vs.as_retriever(
        search_type = SEARCH_TYPE,
        search_kwargs={"k":TOPK}
        )

    path = os.path.join(str(UPLOAD_DIR),file_name)
    with open (path,"rb") as file:
        docs = file.read()
    chunks = file_loader(file_name,docs)

    keyword_retriever = keyword_store(chunks)
    hybrid_retriever = EnsembleRetriever(retrievers=[vs_retriever,keyword_retriever],weights=[0.5,0.5])
    compressor = CohereRerank(cohere_api_key=api_key,model="rerank-english-v3.0")
    rerank_retriever = ContextualCompressionRetriever(base_compressor=compressor,base_retriever=hybrid_retriever)

    qa_chain = create_stuff_documents_chain(llm,prompt)
    history_aware_retriever = create_history_aware_retriever(llm,rerank_retriever,history_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever,qa_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_id,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    return conversational_rag_chain

def get_chain(file_name):
    """
    The memoization wrapper. This is the ONLY function the rest of
    the app should call to get a chain for a file - nobody outside
    this file should call _build_chain directly.
    """
    if file_name not in _chain_cache:
        _chain_cache[file_name] = _build_chain(file_name)
    return _chain_cache[file_name]

def invalidate_chain(file_name):
    """
    Call this whenever a file gets (re)processed, so a stale cached
    chain built from an old version can never be served again.
    .pop(key,None) removes the entry if present and does nothing 
    (no error) if it was never cached - safe either way.
    """
    _chain_cache.pop(file_name,None)

def ask_question(query,file_name):
    question = get_chain(file_name)
    answer = question.invoke({"input":query},config={"configurable":{"session_id":"101"}})
    return answer["answer"]


