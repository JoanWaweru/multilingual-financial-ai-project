# Quick Fix for Claude Quota Error

You're getting a quota error because your Claude API key has exceeded its usage limit.

## Immediate Solution: Use Local Embeddings

The system now automatically supports local embeddings. Here's how to fix it:

### Step 1: Set Environment Variable

Edit `backend/.env` and add:

```env
USE_LOCAL_EMBEDDINGS=true
```

Or if you want to temporarily disable Claude key requirement:

```env
# Comment out or remove ANTHROPIC_API_KEY to force local mode
# ANTHROPIC_API_KEY=your_key_here
USE_LOCAL_EMBEDDINGS=true
```

### Step 2: Run Ingestion Again

```bash
cd backend
source venv/bin/activate
python scripts/ingest_documents.py
```

The system will now use sentence-transformers (local, free) instead of Claude.

## What Happens

- **First time**: It downloads the model (~80MB) - only once
- **After that**: All embeddings are generated locally, no API calls
- **RAG system**: Still works perfectly with local embeddings

## Alternative: Fix Claude Quota

If you want to use Claude embeddings:

1. Add credits to your Claude account: https://console.anthropic.com/settings/billing
2. Or wait for quota to reset (usually monthly)
3. Remove `USE_LOCAL_EMBEDDINGS=true` from `.env`

## For Thesis/Demo

Local embeddings are perfectly fine for academic purposes. The system will work identically, just with different embedding dimensions (384 vs 1536).

The RAG retrieval quality may be slightly different, but still effective for demonstration and testing.

