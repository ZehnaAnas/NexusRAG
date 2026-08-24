from fastapi import FastAPI,UploadFile,BackgroundTasks,HTTPException,Depends,Request
from fastapi.middleware.cors import CORSMiddleware
from utils.loaders import file_loader
from utils.vectorstore import create_vectorstore
from utils.keywordstore import keyword_store
from utils.rag_chain import ask_question, invalidate_chain
from utils.db import init_db, set_status, get_status as db_get_status
from utils.validation import validate_filename, validate_file_size, UploadValidationError
from utils.auth import get_current_owner, storage_key
from utils.logging import setup_logging, request_id_var
import logging
import time
import uuid
from pydantic import BaseModel
import uvicorn

# Do this before anything else runs, so even startup issues are logged
# through the same structured format.
setup_logging()
logger = logging.getLogger("nexusrag")

app = FastAPI(title="NexusRAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    """
    Runs before AND after every single request, for every endpoint —
    this is what gives every log line in this request the same
    request_id, and gives you one summary line per request for free
    (path, status code, how long it took) without adding logging
    calls to each route individually.
    """
    request_id = str(uuid.uuid4())[:8]
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "request completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(token)

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
    start = time.perf_counter()
    logger.info("processing started", extra={"owner": owner, "file_name": file_name})
    try:
        file = file_loader(key,contents)
        if not file:
            logger.warning(
                "processing failed: unsupported file type",
                extra={"owner": owner, "file_name": file_name},
            )
            set_status(owner, file_name, "failed", error="no supported files found")
            return
        create_vectorstore(file,key)
        keyword_store(file)
        invalidate_chain(key)
        set_status(owner, file_name, "completed")
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "processing completed",
            extra={"owner": owner, "file_name": file_name, "duration_ms": duration_ms},
        )
    except Exception as e:
        # exc_info=True attaches the full traceback to the JSON log
        # line (as an "exception" field) instead of printing it loose
        # to a terminal nobody's watching.
        logger.error(
            "processing failed",
            extra={"owner": owner, "file_name": file_name},
            exc_info=True,
        )
        set_status(owner, file_name, "failed", error=str(e))

@app.get("/upload/status/{file_name}")
async def get_status(file_name:str,owner:str=Depends(get_current_owner)):
    return db_get_status(owner, file_name)

@app.post("/upload/question")
async def get_question(request:QueryInfo,owner:str=Depends(get_current_owner)):
    start = time.perf_counter()
    try:
        key = storage_key(owner, request.file_name)
        answer = ask_question(request.question, key)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        # Deliberately NOT logging request.question or the answer text:
        # those are user content, potentially sensitive, and logging
        # them verbatim would mean anyone with log access can read
        # every conversation. Logging the LENGTH still lets you spot
        # patterns (e.g. "questions are timing out around 500 chars")
        # without capturing what was actually asked.
        logger.info(
            "question answered",
            extra={
                "owner": owner,
                "file_name": request.file_name,
                "question_length": len(request.question),
                "duration_ms": duration_ms,
            },
        )
        return {"message": answer}
    except Exception as e:
        logger.error(
            "question failed",
            extra={"owner": owner, "file_name": request.file_name},
            exc_info=True,
        )
        raise HTTPException(status_code=500,detail = str(e))

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)