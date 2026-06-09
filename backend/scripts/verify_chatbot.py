"""
Quick verification that the chatbot RAG pipeline answers correctly.
Run from backend directory: python -m scripts.verify_chatbot
Or: python scripts/verify_chatbot.py (with backend on PYTHONPATH)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.vector_store import vector_store
from app.services.rag_service import rag_service


async def main():
    print("Checking vector store...")
    stats = vector_store.get_stats()
    n = stats.get("total_documents", 0) or stats.get("index_size", 0)
    if n == 0:
        print(
            "⚠️  Vector store is empty. Run document ingestion first:\n"
            "   python -m scripts.ingest_documents\n"
            "Then run this script again."
        )
        return 1

    print(f"✅ Vector store has {n} chunks.\n")

    # Test queries that should be answerable from sample docs
    test_queries = [
        "What does CBK regulate?",
        "How much does the Deposit Protection Fund insure per depositor?",
        "What are Treasury Bills?",
    ]

    for q in test_queries:
        print(f"Q: {q}")
        try:
            out = await rag_service.retrieve_and_generate(q, chat_history=[], user_preferences=None)
            resp = out.get("response", "")
            docs = out.get("retrieved_documents", 0)
            sources = out.get("sources", [])
            conf = out.get("confidence", 0)
            print(f"   Documents used: {docs}  |  Confidence: {conf:.2f}")
            if sources:
                print(f"   Sources: {[s.get('source') for s in sources[:3]]}")
            print(f"   Response (first 200 chars): {resp[:200]}...")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            return 1

    print("✅ Chatbot pipeline is working. You can also test via the frontend or POST /api/chat/.")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
