from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

system_prompt = (
    "You are an intelligent RAG chatbot. Your job is to use the context only to answer the user's questions while also providing the citations using the metadata of the context and when answering and if not then just say that you don't know."
    "\n\n"
    "{context}"
    "{metadata}"
)

prompt = ChatPromptTemplate.from_messages(
    [
    ("system",system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human","{input}")
    ]
)