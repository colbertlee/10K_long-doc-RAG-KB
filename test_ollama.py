"""Test Ollama client directly."""

import ollama

client = ollama.Client(host='http://localhost:11434')

print("Testing Ollama client...")

try:
    # Test with simple prompt
    print("Test 1: Simple prompt")
    resp = client.chat(
        model='qwen3.5:4b',
        messages=[{'role': 'user', 'content': 'test'}],
        stream=False
    )
    print(f"Response: {resp['message']['content']}")
except Exception as e:
    print(f"Error: {e}")

try:
    # Test with JSON prompt
    print("\nTest 2: JSON prompt")
    resp = client.chat(
        model='qwen3.5:4b',
        messages=[{'role': 'user', 'content': 'Return JSON: {"test": "value"}'}],
        stream=False
    )
    print(f"Response: {resp['message']['content']}")
except Exception as e:
    print(f"Error: {e}")