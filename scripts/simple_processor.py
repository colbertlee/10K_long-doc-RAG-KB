"""Simple and robust document processing pipeline bypassing LightRAG complexity."""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

sys.path.insert(0, 'src')

from rag_kb.config import settings
from rag_kb.ingest.cleaner import TextCleaner
from rag_kb.chunkers.structured import StructuredChunker
from rag_kb.parsers.registry import PARSER_REGISTRY
from rag_kb.models import Document


@dataclass
class ProcessingStats:
    """Statistics for document processing."""
    total_documents: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    total_chunks: int = 0
    processing_time: float = 0.0
    errors: list[str] = field(default_factory=list)


class SimpleDocumentProcessor:
    """Simple document processor that bypasses LightRAG complexity."""
    
    def __init__(self):
        """Initialize the simple processor."""
        self.cleaner = TextCleaner()
        self.chunker = StructuredChunker(target_tokens=400, overlap_chars=60)
        self.stats = ProcessingStats()
    
    def process_document(self, file_path: Path) -> dict[str, Any]:
        """Process a single document.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Processing result
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
            print(f"🔄 Processing: {file_path.name}")
            
            # Step 1: Parse file
            parser = next((p for p in PARSER_REGISTRY if p.can_parse(file_path)), None)
            if not parser:
                raise ValueError(f"No parser found for {file_path.suffix}")
            
            doc = parser.parse(file_path)
            
            result['doc_id'] = doc.doc_id
            self.stats.total_documents += 1
            
            # Step 2: Clean content
            cleaned_content = self.cleaner.clean_text(doc.content, mask_pii=False)
            
            # Step 3: Chunk document
            chunks = self.chunker.chunk(cleaned_content, metadata=doc.metadata)
            result['chunks_count'] = len(chunks)
            self.stats.total_chunks += len(chunks)
            
            # Step 4: Store in document registry
            self._store_in_registry(doc, cleaned_content, chunks)
            
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
    
    def _store_in_registry(self, doc: Document, cleaned_content: str, chunks: list):
        """Store document and chunks in document registry."""
        registry_file = Path(settings.data_dir) / 'document_registry.json'
        
        # Load existing registry
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        else:
            registry = {}
        
        # Update document entry
        registry[doc.doc_id] = {
            'doc_id': doc.doc_id,
            'title': doc.title,
            'content': cleaned_content,
            'metadata': doc.metadata,
            'chunks_count': len(chunks),
            'chunks': [
                {
                    'chunk_id': chunk.chunk_id,
                    'text': chunk.text,
                    'metadata': chunk.metadata
                }
                for chunk in chunks
            ]
        }
        
        # Save registry
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def process_directory(self, directory: Path, pattern: str = "*.pdf") -> dict[str, Any]:
        """Process all files in a directory.
        
        Args:
            directory: Directory containing files to process
            pattern: File pattern to match
            
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
            result = self.process_document(file_path)
            results.append(result)
        
        return {
            'success': True,
            'total_files': len(files),
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
            'total_processing_time': self.stats.processing_time,
            'average_processing_time': self.stats.processing_time / self.stats.total_documents if self.stats.total_documents > 0 else 0,
            'errors': self.stats.errors
        }


async def main():
    """Main function to test the simple pipeline."""
    print("🚀 Simple Document Processing Pipeline Test")
    print("=" * 60)
    
    processor = SimpleDocumentProcessor()
    
    # Test processing documents from uploads directory
    uploads_dir = Path(settings.data_dir) / 'uploads'
    
    if uploads_dir.exists():
        print(f"\n📋 Processing files from uploads directory...")
        result = processor.process_directory(uploads_dir, "*.pdf")
        
        print(f"\n📊 Processing Summary:")
        print(f"  Total files: {result['total_files']}")
        print(f"  Successful: {result['stats']['successful_documents']}")
        print(f"  Failed: {result['stats']['failed_documents']}")
        print(f"  Total chunks: {result['stats']['total_chunks']}")
        print(f"  Processing time: {result['stats']['processing_time']:.2f}s")
        
        if result['stats']['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in result['stats']['errors'][:5]:
                print(f"  - {error}")
    else:
        print(f"⚠️  Uploads directory not found: {uploads_dir}")
    
    print("\n" + "=" * 60)
    print("✅ Simple pipeline test completed")
    print("=" * 60)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)