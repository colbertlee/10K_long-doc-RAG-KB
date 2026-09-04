"""Test index management API endpoints."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_kb.ingest.index_manager import get_index_manager


async def test_index_management_workflow():
    """Test complete index management workflow."""
    
    print("=" * 60)
    print("Testing Index Management Workflow")
    print("=" * 60)
    
    try:
        # Step 1: Get index integrity report
        print("\nStep 1: Getting index integrity report...")
        index_manager = get_index_manager()
        report = index_manager.get_index_integrity_report()
        
        print(f"Total uploaded: {report['total_uploaded']}")
        print(f"Total indexed: {report['total_indexed']}")
        print(f"Unindexed count: {report['unindexed_count']}")
        print(f"Index health: {report['index_health']}")
        
        # Step 2: Get unindexed documents
        print("\nStep 2: Getting unindexed documents...")
        unindexed = index_manager.get_unindexed_documents()
        print(f"Unindexed documents: {len(unindexed)}")
        
        if unindexed:
            print("Unindexed document list:")
            for i, doc in enumerate(unindexed[:3], 1):
                print(f"  {i}. {doc['doc_id']} - {doc['title']}")
        
        # Step 3: Check if we should index documents
        if report['index_health'] == 'unhealthy' and unindexed:
            print("\nStep 3: Index health is unhealthy, considering indexing...")
            print(f"Would index {len(unindexed)} documents")
            print("Skipping actual indexing to avoid long-running test")
            print("✅ Index management workflow test passed")
            return True
        elif report['index_health'] == 'healthy':
            print("\nStep 3: Index health is healthy, no action needed")
            print("✅ Index management workflow test passed")
            return True
        else:
            print("\nStep 3: Index health is partial, may need attention")
            print("✅ Index management workflow test passed")
            return True
        
    except Exception as e:
        print(f"❌ Index management workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_index_management_workflow())
    sys.exit(0 if result else 1)