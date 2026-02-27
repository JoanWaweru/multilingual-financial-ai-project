"""
Embedding service for generating vector embeddings
"""
from app.core.config import settings
import numpy as np
from typing import List, Union
import os

# Try to use local embeddings as fallback
LOCAL_EMBEDDINGS_AVAILABLE = False
SentenceTransformer = None
try:
    from sentence_transformers import SentenceTransformer
    LOCAL_EMBEDDINGS_AVAILABLE = True
except ImportError as e:
    LOCAL_EMBEDDINGS_AVAILABLE = False
    print(f"Note: sentence-transformers import failed: {e}")
except Exception as e:
    LOCAL_EMBEDDINGS_AVAILABLE = False
    print(f"Note: sentence-transformers initialization failed: {e}")

class EmbeddingService:
    """Service for generating text embeddings with local fallback"""
    
    def __init__(self):
        self.model = settings.embedding_model
        self.use_local = settings.use_local_embeddings
        self.local_model = None
        if not self.use_local:
            print("ℹ️ Embeddings are configured for local mode.")
            self.use_local = True
        
        # Initialize local model if needed
        if self.use_local:
            # Try to import sentence-transformers if not already available
            if not LOCAL_EMBEDDINGS_AVAILABLE:
                try:
                    from sentence_transformers import SentenceTransformer as ST
                    # Update the module-level variables
                    globals()['LOCAL_EMBEDDINGS_AVAILABLE'] = True
                    globals()['SentenceTransformer'] = ST
                    print("✅ sentence-transformers imported successfully")
                except Exception as e:
                    print(f"⚠️ Warning: sentence-transformers not available: {e}")
                    print("   Install it with: pip install sentence-transformers")
                    return
            
            # Check if SentenceTransformer is available
            st_class = globals().get('SentenceTransformer', None)
            if LOCAL_EMBEDDINGS_AVAILABLE and st_class:
                try:
                    # Use a lightweight multilingual model
                    print("📦 Loading local embedding model (first time may take a while)...")
                    st_class = globals().get('SentenceTransformer', None)
                    if st_class:
                        self.local_model = st_class('all-MiniLM-L6-v2')
                        print("✅ Local embedding model loaded")
                except Exception as e:
                    print(f"⚠️ Warning: Could not load local model: {e}")
                    print(f"   Error details: {type(e).__name__}: {str(e)}")
            else:
                print("⚠️ Warning: sentence-transformers not available. Install it with: pip install sentence-transformers")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        # Use local embeddings if enabled
        if self.use_local:
            if not self.local_model:
                st_class = globals().get('SentenceTransformer', None)
                if st_class and LOCAL_EMBEDDINGS_AVAILABLE:
                    print("📦 Loading local embedding model...")
                    self.local_model = st_class('all-MiniLM-L6-v2')
            if self.local_model:
                return self._embed_local([text])[0]
        
        if self.local_model:
            return self._embed_local([text])[0]
        raise ValueError("No embedding service available (local embeddings not initialized)")
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        # Use local embeddings if enabled
        if self.use_local:
            # Ensure sentence-transformers is available
            st_class = globals().get('SentenceTransformer', None)
            if not LOCAL_EMBEDDINGS_AVAILABLE or not st_class:
                try:
                    from sentence_transformers import SentenceTransformer as ST
                    globals()['LOCAL_EMBEDDINGS_AVAILABLE'] = True
                    globals()['SentenceTransformer'] = ST
                    st_class = ST
                except Exception as e:
                    raise ValueError(f"Local embeddings requested but sentence-transformers is not available: {e}. Run: pip install sentence-transformers")
            
            if not self.local_model:
                try:
                    print("📦 Loading local embedding model...")
                    self.local_model = st_class('all-MiniLM-L6-v2')
                    print("✅ Local model loaded")
                except Exception as e:
                    print(f"❌ Failed to load local model: {e}")
                    raise ValueError(f"Could not load local embedding model: {e}")
            return self._embed_local(texts)
        
        if self.local_model:
            return self._embed_local(texts)
        raise ValueError("No embedding service available (local embeddings not initialized)")
    
    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers model"""
        if not self.local_model:
            raise ValueError("Local embedding model not available")
        embeddings = self.local_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.use_local and self.local_model:
            return self.local_model.get_sentence_embedding_dimension()
        
        if "3-small" in self.model:
            return 1536
        elif "3-large" in self.model:
            return 3072
        else:
            return 1536  # default

embedding_service = EmbeddingService()

