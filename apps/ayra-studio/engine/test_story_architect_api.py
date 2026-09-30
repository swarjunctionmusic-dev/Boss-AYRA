import json
import urllib.request

url = "http://127.0.0.1:11434/api/generate"

prompt = """
You are AYRA Studio Story Architect.

Create a cinematic anime story from this concept:
A young girl discovers a mysterious portal inside an abandoned city and enters a hidden world where time has stopped.

Return ONLY valid JSON with exactly these keys:
{
  "hook": "...",
  "tone": "...",
  "beginning": "...",
  "middle": "...",
  "climax": "...",
  "ending": "..."
}

Do not use markdown.
"""

payload = {
    "model": "llama3.2:latest",
    "prompt": prompt,
    "stream": False,
    "format": "json"
}

request = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(request, timeout=180) as response:
    data = json.loads(response.read().decode("utf-8"))

story = json.loads(data["response"])

print("AYRA Story Architect API: PASS")
print(json.dumps(story, indent=2, ensure_ascii=False))
