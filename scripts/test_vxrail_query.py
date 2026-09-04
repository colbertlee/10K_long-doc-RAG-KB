"""Test query functionality with vxrail."""

import requests
import json

def test_vxrail_query():
    """Test query for vxrail."""
    print("🧪 Testing VXRail Query")
    print("=" * 60)
    
    try:
        # Test query
        url = "http://localhost:8000/api/v1/search"
        payload = {
            "q": "vxrail",
            "mode": "naive"
        }
        
        print(f"📤 Sending query: {payload}")
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Query result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check if answer is meaningful
            answer = result.get('answer', '')
            if answer and '未找到' not in answer:
                print("✅ Query returned meaningful answer")
                return True
            else:
                print("⚠️  Query returned empty or no information")
                return False
        else:
            print(f"❌ Query failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_vxrail_query()
    print("=" * 60)
    print(f"Test result: {'✅ Success' if success else '❌ Failed'}")
    print("=" * 60)