from fastapi import FastAPI,UploadFile,BackgroundTasks,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.loaders import file_loader
from utils.vectorstore import create_vectorstore
from utils.keywordstore import keyword
from utils.rag_chain import ask_question
from utils.db import init_db, set_status, get_status as db_get_status
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
# Safe to call every time - it won't erase existing data.

init_db()

class QueryInfo(BaseModel):
    question:str
    file_name:str

@app.get("/")
async def root():
    return {"message":"SUCCESS"}

@app.post("/upload/file")
async def get_file(file:UploadFile,background_tasks:BackgroundTasks):
    try:
        file_name = file.filename
        contents = await file.read()
        set_status(str(file_name),"processing")
        background_tasks.add_task(rag_process,contents,file_name)
        return {"message":file_name,"status":"processing"}
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

def rag_process(contents,file_name):
    try:
        file = file_loader(file_name,contents)
        if not file:
            set_status(file_name,"failed",error="Failed: no supported files found")
            return
        create_vectorstore(file,file_name)
        keyword(file)
        set_status(file_name, "completed")
    except Exception as e:
        print(f"Error while trying to process {traceback.format_exc()}, Exception: {e}")
        set_status(file_name,"failed",error=str(e))

@app.get("/upload/status/{file_name}")
async def get_status(file_name:str):
    return db_get_status(file_name)

@app.post("/upload/question")
async def get_question(request:QueryInfo):
    try:
        answer = ask_question(request.question, request.file_name)
        return {"message": answer}
    except Exception as e:
        raise HTTPException(status_code=500,detail = str(e))

if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8000)