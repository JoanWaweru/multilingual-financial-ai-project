# Conversational AI Financial Advisor for Kenyans

A web-based conversational AI system designed to assist Kenyans with personal finance decisions, built as part of an MSc thesis in Data Science.

## Features

- **Multilingual Support**: English and Kiswahili with natural code-switching
- **RAG Pipeline**: Retrieval-Augmented Generation using Kenyan financial documents
- **Memory Management**: Short-term chat context and long-term user preferences
- **Financial Coverage**: SACCOs, banks, MMFs, Treasury Bills/Bonds, NSE stocks, pensions, budgeting
- **Regulatory Context**: Integration with CBK, CMA, and KRA guidelines

## Tech Stack

- **Frontend**: Next.js 14 (React)
- **Backend**: Python FastAPI
- **Vector DB**: FAISS
- **LLM**: Anthropic Claude
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Embeddings**: Local (sentence-transformers) by default; configurable

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose (optional)

### Using Docker (Recommended)

Set `ANTHROPIC_API_KEY` in your environment or in a `.env` file in the project root (the backend uses Anthropic Claude, not OpenAI). Then:

```bash
docker-compose up --build
```

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Testing the chatbot

1. **Ingest documents** (if the vector store is empty):  
   `cd backend && source venv/bin/activate && python -m scripts.ingest_documents`

2. **Quick pipeline check**:  
   `cd backend && python -m scripts.verify_chatbot`  
   This checks that the vector store is populated and runs a few RAG queries.

3. **Manual test**: Start backend and frontend, then ask financial questions (e.g. “What does CBK regulate?”, “How much does DPF insure?”). Answers should cite the ingested documents and avoid inventing figures.

## Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories:

**backend/.env**:
```
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=sqlite:///./database/financial_advisor.db
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=claude-sonnet-4-6
# Optional: MAX_CHAT_HISTORY=40  (how many recent messages the model sees; default 40)
```

**frontend/.env.local**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (e.g. Vercel frontend + hosted backend)

The chatbot needs a **populated vector store** to answer from your documents. Otherwise it will always respond with "I don't have verified information...".

- **If you deploy the backend with Docker** (Railway, Render, Fly.io, etc.): The Dockerfile runs document ingestion at **build time**, so the image includes the FAISS index. Redeploy so the new image is used.
- **If you deploy without Docker** (e.g. Render “Native Python”): The app runs ingestion automatically on startup when the vector store is empty (then reloads the index). First deploy may take 1–2 minutes.

Check that the store is loaded: **GET /health** returns `vector_store_documents` and `vector_store_index_size`. If both are 0, the chatbot will not have context to answer.

#### Deploying the backend on Render (from GitHub)

1. **Use Docker (recommended)**  
   - In Render: New → Web Service → connect your GitHub repo.  
   - Set **Root Directory** to `backend`.  
   - Render will detect the Dockerfile and build the image (ingestion runs at build time).  
   - Add env var **ANTHROPIC_API_KEY** (secret).  
   - Optional: use the repo’s **render.yaml** (Blueprint) so Root Directory and Docker are set automatically.

2. **Without Docker (Native Python)**  
   - Root Directory: `backend`.  
   - Build Command: `pip install -r requirements.txt`.  
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.  
   - Add **ANTHROPIC_API_KEY**.  
   - On first start the app will run document ingestion if the vector store is empty (may take 1–2 min).

3. **Frontend (Vercel)**  
   - Set **NEXT_PUBLIC_API_URL** to your Render backend URL (e.g. `https://kenyan-financial-ai-backend.onrender.com`).

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── data/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## License

Academic research project - University of Debrecen

