# NexusRAG

> **Production-oriented Retrieval-Augmented Generation (RAG) platform for intelligent document retrieval, conversational querying, and grounded AI responses.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C)
![Chroma](https://img.shields.io/badge/VectorDB-Chroma-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)

---

## 🧠 Overview

**NexusRAG** is a modular RAG system engineered beyond a basic *"chat with PDF"* implementation.

It combines **dense semantic retrieval, BM25 lexical search, ensemble retrieval, neural reranking, history-aware query contextualization, persistent conversation memory, and grounded generation** into a single retrieval pipeline.

The backend also incorporates production-oriented concerns including **API-key authentication, owner-scoped document isolation, upload validation, background processing, request correlation, structured logging, caching, and Docker-based deployment**.

---

## ⚡ Architecture

```text
                    DOCUMENT
                       │
                       ▼
              ┌─────────────────┐
              │  Unstructured   │
              │  Document Parse │
              └────────┬────────┘
                       │
                       ▼
              Token-Aware Chunking
              1000 tokens / 200 overlap
                       │
              ┌────────┴────────┐
              ▼                 ▼
       OpenAI Embeddings      BM25
              │                 │
              ▼                 ▼
           Chroma        Sparse Retrieval
              │                 │
              └────────┬────────┘
                       ▼
              Ensemble Retrieval
                0.5 / 0.5
                       │
                       ▼
                Cohere Rerank
                    Top-6
                       │
                       ▼
             History-Aware RAG
                       │
                       ▼
                GPT-4o-mini
                       │
                       ▼
              Grounded Response
              + Source Metadata
```

---

## 🔬 Retrieval Engineering

### Hybrid Retrieval

NexusRAG combines:

* **Dense retrieval** using OpenAI `text-embedding-3-small`
* **Sparse retrieval** using BM25
* **Weighted ensemble retrieval** using LangChain
* **Cohere neural reranking**

The retrieval pipeline operates in multiple stages:

```text
Query
 ↓
Dense + Sparse Retrieval
 ↓
Candidate Fusion
 ↓
Cohere Reranking
 ↓
Top-K Context
 ↓
LLM
```

Current retrieval configuration:

```text
RETRIEVE_K = 20
TOPK       = 6
```

This allows semantic similarity and exact lexical matching to complement each other before the final context is passed to the LLM.

---

## 🧠 Conversational RAG

NexusRAG implements **history-aware retrieval** rather than treating every query independently.

```text
Conversation History
        ↓
Query Contextualization
        ↓
Standalone Search Query
        ↓
Hybrid Retrieval
        ↓
Reranking
        ↓
Grounded Generation
```

Conversation state is persisted using **LangChain's `SQLChatMessageHistory` backed by SQLite**, allowing sessions to survive process restarts.

---

## 🧩 Intelligent Document Processing

Documents are processed using **Unstructured** and split using a token-aware recursive chunking strategy.

```text
CHUNK_SIZE    = 1000 tokens
CHUNK_OVERLAP = 200 tokens
```

`tiktoken` with `cl100k_base` is used to measure token length, providing more predictable context sizing than naive character-based splitting.

Document metadata is preserved throughout the retrieval pipeline to enable source-aware responses.

---

## ⚡ Performance & Caching

RAG chains are cached in memory to avoid repeatedly constructing expensive retrieval pipelines.

```text
First request
     ↓
Build RAG Chain
     ↓
Cache
     ↓
Execute

Subsequent request
     ↓
Cached Chain
     ↓
Execute
```

Cache invalidation is triggered when a document is reprocessed, preventing stale retrieval chains.

Document indexing is also executed through **FastAPI background tasks**, allowing uploads to return without blocking on the complete indexing process.

---

## 🔐 Security

NexusRAG treats document uploads and API requests as untrusted input.

Implemented protections include:

* Cryptographically secure API-key generation
* SHA-256 API-key hashing
* Owner-scoped document access
* File extension allow-listing
* Filename sanitization
* Path traversal protection
* 20 MB upload limit
* Empty-file validation

Resource ownership is derived from authenticated API keys, preventing users from accessing another user's indexed documents.

---

## 📊 Observability

The API includes structured operational logging with:

* JSON-formatted logs
* Request correlation IDs
* Request duration tracking
* Document processing timing
* Error trace capture
* Privacy-aware logging

Example:

```json
{
  "level": "INFO",
  "request_id": "a31c91ef",
  "owner": "user",
  "file_name": "document.pdf",
  "duration_ms": 428.3
}
```

---

## 🛠️ Tech Stack

### AI / RAG

* **LangChain** — RAG orchestration
* **OpenAI GPT-4o-mini** — Generation
* **OpenAI text-embedding-3-small** — Embeddings
* **Chroma** — Vector storage
* **BM25 / rank_bm25** — Sparse retrieval
* **Cohere Rerank** — Neural reranking
* **tiktoken** — Token-aware chunking
* **Unstructured** — Document parsing

### Backend

* **Python 3.11**
* **FastAPI**
* **Uvicorn**
* **Pydantic**
* **SQLite**

### Frontend

* **React**
* **Vite**
* **Tailwind CSS**

### Infrastructure

* **Docker**
* **Docker Compose**
* **Docker BuildKit**
* **Tesseract**
* **Poppler**
* **libmagic**

---

## 📁 Project Structure

```text
NexusRAG/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── main.jsx
│   └── package.json
│
├── utils/
│   ├── auth.py
│   ├── config.py
│   ├── db.py
│   ├── history_prompt.py
│   ├── keywordstore.py
│   ├── llm.py
│   ├── loaders.py
│   ├── logging.py
│   ├── prompts.py
│   ├── rag_chain.py
│   ├── validation.py
│   └── vectorstore.py
│
├── create_api_key.py
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── LICENSE
```

---

## 🚀 Getting Started

### Clone

```bash
git clone https://github.com/ZehnaAnas/NexusRAG.git
cd NexusRAG
```

### Backend

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key
UNSTRUCTURED_API_KEY=your_unstructured_api_key
```

Start the backend:

```bash
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

---

## 🔮 Roadmap

* [ ] PostgreSQL + Alembic migrations
* [ ] Redis distributed caching
* [ ] Celery/background worker architecture
* [ ] Streaming LLM responses
* [ ] RAGAS-based retrieval evaluation
* [ ] Retrieval precision/recall benchmarking
* [ ] Rate limiting
* [ ] Role-based access control
* [ ] Multi-user workspaces
* [ ] Cloud deployment
* [ ] Observability dashboard

---

## 📄 License

MIT License.

---

## 👨‍💻 Author

**Zehna Anas**

Focused on:

`AI Engineering` · `Generative AI` · `RAG Systems` · `Backend Engineering` · `Cloud`

---

> **NexusRAG — Engineering the retrieval layer between your data and your LLM.**


