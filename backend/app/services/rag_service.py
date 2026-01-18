"""
Retrieval-Augmented Generation (RAG) service
"""
from typing import List, Dict
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.core.config import settings

class RAGService:
    """Service for RAG pipeline"""
    
    async def retrieve_and_generate(
        self,
        query: str,
        chat_history: List[Dict] = None,
        user_preferences: Dict = None
    ) -> Dict:
        """
        Complete RAG pipeline: retrieve relevant documents and generate response
        """
        # Step 1: Retrieve relevant documents
        retrieved_docs = await vector_store.search(
            query,
            k=settings.top_k_retrieval
        )
        
        # Format retrieved context
        context = []
        for text, metadata, distance in retrieved_docs:
            context.append({
                'text': text,
                'metadata': metadata,
                'similarity_score': 1.0 / (1.0 + distance)  # Convert distance to similarity
            })
        
        # Step 2: Generate response using LLM with context
        response = await llm_service.generate_response(
            user_message=query,
            context=context,
            chat_history=chat_history,
            user_preferences=user_preferences
        )
        
        # Add RAG metadata
        response['retrieved_documents'] = len(context)
        response['sources'] = [
            {
                'source': doc['metadata'].get('source', 'Unknown'),
                'similarity': doc['similarity_score']
            }
            for doc in context
        ]
        
        return response
    
    async def retrieve_only(self, query: str, k: int = None) -> List[Dict]:
        """Retrieve documents without generating response"""
        k = k or settings.top_k_retrieval
        results = await vector_store.search(query, k=k)
        
        return [
            {
                'text': text,
                'metadata': metadata,
                'distance': distance,
                'similarity': 1.0 / (1.0 + distance)
            }
            for text, metadata, distance in results
        ]

rag_service = RAGService()

