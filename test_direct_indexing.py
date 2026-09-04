"""Direct indexing test without API."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_kb.ingest.index_manager import get_index_manager


async def test_direct_indexing():
    """Test direct indexing without API."""
    
    print("=" * 60)
    print("Direct Indexing Test")
    print("=" * 60)
    
    try:
        index_manager = get_index_manager()
        
        # Get unindexed documents
        unindexed = index_manager.get_unindexed_documents()
        print(f"\nFound {len(unindexed)} unindexed documents")
        
        if not unindexed:
            print("No unindexed documents found")
            return
        
        # Try to index first document
        first_doc = unindexed[0]
        doc_id = first_doc['doc_id']
        
        print(f"\nAttempting to index document: {doc_id}")
        print(f"Title: {first_doc['title']}")
        
        success, message = await index_manager.index_document(doc_id)
        
        print(f"\nResult: {success}")
        print(f"Message: {message}")
        
        # Check updated status
        report = index_manager.get_index_integrity_report()
        print(f"\nUpdated index status:")
        print(f"  Total uploaded: {report['total_uploaded']}")
        print(f"  Total indexed: {report['total_indexed']}")
        print(f"  Unindexed: {report['unindexed_count']}")
        print(f"  Index health: {report['index_health']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_indexing())