import requests
import json

try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    print("Ollama API Status:", response.status_code)
    print("Models:", response.json())
except Exception as e:
    print("Error:", e)