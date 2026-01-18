"""
Document management API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.services.vector_store import vector_store
from app.utils.document_processor import DocumentProcessor

router = APIRouter()

@router.get("/stats")
async def get_document_stats():
    """Get statistics about the document store"""
    stats = vector_store.get_stats()
    return stats

@router.post("/ingest")
async def ingest_documents(
    file: UploadFile = File(...)
):
    """Ingest a document into the vector store"""
    try:
        processor = DocumentProcessor()
        
        # Read file content
        content = await file.read()
        
        # Process document based on file type
        texts, metadata = await processor.process_file(
            content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Add to vector store
        await vector_store.add_documents(texts, metadata)
        
        return {
            "status": "success",
            "message": f"Processed {len(texts)} chunks from {file.filename}",
            "chunks": len(texts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@router.post("/search")
async def search_documents(query: str, k: int = 5):
    """Search documents in the vector store"""
    try:
        results = await vector_store.search(query, k=k)
        return {
            "query": query,
            "results": [
                {
                    "text": text[:500] + "..." if len(text) > 500 else text,
                    "metadata": metadata,
                    "similarity": 1.0 / (1.0 + distance)
                }
                for text, metadata, distance in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

