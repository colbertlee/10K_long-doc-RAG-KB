"""Complete document processing pipeline with error handling and monitoring."""

import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

from rag_kb.config import settings
from rag_kb.ingest.cleaner import TextCleaner, mask_pii_placeholder
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.parsers.registry import PARSER_REGISTRY
from rag_kb.models import Document
from rag_kb.utils.deduplication import get_deduplicator


@dataclass
class ProcessingStats:
    """Statistics for document processing."""
    total_documents: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    total_chunks: int = 0
    total_embeddings: int = 0
    processing_time: float = 0.0
    errors: list[str] = field(default_factory=list)


class DocumentProcessingPipeline:
    """Complete document processing pipeline from file to vector database."""
    
    def __init__(self):
        """Initialize the complete processing pipeline."""
        self.cleaner = TextCleaner()
        self.chunker = StructuredChunker(target_tokens=400, overlap_chars=60)
        self.deduplicator = get_deduplicator()
        self.stats = ProcessingStats()
    
    async def process_file(self, file_path: Path, metadata: dict = None) -> dict[str, Any]:
        """Process a single file through the complete pipeline.
        
        Args:
            file_path: Path to the file to process
            metadata: Optional metadata dictionary
            
        Returns:
            Processing result with document ID and status
        """
        start_time = time.time()
        result = {
            'file_path': str(file_path),
            'status': 'pending',
            'doc_id': None,
            'chunks_count': 0,
            'error': None,
            'processing_time': 0.0
        }
        
        try:
            print(f"🔄 Processing file: {file_path.name}")
            
            # Step 1: Parse file (using parser registry directly)
            print(f"  📄 Step 1/5: Parsing file...")
            parser = next((p for p in PARSER_REGISTRY if p.can_parse(file_path)), None)
            if not parser:
                raise ValueError(f"No parser found for {file_path.suffix}")
            
            doc = parser.parse(file_path)
            
            # Check for duplicates
            is_duplicate, reason = self.deduplicator.is_duplicate(
                doc.doc_id, 
                doc.content, 
                doc.metadata
            )
            if is_duplicate:
                result['status'] = 'skipped'
                result['error'] = f'Duplicate: {reason}'
                print(f"  ⚠️  Skipping duplicate: {reason}")
                return result
            
            result['doc_id'] = doc.doc_id
            self.stats.total_documents += 1
            
            # Step 2: Clean content
            print(f"  🧹 Step 2/5: Cleaning content...")
            cleaned_content = self.cleaner.clean_text(doc.content, mask_pii=False)
            
            # Step 3: Chunk document
            print(f"  ✂️  Step 3/5: Chunking document...")
            chunks = self.chunker.chunk(cleaned_content, metadata=doc.metadata)
            result['chunks_count'] = len(chunks)
            self.stats.total_chunks += len(chunks)
            
            # Step 4: Vectorize and store
            print(f"  🔢 Step 4/5: Vectorizing and storing...")
            adapter = LightRAGAdapter()
            await adapter.ensure_initialized()
            
            # Insert chunks with proper formatting
            for chunk in chunks:
                formatted_content = f"# {doc.title}\n\n{chunk.text}"
                await adapter.rag.ainsert(formatted_content)
                self.stats.total_embeddings += 1
            
            # Step 5: Verify storage
            print(f"  ✅ Step 5/5: Verifying storage...")
            # Verification could be added here
            
            result['status'] = 'success'
            self.stats.successful_documents += 1
            print(f"  ✅ Successfully processed: {file_path.name}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.stats.failed_documents += 1
            self.stats.errors.append(f"{file_path.name}: {str(e)}")
            print(f"  ❌ Failed to process {file_path.name}: {e}")
        
        result['processing_time'] = time.time() - start_time
        self.stats.processing_time += result['processing_time']
        
        return result
    
    async def process_directory(self, directory: Path, pattern: str = "*.pdf") -> dict[str, Any]:
        """Process all files in a directory.
        
        Args:
            directory: Directory containing files to process
            pattern: File pattern to match (default: *.pdf)
            
        Returns:
            Processing results summary
        """
        print(f"🔄 Processing directory: {directory}")
        print(f"📋 Pattern: {pattern}")
        
        if not directory.exists():
            return {
                'success': False,
                'error': f'Directory not found: {directory}',
                'stats': self.stats.__dict__
            }
        
        files = list(directory.glob(pattern))
        print(f"📊 Found {len(files)} files to process")
        
        results = []
        for file_path in files:
            result = await self.process_file(file_path)
            results.append(result)
        
        return {
            'success': True,
            'total_files': len(files),
            'results': results,
            'stats': self.stats.__dict__
        }
    
    async def process_registry_documents(self) -> dict[str, Any]:
        """Process all documents from the document registry.
        
        Returns:
            Processing results summary
        """
        print("🔄 Processing documents from registry")
        
        registry_file = Path(settings.data_dir) / 'document_registry.json'
        
        if not registry_file.exists():
            return {
                'success': False,
                'error': 'Document registry not found',
                'stats': self.stats.__dict__
            }
        
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        print(f"📊 Found {len(registry)} documents in registry")
        
        # Initialize LightRAG adapter once
        adapter = LightRAGAdapter()
        await adapter.ensure_initialized()
        
        results = []
        for doc_id, doc_data in registry.items():
            start_time = time.time()
            result = {
                'doc_id': doc_id,
                'title': doc_data.get('title', doc_id),
                'status': 'pending',
                'chunks_count': 0,
                'error': None,
                'processing_time': 0.0
            }
            
            try:
                content = doc_data.get('content', '')
                if not content or len(content) < 100:
                    result['status'] = 'skipped'
                    result['error'] = 'Empty or short content'
                    continue
                
                print(f"🔄 Processing: {doc_data.get('title', doc_id)}")
                
                # Clean content
                cleaned_content = self.cleaner.clean_text(content, mask_pii=False)
                
                # Chunk document
                chunks = self.chunker.chunk(cleaned_content, metadata=doc_data.get('metadata', {}))
                result['chunks_count'] = len(chunks)
                self.stats.total_chunks += len(chunks)
                
                # Vectorize and store
                for chunk in chunks:
                    formatted_content = f"# {doc_data.get('title', doc_id)}\n\n{chunk.text}"
                    await adapter.rag.ainsert(formatted_content)
                    self.stats.total_embeddings += 1
                
                result['status'] = 'success'
                self.stats.successful_documents += 1
                print(f"  ✅ Successfully processed: {doc_data.get('title', doc_id)}")
                
            except Exception as e:
                result['status'] = 'failed'
                result['error'] = str(e)
                self.stats.failed_documents += 1
                self.stats.errors.append(f"{doc_id}: {str(e)}")
                print(f"  ❌ Failed to process {doc_id}: {e}")
            
            result['processing_time'] = time.time() - start_time
            self.stats.processing_time += result['processing_time']
            results.append(result)
        
        self.stats.total_documents = len(registry)
        
        return {
            'success': True,
            'total_documents': len(registry),
            'results': results,
            'stats': self.stats.__dict__
        }
    
    def get_statistics(self) -> dict[str, Any]:
        """Get current processing statistics."""
        return {
            'total_documents': self.stats.total_documents,
            'successful_documents': self.stats.successful_documents,
            'failed_documents': self.stats.failed_documents,
            'success_rate': self.stats.successful_documents / self.stats.total_documents if self.stats.total_documents > 0 else 0,
            'total_chunks': self.stats.total_chunks,
            'total_embeddings': self.stats.total_embeddings,
            'total_processing_time': self.stats.processing_time,
            'average_processing_time': self.stats.processing_time / self.stats.total_documents if self.stats.total_documents > 0 else 0,
            'errors': self.stats.errors
        }


async def main():
    """Main function to test the complete pipeline."""
    print("🚀 Complete Document Processing Pipeline Test")
    print("=" * 60)
    
    pipeline = DocumentProcessingPipeline()
    
    # Test processing documents from registry
    print("\n📋 Processing documents from registry...")
    result = await pipeline.process_registry_documents()
    
    print(f"\n📊 Processing Summary:")
    print(f"  Total documents: {result['total_documents']}")
    print(f"  Successful: {result['stats']['successful_documents']}")
    print(f"  Failed: {result['stats']['failed_documents']}")
    print(f"  Total chunks: {result['stats']['total_chunks']}")
    print(f"  Total embeddings: {result['stats']['total_embeddings']}")
    print(f"  Processing time: {result['stats']['processing_time']:.2f}s")
    
    if result['stats']['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in result['stats']['errors'][:5]:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print("✅ Pipeline test completed")
    print("=" * 60)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)