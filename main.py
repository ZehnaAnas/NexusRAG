from fastapi import FastAPI,UploadFile,BackgroundTasks,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.loaders import file_loader
from utils.vectorstore import create_vectorstore
from utils.keywordstore import keyword
from utils.rag_chain import ask_question
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

file_status = {}

class QueryInfo(BaseModel):
    question:str
    file_name:str

@app.post("/")
async def root():
    return {"message":"SUCCESS"}

@app.post("/upload/file")
async def get_file(file:UploadFile,background_tasks:BackgroundTasks):
    try:
        file_name = str(file)
        contents = await file.read()
        file_status[file_name] = "processing"
        background_tasks.add_task(rag_process,contents,file_name)
        return {"message":file_name,"status":"processing"}
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

def rag_process(contents,file_name):
    try:
        file = file_loader(file_name,contents)
        if not file:
            file_status[file_name] = "Failed: no supported files found"
            return
        create_vectorstore(file,file_name)
        keyword(file)
        file_status[file_name] = "completed"
    except Exception as e:
        print(f"Error while trying to process {traceback.format_exc()}, Exception: {e}")

@app.get("/upload/status/{file_name}")
async def get_status(file_name:str):
    status = file_status.get(file_name,"unknown")
    return {"file_name":file_name,"status":status}

@app.get("/upload/question")
async def get_question(request:QueryInfo):
    try:
        answer = ask_question(request.question, request.file_name)
        return {"message": answer}
    except Exception as e:
        raise HTTPException(status_code=500,detail = e)

if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8000)