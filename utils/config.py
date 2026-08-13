from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR/"data"
UPLOAD_DIR = DATA_DIR/"uploads"
VECTORSTORE_DIR = DATA_DIR/"vectorstores"

UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True,exist_ok=True)

LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
SEARCH_TYPE = "similarity"
TOPK = 3
TEMPERATURE = 0
MAX_NEW_TOKENS = 200

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

