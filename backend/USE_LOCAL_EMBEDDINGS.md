# Using Local Embeddings (No OpenAI API Required)

If you've exceeded your OpenAI API quota or want to test without API costs, you can use local embeddings instead.

## Option 1: Set Environment Variable

Add this to your `backend/.env` file:

```env
USE_LOCAL_EMBEDDINGS=true
```

Then run the ingestion script again. It will automatically use sentence-transformers (free, local) instead of OpenAI.

## Option 2: Force Local Mode in Code

The embedding service will automatically fall back to local embeddings if:
- OpenAI API quota is exceeded
- OpenAI API key is invalid
- `USE_LOCAL_EMBEDDINGS=true` is set

## What Changes

**Local Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Pros**: Free, no API calls, works offline
- **Cons**: Different dimensions (384 vs 1536), may have slightly different results

**OpenAI Model**: `text-embedding-3-small` (1536 dimensions)
- **Pros**: Higher quality, consistent dimensions
- **Cons**: Requires API key and credits

## Installation

The local embedding model (`sentence-transformers`) is already in `requirements.txt`.

The first time you use it, it will download the model (~80MB) - this only happens once.

## Recommendation for Thesis

For academic purposes and testing, local embeddings are perfectly fine. The RAG system will still work effectively with local embeddings.

## Switching Back

To use OpenAI embeddings again:
1. Remove or set `USE_LOCAL_EMBEDDINGS=false` in `.env`
2. Ensure your OpenAI API key is valid and has credits
3. Restart the application

## Current Status

The system will automatically detect OpenAI quota issues and switch to local embeddings, so you can continue testing even with API limitations.

