from langchain_classic.retrievers import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from utils.llm import llm
from utils.prompts import prompt
from utils.vectorstore import get_embeddings
from utils.config import SEARCH_TYPE,TOPK,VECTORSTORE_DIR

def ragChain(file_name):

    vs = Chroma(
        embedding_function=get_embeddings(),
        persist_directory=f"{VECTORSTORE_DIR}/{file_name}"
        )
    
    vs_retriever = vs.as_retriever(
        search_type = SEARCH_TYPE,
        search_kwargs={"k":TOPK}
        )

    qa_chain = create_stuff_documents_chain(llm,prompt)
    rag_chain = create_retrieval_chain(vs_retriever,qa_chain)

    return rag_chain

def ask_question(query,file_name):
    question = ragChain(file_name)
    answer = question.invoke({"input":query})
    return answer


