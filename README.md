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
- **Embeddings**: Claude text-embedding-3-small

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose (optional)

### Using Docker (Recommended)

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

## Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories:

**backend/.env**:
```
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=sqlite:///./financial_advisor.db
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=claude-3-5-sonnet-20240620
```

**frontend/.env.local**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

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

