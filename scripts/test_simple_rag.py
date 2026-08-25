"""
Simple RAG System Test
Quick test to verify basic functionality
"""

import requests
import json
from pathlib import Path

def test_basic_functionality():
    """Test basic RAG functionality"""
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("SIMPLE RAG SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Server Health
    print("\n1. Testing Server Health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Document Registry
    print("\n2. Testing Document Registry...")
    try:
        response = requests.get(f"{base_url}/api/v1/documents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            doc_count = data.get('total', 0)
            print(f"✅ Found {doc_count} documents")
            if doc_count > 0:
                print(f"   Sample document: {data['documents'][0]['title']}")
        else:
            print(f"❌ Registry check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Registry check failed: {e}")
    
    # Test 3: Vector Database
    print("\n3. Testing Vector Database...")
    vdb_file = Path("lightrag_db/vdb_chunks.json")
    if vdb_file.exists():
        print(f"✅ Vector database exists ({vdb_file.stat().st_size} bytes)")
    else:
        print("❌ Vector database file not found")
    
    # Test 4: Simple GET Search
    print("\n4. Testing GET Search...")
    try:
        response = requests.get(f"{base_url}/api/v1/search", 
                               params={'q': 'test', 'mode': 'hybrid'}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET search works")
            print(f"   Answer: {data.get('answer', 'N/A')[:50]}...")
        else:
            print(f"❌ GET search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET search failed: {e}")
    
    # Test 5: Simple POST Search (with longer timeout)
    print("\n5. Testing POST Search (may take time)...")
    try:
        response = requests.post(f"{base_url}/api/v1/search",
                                json={'q': 'Machine Learning', 'mode': 'hybrid'}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            print(f"✅ POST search works")
            print(f"   Answer length: {len(answer)}")
            print(f"   Answer preview: {answer[:100]}...")
        else:
            print(f"❌ POST search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST search failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed")
    print("=" * 50)

if __name__ == "__main__":
    test_basic_functionality()