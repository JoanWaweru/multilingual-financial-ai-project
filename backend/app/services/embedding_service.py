"""
Embedding service for generating vector embeddings
"""
from openai import OpenAI, RateLimitError
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
    """Service for generating text embeddings with OpenAI or local fallback"""
    
    def __init__(self):
        self.client = None
        self.model = settings.embedding_model
        self.use_local = settings.use_local_embeddings
        self.local_model = None
        
        # Initialize OpenAI client only if not using local and API key is available
        if not self.use_local and settings.openai_api_key:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize OpenAI client: {e}")
                self.use_local = True
        elif not settings.openai_api_key:
            print("ℹ️ No OpenAI API key found. Using local embeddings.")
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
        
        # If no client available, fall back to local
        if not self.client:
            print("⚠️ No OpenAI client available. Switching to local embeddings...")
            if not self.local_model:
                st_class = globals().get('SentenceTransformer', None)
                if st_class and LOCAL_EMBEDDINGS_AVAILABLE:
                    self.local_model = st_class('all-MiniLM-L6-v2')
                    self.use_local = True
            if self.local_model:
                return self._embed_local([text])[0]
            raise ValueError("No embedding service available (neither OpenAI nor local)")
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except RateLimitError:
            print("⚠️ OpenAI rate limit exceeded. Switching to local embeddings...")
            if not self.local_model:
                st_class = globals().get('SentenceTransformer', None)
                if st_class and LOCAL_EMBEDDINGS_AVAILABLE:
                    self.local_model = st_class('all-MiniLM-L6-v2')
                    self.use_local = True
            if self.local_model:
                return self._embed_local([text])[0]
            raise
        except Exception as e:
            print(f"⚠️ OpenAI error: {e}. Attempting local fallback...")
            if not self.local_model:
                st_class = globals().get('SentenceTransformer', None)
                if st_class and LOCAL_EMBEDDINGS_AVAILABLE:
                    self.local_model = st_class('all-MiniLM-L6-v2')
                    self.use_local = True
            if self.local_model:
                return self._embed_local([text])[0]
            raise
    
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
        
        # If no client available, fall back to local
        if not self.client:
            print("⚠️ No OpenAI client available. Switching to local embeddings...")
            # Ensure sentence-transformers is available
            st_class = globals().get('SentenceTransformer', None)
            if not LOCAL_EMBEDDINGS_AVAILABLE or not st_class:
                try:
                    from sentence_transformers import SentenceTransformer as ST
                    globals()['LOCAL_EMBEDDINGS_AVAILABLE'] = True
                    globals()['SentenceTransformer'] = ST
                    st_class = ST
                except Exception as e:
                    raise ValueError(f"No OpenAI client and sentence-transformers not available: {e}. Run: pip install sentence-transformers")
            
            if not self.local_model:
                try:
                    print("📦 Loading local embedding model...")
                    self.local_model = st_class('all-MiniLM-L6-v2')
                    self.use_local = True
                    print("✅ Local model loaded")
                except Exception as e:
                    print(f"❌ Failed to load local model: {e}")
                    raise ValueError(f"Could not load local embedding model: {e}")
            return self._embed_local(texts)
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except RateLimitError:
            print("⚠️ OpenAI rate limit exceeded. Switching to local embeddings...")
            # Ensure sentence-transformers is available
            st_class = globals().get('SentenceTransformer', None)
            if not LOCAL_EMBEDDINGS_AVAILABLE or not st_class:
                try:
                    from sentence_transformers import SentenceTransformer as ST
                    globals()['LOCAL_EMBEDDINGS_AVAILABLE'] = True
                    globals()['SentenceTransformer'] = ST
                    st_class = ST
                except Exception as e:
                    raise ValueError(f"OpenAI rate limit exceeded and sentence-transformers not available: {e}")
            
            if not self.local_model:
                self.local_model = st_class('all-MiniLM-L6-v2')
                self.use_local = True
            if self.local_model:
                return self._embed_local(texts)
            raise
        except Exception as e:
            print(f"⚠️ OpenAI error: {e}. Attempting local fallback...")
            # Ensure sentence-transformers is available
            st_class = globals().get('SentenceTransformer', None)
            if not LOCAL_EMBEDDINGS_AVAILABLE or not st_class:
                try:
                    from sentence_transformers import SentenceTransformer as ST
                    globals()['LOCAL_EMBEDDINGS_AVAILABLE'] = True
                    globals()['SentenceTransformer'] = ST
                    st_class = ST
                except Exception as import_error:
                    raise ValueError(f"OpenAI error and sentence-transformers not available: {import_error}")
            
            if not self.local_model:
                self.local_model = st_class('all-MiniLM-L6-v2')
                self.use_local = True
            if self.local_model:
                return self._embed_local(texts)
            raise
    
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

