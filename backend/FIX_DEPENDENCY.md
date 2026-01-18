# Fix for sentence-transformers Dependency Issue

You're encountering a version incompatibility between `sentence-transformers==2.2.2` and the installed `huggingface_hub` version.

## Quick Fix

Update sentence-transformers to a newer version:

```bash
cd backend
source venv/bin/activate
pip install --upgrade sentence-transformers
```

This will install a compatible version that works with the current `huggingface_hub`.

## Alternative: Reinstall All Dependencies

```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## What Changed

I've updated `requirements.txt` to use `sentence-transformers>=2.7.0` which is compatible with newer versions of `huggingface_hub`.

After upgrading, run the ingestion script again:

```bash
python scripts/ingest_documents.py
```

This should resolve the `cached_download` import error.

