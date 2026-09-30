import subprocess

prompt = """
You are AYRA Studio Story Architect.

Concept:
A young girl discovers a mysterious portal inside an abandoned city.

Return ONLY this JSON object and nothing else:

{
  "hook": "one sentence",
  "tone": "cinematic",
  "beginning": "one paragraph",
  "middle": "one paragraph",
  "climax": "one paragraph",
  "ending": "one paragraph"
}
"""

result = subprocess.run(
    ["ollama", "run", "llama3.2:latest", prompt],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

print("----- OLLAMA RAW RESPONSE -----")
print(result.stdout)
print("----- OLLAMA STDERR -----")
print(result.stderr)
