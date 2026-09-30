import json
import urllib.request

url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "llama3.2:latest",
    "prompt": "Reply with exactly: AYRA LOCAL API OK",
    "stream": False
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(request, timeout=120) as response:
    data = json.loads(response.read().decode("utf-8"))

print("AYRA Ollama API test: PASS")
print("Response:", data.get("response", "").strip())
