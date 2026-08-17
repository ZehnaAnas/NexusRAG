# NexusRAG — Frontend

A React + Tailwind chat UI for your FastAPI RAG backend.

## 1. Backend fixes (required — see chat message for why)

In `NR/main.py`:

```python
# before
file_name = str(file)

# after
file_name = file.filename
```

```python
# before
@app.get("/upload/question")
async def get_question(request: QueryInfo):

# after
@app.post("/upload/question")
async def get_question(request: QueryInfo):
```

```python
# before
raise HTTPException(status_code=500, detail=e)

# after
raise HTTPException(status_code=500, detail=str(e))
```

In `NR/utils/rag_chain.py`, line 37, match the stripped name `create_vectorstore` actually persists under:

```python
# before
persist_directory=f"{VECTORSTORE_DIR}/{file_name}"

# after
persist_directory=f"{VECTORSTORE_DIR}/{file_name.removesuffix('.pdf')}"
```

## 2. Drop this folder in

Place this `nexusrag-frontend` folder next to your `NR` backend folder (as a sibling), so you have:

```
your-project/
├── NR/                  <- your FastAPI backend
└── nexusrag-frontend/   <- this folder
```

## 3. Install and run

```bash
cd nexusrag-frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). Your backend needs to already be running on `http://localhost:8000` (`python NR/main.py`), since CORS on the backend is already set to allow all origins.

## 4. If you deploy

Update `BASE_URL` in `src/api.js` to your deployed backend's URL.
