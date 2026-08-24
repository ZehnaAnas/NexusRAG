from fastapi import FastAPI,UploadFile,BackgroundTasks,HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from utils.loaders import file_loader
from utils.vectorstore import create_vectorstore
from utils.keywordstore import keyword_store
from utils.rag_chain import ask_question, invalidate_chain
from utils.db import init_db, set_status, get_status as db_get_status
from utils.validation import validate_filename, validate_file_size, UploadValidationError
from utils.auth import get_current_owner, storage_key
import traceback
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="NexusRAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# Runs once when the app boots: makes sure the table exists.
# Safe to call every time — it won't erase existing data.
init_db()

class QueryInfo(BaseModel):
    question:str
    file_name:str

@app.get("/")
async def root():
    return {"message":"SUCCESS"}

@app.post("/upload/file")
async def get_file(file:UploadFile,background_tasks:BackgroundTasks,owner:str=Depends(get_current_owner)):
    contents = await file.read()

    try:
        safe_file_name = validate_filename(file.filename)
        validate_file_size(contents)
    except UploadValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # This is the only place storage_key() gets computed for uploads.
    # Everything past this point (rag_process, the loader, the
    # vectorstore, the chain cache) only ever sees `key` — a single
    # collision-proof string — never the raw owner/filename pair.
    key = storage_key(owner, safe_file_name)

    try:
        set_status(owner, safe_file_name, "processing")
        background_tasks.add_task(rag_process,contents,key,owner,safe_file_name)
        return {"message":safe_file_name,"status":"processing"}
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

def rag_process(contents,key,owner,file_name):
    try:
        file = file_loader(key,contents)
        if not file:
            set_status(owner, file_name, "failed", error="no supported files found")
            return
        create_vectorstore(file,key)
        keyword_store(file)
        invalidate_chain(key)
        set_status(owner, file_name, "completed")
    except Exception as e:
        print(f"Error while trying to process {traceback.format_exc()}, Exception: {e}")
        set_status(owner, file_name, "failed", error=str(e))

@app.get("/upload/status/{file_name}")
async def get_status(file_name:str,owner:str=Depends(get_current_owner)):
    return db_get_status(owner, file_name)

@app.post("/upload/question")
async def get_question(request:QueryInfo,owner:str=Depends(get_current_owner)):
    try:
        key = storage_key(owner, request.file_name)
        answer = ask_question(request.question, key)
        return {"message": answer}
    except Exception as e:
        raise HTTPException(status_code=500,detail = str(e))

if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8000)