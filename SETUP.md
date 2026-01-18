# Setup Instructions

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- OpenAI API key

## Quick Start with Docker

1. **Clone and navigate to the project**
   ```bash
   cd "kenyan-financial-ai"
   ```

2. **Set up environment variables**
   
   Create `backend/.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=sqlite:///./database/financial_advisor.db
   EMBEDDING_MODEL=text-embedding-3-small
   LLM_MODEL=gpt-4-turbo-preview
   ```
   
   Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Ingest sample documents** (in a new terminal)
   ```bash
   docker-compose exec backend python scripts/ingest_documents.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

5. **Create necessary directories**
   ```bash
   mkdir -p data/vector_store database
   ```

6. **Run the backend**
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

7. **Ingest sample documents** (in a new terminal)
   ```bash
   cd backend
   source venv/bin/activate
   python scripts/ingest_documents.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local if needed
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Testing the System

1. **Start both backend and frontend**

2. **Open http://localhost:3000 in your browser**

3. **Try sample questions:**
   - "What are SACCOs and how do they work?"
   - "Explain Treasury Bills in Kenya"
   - "How do I invest in the NSE?"
   - "What is the difference between a bank and a SACCO?"
   - "Nisaidie kuhusu bajeti ya kibinafsi" (Kiswahili)

4. **Test multilingual support:**
   - Ask questions in English
   - Ask questions in Kiswahili
   - Mix both languages (code-switching)

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration and database
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic (RAG, LLM, Memory)
│   │   └── utils/        # Utility functions
│   ├── data/             # Document storage
│   ├── scripts/          # Utility scripts
│   └── main.py           # FastAPI application
├── frontend/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── lib/             # API client
│   └── types/           # TypeScript types
└── docker-compose.yml   # Docker configuration
```

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure virtual environment is activated
- **Database errors**: Check that database directory exists and is writable
- **OpenAI API errors**: Verify API key is correct and has credits
- **Vector store errors**: Run document ingestion script first

### Frontend Issues

- **API connection errors**: Check that backend is running on port 8000
- **Build errors**: Run `npm install` again
- **Type errors**: Check TypeScript configuration

### Docker Issues

- **Port conflicts**: Change ports in docker-compose.yml
- **Build failures**: Check Docker logs with `docker-compose logs`
- **Volume permissions**: Ensure directories are writable

## Next Steps

1. Add more Kenyan financial documents to the knowledge base
2. Fine-tune the LLM prompts for better responses
3. Implement user authentication (optional)
4. Add analytics and monitoring
5. Deploy to production (Vercel, Render, Railway, etc.)

## Support

For issues or questions, check the README.md or review the code documentation.

