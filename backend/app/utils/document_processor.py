"""
Document processing utilities for ingesting financial documents
"""
from typing import List, Dict, Tuple
import PyPDF2
from io import BytesIO
from bs4 import BeautifulSoup
from app.core.config import settings
import re

class DocumentProcessor:
    """Process various document types for RAG ingestion"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    async def process_file(
        self,
        content: bytes,
        filename: str,
        content_type: str = None
    ) -> Tuple[List[str], List[Dict]]:
        """Process a file and return chunks with metadata"""
        
        # Determine file type
        if filename.endswith('.pdf'):
            return await self.process_pdf(content, filename)
        elif filename.endswith('.txt') or filename.endswith('.md'):
            return await self.process_text(content, filename)
        elif filename.endswith('.html') or filename.endswith('.htm'):
            return await self.process_html(content, filename)
        else:
            # Try to process as text
            return await self.process_text(content, filename)
    
    async def process_pdf(self, content: bytes, filename: str) -> Tuple[List[str], List[Dict]]:
        """Extract text from PDF"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_chunks = []
            metadata_list = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    chunks = self._chunk_text(text)
                    for chunk in chunks:
                        text_chunks.append(chunk)
                        metadata_list.append({
                            'source': filename,
                            'page': page_num + 1,
                            'type': 'pdf'
                        })
            
            return text_chunks, metadata_list
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    async def process_text(self, content: bytes, filename: str) -> Tuple[List[str], List[Dict]]:
        """Process plain text file"""
        try:
            text = content.decode('utf-8')
            chunks = self._chunk_text(text)
            metadata = [
                {
                    'source': filename,
                    'type': 'text'
                }
            ] * len(chunks)
            return chunks, metadata
        except Exception as e:
            raise Exception(f"Error processing text: {str(e)}")
    
    async def process_html(self, content: bytes, filename: str) -> Tuple[List[str], List[Dict]]:
        """Extract text from HTML"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            chunks = self._chunk_text(text)
            metadata = [
                {
                    'source': filename,
                    'type': 'html'
                }
            ] * len(chunks)
            return chunks, metadata
        except Exception as e:
            raise Exception(f"Error processing HTML: {str(e)}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if not text.strip():
            return []
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:].strip())
                break
            
            # Try to break at sentence boundary
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            
            break_point = max(last_period, last_newline)
            if break_point > start:
                end = break_point + 1
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return [chunk for chunk in chunks if chunk]

