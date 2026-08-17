"""Bulk ingestion script for processing multiple documents."""

from pathlib import Path
from rag_kb.ingest.pipeline import IngestPipeline
from rag_kb.chunkers.parent_child import ParentChildChunker
from rag_kb.lightrag.adapter import LightRAGAdapter


def main():
    """Process all documents in the data/raw directory."""
    data_dir = Path('./data/raw')
    if not data_dir.exists():
        print(f"Data directory {data_dir} does not exist. Creating it.")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"Please place your documents in {data_dir}")
        return
    
    pipeline = IngestPipeline()
    chunker = ParentChildChunker()
    adapter = LightRAGAdapter()
    
    processed_count = 0
    total_chunks = 0
    
    for path in data_dir.glob('*.*'):
        if path.suffix.lower() in {'.pdf', '.docx', '.md', '.txt'}:
            try:
                print(f'Processing {path.name}...')
                doc = pipeline.run(path, acl={'dept': [], 'level': ['Internal']})
                chunks = chunker.chunk(doc)
                adapter.insert_chunks(chunks)
                
                processed_count += 1
                total_chunks += len(chunks)
                print(f'  Indexed {path.name}: {len(chunks)} chunks')
            except Exception as e:
                print(f'  Error processing {path.name}: {e}')
    
    print(f'\nBulk ingestion complete: {processed_count} documents, {total_chunks} total chunks')


if __name__ == '__main__':
    main()