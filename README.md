# Multilingual Financial AI — Kenyan Code-Switching Research

MSc Data Science thesis project (University of Debrecen): deep learning for English–Swahili code-switching in Kenyan financial communication, plus a production-style conversational advisor.

## What this repo contains

**Research & ML pipeline**

- Code-switching detection (fine-tuned multilingual BERT)
- Data acquisition, preprocessing, training, and evaluation
- Streamlit demo and rule-based `chatbot/` orchestrator with live NSE/CBK scrapers

**Full-stack web app** (`frontend/` + `backend/`)

- Next.js UI with auth, chat history, and user financial profiles (PostgreSQL)
- FastAPI + RAG over Kenyan financial documents (FAISS + Claude)
- Long-term preferences (goals, risk tolerance) stored per user

## Quick start (Docker — recommended)

```bash
cp .env.docker.example .env   # set ANTHROPIC_API_KEY
make up
# or: docker compose up --build
```

| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| API      | http://localhost:8000 |
| Health   | http://localhost:8000/health |

Postgres runs in Docker (`kfa` / `financial_advisor` on port 5432).

## Manual setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Set DATABASE_URL and ANTHROPIC_API_KEY in .env
python -m uvicorn main:app --reload --port 8000
```

Ingest documents if the vector store is empty:

```bash
python -m scripts.ingest_documents
python -m scripts.verify_chatbot
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`.

### Streamlit chatbot (research demo)

```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

## Environment variables

See `.env.docker.example` for Docker. For local backend, create `backend/.env`:

```
ANTHROPIC_API_KEY=your_key
DATABASE_URL=postgresql://kfa:kfa@localhost:5432/financial_advisor
LLM_MODEL=claude-sonnet-4-6
USE_LOCAL_EMBEDDINGS=true
AUTH_SECRET_KEY=change-me-in-production
```

## Project structure

```
.
├── backend/          # FastAPI, RAG, auth, Postgres models
├── frontend/         # Next.js app
├── chatbot/          # Thesis chatbot engine & scrapers
├── training/         # BERT training scripts
├── preprocessing/    # Dataset pipeline
├── streamlit_app/    # Streamlit UI
├── docker-compose.yml
└── Makefile
```

## Deployment notes

- **Vector store**: the chatbot needs ingested documents. Docker builds run ingestion; on bare-metal deploy, startup ingests if the store is empty. Check `GET /health` for `vector_store_documents`.
- **Render**: use `backend/Dockerfile`, set `ANTHROPIC_API_KEY`, point Vercel `NEXT_PUBLIC_API_URL` at the backend URL. See `render.yaml` if using Blueprint.

## License

Academic research project — University of Debrecen
