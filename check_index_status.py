"""Quick index status check."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_kb.ingest.index_manager import get_index_manager

index_manager = get_index_manager()
report = index_manager.get_index_integrity_report()

print(f"Total uploaded: {report['total_uploaded']}")
print(f"Total indexed: {report['total_indexed']}")
print(f"Unindexed: {report['unindexed_count']}")
print(f"Index health: {report['index_health']}")