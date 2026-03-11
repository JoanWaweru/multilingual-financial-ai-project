"""
Vector store service using FAISS for document retrieval
"""
import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict
from app.services.embedding_service import embedding_service
from app.core.config import settings

class VectorStore:
    """FAISS-based vector store for document retrieval"""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = None
        self.documents = []  # Store document metadata
        self.store_path = settings.vector_db_path
        os.makedirs(self.store_path, exist_ok=True)
        self.index_path = os.path.join(self.store_path, "faiss.index")
        self.metadata_path = os.path.join(self.store_path, "metadata.pkl")
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.documents = pickle.load(f)
                # Ensure index dimension matches current embedding model (e.g. after switching local vs API)
                if self.index.d != self.dimension:
                    print(
                        f"⚠️ Index dimension ({self.index.d}) does not match embedding dimension ({self.dimension}). "
                        "Creating new index. Re-run document ingestion to populate."
                    )
                    self._create_new_index()
                else:
                    print(f"✅ Loaded vector store with {len(self.documents)} documents")
            except Exception as e:
                print(f"⚠️ Error loading index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()

    def reload_from_disk(self):
        """Reload index and metadata from disk (e.g. after another process ran ingestion)."""
        self._load_or_create_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        print("✅ Created new vector store index")
    
    async def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """Add documents to the vector store"""
        if not texts:
            return
        
        # Generate embeddings
        embeddings = await embedding_service.embed_batch(texts)
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store metadata
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            self.documents.append({
                'text': text,
                'metadata': metadata
            })
        
        self._save_index()
        print(f"✅ Added {len(texts)} documents to vector store")
    
    async def search(self, query: str, k: int = 5) -> List[Tuple[str, Dict, float]]:
        """Search for similar documents"""
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        # Return results with metadata
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append((
                    doc['text'],
                    doc['metadata'],
                    float(distance)
                ))
        
        return results
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)
        except Exception as e:
            print(f"⚠️ Error saving index: {e}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'dimension': self.dimension
        }

# Initialize vector store
vector_store = VectorStore(dimension=embedding_service.get_embedding_dimension())

