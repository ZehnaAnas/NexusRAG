from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

contextualize_q_system_prompt = (
    "Given the chat history and the user's latest message, rewrite it "
    "as a single standalone search query that can be understood without "
    "the chat history.\n\n"
    "Rules:\n"
    "- Do NOT answer the question.\n"
    "- Resolve pronouns and references using the chat history "
    "(e.g. 'what about the deadline for it?' -> 'submission deadline "
    "for the Designathon').\n"
    "- Keep the user's own keywords and terminology; they usually match "
    "the wording in the source document.\n"
    "- If the message is already standalone, return it unchanged.\n"
    "- Output only the query text, nothing else."
)
history_prompt = ChatPromptTemplate.from_messages(
    [("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human","{input}")
    ]
)