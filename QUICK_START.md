# Quick Start Guide (Without Docker)

Since Docker is not installed, follow these manual setup instructions.

## Prerequisites Check

✅ Python 3.9.6 - Installed  
✅ Node.js v24.10.0 - Installed  
❌ Docker - Not installed (using manual setup)

## Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/vector_store database

# Create .env file (you'll need to add your Claude API key)
cat > .env << EOF
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=sqlite:///./database/financial_advisor.db
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview
EOF

# Edit .env and add your actual Claude API key
# You can use: nano .env  or  open -e .env
```

## Step 2: Ingest Sample Documents

```bash
# Make sure you're in the backend directory with venv activated
python scripts/ingest_documents.py
```

You should see:
```
📚 Ingesting sample Kenyan financial documents...
✅ Ingested cbk_guidelines.txt: X chunks
✅ Ingested sacco_guide.txt: X chunks
...
✅ Document ingestion complete!
```

## Step 3: Start Backend Server

```bash
# Still in backend directory with venv activated
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Database initialized
✅ Application ready
```

Keep this terminal open!

## Step 4: Frontend Setup (New Terminal)

Open a **new terminal window** and:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend development server
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
- Local: http://localhost:3000
```

## Step 5: Access the Application

1. Open your browser and go to: **http://localhost:3000**
2. You should see the chat interface
3. Try asking: "What are SACCOs and how do they work?"

## Troubleshooting

### Backend won't start
- Make sure virtual environment is activated (`source venv/bin/activate`)
- Check that `.env` file exists and has your Claude API key
- Ensure port 8000 is not in use: `lsof -i :8000`

### Frontend won't start
- Make sure you ran `npm install` first
- Check that backend is running on port 8000
- Try deleting `node_modules` and `.next` folders, then `npm install` again

### "Module not found" errors
- Backend: Make sure venv is activated and you ran `pip install -r requirements.txt`
- Frontend: Make sure you ran `npm install`

### Claude API errors
- Verify your API key is correct in `backend/.env`
- Check you have credits in your Claude account
- Try a simple test: `curl https://api.anthropic.com/v1/messages -H "x-api-key: YOUR_KEY"`

## Quick Test

Once both servers are running:

1. Backend API docs: http://localhost:8000/docs
2. Frontend: http://localhost:3000
3. Try these questions:
   - "What are SACCOs?"
   - "Explain Treasury Bills in Kenya"
   - "Nisaidie kuhusu bajeti" (Kiswahili)

## Stopping the Servers

- Backend: Press `Ctrl+C` in the backend terminal
- Frontend: Press `Ctrl+C` in the frontend terminal

## Next Time You Run

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

That's it! The system should be running now.

