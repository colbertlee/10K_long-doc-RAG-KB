"""
Direct test of LightRAG adapter without any caching
"""

import sys
import os

# Force reload by clearing module cache
modules_to_clear = [k for k in sys.modules.keys() if 'rag_kb' in k or 'lightrag' in k]
for mod in modules_to_clear:
    del sys.modules[mod]

# Clear all pycache
import subprocess
subprocess.run(['powershell', '-Command', 'Get-ChildItem -Path . -Recurse -Include *.pyc,__pycache__ | Remove-Item -Recurse -Force'], 
               capture_output=True)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import fresh
from rag_kb.lightrag.adapter import LightRAGAdapter
import inspect

print("=" * 60)
print("Direct Adapter Test")
print("=" * 60)

# Check the actual source
source = inspect.getsource(LightRAGAdapter.ingest)
print(f"Total lines in ingest: {len(source.split(chr(10)))}")
print(f"Contains 'ainsert': {'ainsert' in source}")
print(f"Contains 'run_in_executor': {'run_in_executor' in source}")

# Show key lines
lines = source.split(chr(10))
print("\nKey lines:")
for i, line in enumerate(lines[5:15], start=6):
    print(f"  Line {i}: {line}")