from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

history_prompt = ChatPromptTemplate.from_messages(
    [("system", "Using the previous conversation history, reformat and answer the users current question."),
    MessagesPlaceholder("chat_history"),
    ("human","{input}")
    ]
)