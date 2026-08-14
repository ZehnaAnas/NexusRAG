from fastapi import FastAPI,UploadFile,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from utils.loaders import file_loader
from utils.vectorstore import create_vectorstore
from utils.rag_chain import ask_question
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

class QueryInfo(BaseModel):
    question:str
    file_name:str

@app.post("/")
async def root():
    return {"message":"SUCCESS"}

@app.post("/upload/file")
async def get_file(file:UploadFile,background_tasks:BackgroundTasks):
    file_name = str(file)
    contents = await file.read()
    background_tasks.add_task(rag_process,contents,file_name)
    return {"message":file_name}

def rag_process(contents,file_name):
    file = file_loader(file_name,contents)
    create_vectorstore(file,file_name)
    return {"message":"file processing"}

@app.get("/upload/question")
async def get_question(question: str, file_name: str):
    answer = ask_question(question, file_name)
    return {"message": answer}



if __name__ == "__main__":
    uvicorn.run(app,host="localhost",port=8000)