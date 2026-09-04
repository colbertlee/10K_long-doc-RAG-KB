"""
Test script that runs in a completely fresh Python process
"""

import subprocess
import sys

# Run in a completely fresh Python process
code = """
import sys
sys.path.insert(0, 'src')
from rag_kb.lightrag.adapter import LightRAGAdapter
import inspect

source = inspect.getsource(LightRAGAdapter.ingest)
print('Total lines:', len(source.split('\\n')))
print('Has ainsert:', 'ainsert' in source)
print('Has run_in_executor:', 'run_in_executor' in source)
print('First 10 lines:')
for i, line in enumerate(source.split('\\n')[:10], start=1):
    print(f'  {i}: {line}')
"""

result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)