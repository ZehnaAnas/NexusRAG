from langchain_openai import ChatOpenAI
from utils.config import LLM_MODEL,TEMPERATURE,MAX_NEW_TOKENS
import os
from pydantic import SecretStr
from dotenv import load_dotenv
load_dotenv()

API_KEY = SecretStr(os.getenv("OPENAI_API_KEY") or "OPENAI API KEY not found")

llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=TEMPERATURE,
    api_key=API_KEY,
    max_completion_tokens=MAX_NEW_TOKENS
)

