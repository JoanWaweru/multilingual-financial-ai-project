"""
Retrieval-Augmented Generation (RAG) service
"""
from typing import List, Dict
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.services.market_data_service import market_data_service
from app.core.config import settings
from app.utils.language_detection import detect_language_style

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
        
        if settings.min_context_similarity and settings.min_context_similarity > 0:
            context = [
                item for item in context
                if item['similarity_score'] >= settings.min_context_similarity
            ]

        # Add live market snapshot when query is market-related
        if self._is_market_query(query):
            market_snapshot = await market_data_service.get_market_snapshot(query)
            if market_snapshot:
                context.append({
                    'text': market_snapshot,
                    'metadata': {'source': 'NSE live market data'},
                    'similarity_score': 1.0
                })
                if "not individual share prices" in market_snapshot:
                    context.append({
                        'text': (
                            "Live share gainers/losers are not available right now. "
                            "Suggest checking the NSE website or a licensed broker for today’s top movers. "
                            "Offer to help compare specific shares if the user names them."
                        ),
                        'metadata': {'source': 'Market data fallback guidance'},
                        'similarity_score': 0.9
                    })
        
        if settings.require_citations and not context:
            return {
                "response": self._no_verified_info_message(query),
                "confidence": 0.2,
                "retrieved_documents": 0,
                "sources": [],
                "evidence": []
            }

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
        response['evidence'] = [
            {
                'text': doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text'],
                'source': doc['metadata'].get('source', 'Unknown'),
                'similarity': doc['similarity_score']
            }
            for doc in context
        ]
        
        return response

    def _no_verified_info_message(self, query: str) -> str:
        style = detect_language_style(query)
        if style == "kiswahili":
            return (
                "Samahani, sina taarifa zilizothibitishwa za kujibu swali hilo kwa sasa. "
                "Tafadhali toa chanzo au uliza kuhusu jambo lililo kwenye nyaraka zilizopo."
            )
        if style == "code-switch":
            return (
                "I don't have verified information to answer that right now. "
                "Tafadhali toa chanzo au uliza kuhusu jambo lililo kwenye nyaraka zilizopo."
            )
        return (
            "I don't have verified information to answer that right now. "
            "Please provide a source or ask about something covered in the available documents."
        )


    def _is_market_query(self, query: str) -> bool:
        q = query.lower()
        keywords = [
            "nse", "shares", "stocks", "equity", "equities", "stock", "share",
            "price", "market", "gainers", "losers", "dividend", "ticker"
        ]
        return any(k in q for k in keywords)
    
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

