"""Test chunking functionality to diagnose the issue."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


async def test_chunking():
    """Test if LightRAG can properly chunk documents."""
    
    print("=" * 60)
    print("Testing LightRAG Chunking Functionality")
    print("=" * 60)
    
    # Initialize LightRAG adapter
    rag = LightRAGAdapter()
    await rag.ensure_initialized()
    
    # Test document
    test_content = """
# Machine Learning Basics

Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data. It enables computers to improve their performance on a specific task through experience.

## Key Concepts

### Supervised Learning
In supervised learning, the algorithm is trained on labeled data. The model learns to map input data to the correct output.

### Unsupervised Learning  
Unsupervised learning deals with unlabeled data. The algorithm tries to find patterns and structures in the data without explicit guidance.

### Deep Learning
Deep learning is a subset of machine learning that uses neural networks with multiple layers to model complex patterns in large datasets.

## Applications

Machine learning is used in various fields:
- Healthcare: Disease diagnosis and drug discovery
- Finance: Fraud detection and algorithmic trading
- Technology: Image recognition and natural language processing
- Transportation: Autonomous vehicles and route optimization
"""
    
    test_doc = {
        'doc_id': 'test_chunking_doc',
        'content': test_content,
        'metadata': {
            'title': 'Test Document for Chunking',
            'source': 'test_source'
        }
    }
    
    print(f"Test document length: {len(test_content)} characters")
    print(f"Chunk token size setting: 1200")
    
    try:
        # Try to ingest the test document using synchronous insert
        print("\nAttempting to ingest test document using synchronous insert...")
        
        # Format document
        formatted_content = rag._format_document(test_content, test_doc['doc_id'], test_doc['metadata'])
        print(f"Formatted content length: {len(formatted_content)}")
        
        # Use synchronous insert in thread pool to avoid event loop issues
        print("Using thread pool for insert...")
        import asyncio
        loop = asyncio.get_event_loop()
        
        def sync_insert():
            rag.rag.insert(formatted_content)
        
        await loop.run_in_executor(None, sync_insert)
        print("Insert completed successfully!")
        
        # Check if chunks were created
        print("\nChecking chunk status...")
        working_dir = Path(settings.lightrag_working_dir)
        vdb_chunks = working_dir / "vdb_chunks.json"
        
        if vdb_chunks.exists():
            print(f"vdb_chunks.json exists: {vdb_chunks.stat().st_size} bytes")
            import json
            with open(vdb_chunks, 'r') as f:
                chunks_data = json.load(f)
            print(f"Number of chunks in vdb_chunks.json: {len(chunks_data)}")
            
            # Show some chunk info
            if chunks_data:
                first_chunk_key = list(chunks_data.keys())[0]
                print(f"First chunk key: {first_chunk_key}")
                print(f"First chunk data preview: {str(chunks_data[first_chunk_key])[:200]}...")
        else:
            print("vdb_chunks.json does not exist")
        
        # Try to query the ingested document
        print("\nTrying to query the ingested document...")
        query_result = await rag.query("What is machine learning?", mode="naive")
        print(f"Query result: {query_result[:300] if query_result else 'None'}...")
        
    except Exception as e:
        print(f"Error during chunking test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_chunking())