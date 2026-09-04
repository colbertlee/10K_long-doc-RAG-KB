"""Test script to verify LightRAG adapter fixes."""

import sys
sys.path.insert(0, 'src')

try:
    from rag_kb.lightrag.adapter import LightRAGAdapter
    import inspect
    
    # Check the current LightRAG initialization code
    source = inspect.getsource(LightRAGAdapter.__init__)
    print("Current LightRAG initialization code:")
    print("=" * 50)
    for i, line in enumerate(source.split('\n'), start=1):
        print(f"{i:3}: {line}")
    print("=" * 50)
    
    # Check for problematic parameter
    if 'llm_response_max_length' in source:
        print("❌ ERROR: llm_response_max_length parameter still present!")
    else:
        print("✅ SUCCESS: llm_response_max_length parameter removed!")
    
    # Try to create an instance
    print("\nAttempting to create LightRAGAdapter instance...")
    try:
        adapter = LightRAGAdapter()
        print("✅ SUCCESS: LightRAGAdapter created successfully!")
    except Exception as e:
        print(f"❌ ERROR: Failed to create adapter: {e}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()