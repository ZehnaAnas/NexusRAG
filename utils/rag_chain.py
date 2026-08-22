from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_classic.retrievers import EnsembleRetriever,ContextualCompressionRetriever
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_cohere import CohereRerank
from utils.llm import llm
from utils.prompts import prompt
from utils.vectorstore import get_embeddings
from utils.config import SEARCH_TYPE,TOPK,VECTORSTORE_DIR,UPLOAD_DIR
from utils.keywordstore import keyword
from utils.history_prompt import history_prompt
from utils.loaders import file_loader
import os
from dotenv import load_dotenv
from pydantic import SecretStr
from unstructured.chunking.title import chunk_by_title

load_dotenv()
store = {}

co = os.getenv("COHERE_API_KEY")
if not co:
    raise ValueError("API key not found!")
api_key = SecretStr(co)

def get_session_id(session_id:str)-> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def rag(file_name):

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

    keyword_retriever = keyword(chunks,file_name)
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

def ask_question(query,file_name):
    question = rag(file_name)
    answer = question.invoke({"input":query},config={"configurable":{"session_id":"101"}})
    return answer["answer"]


