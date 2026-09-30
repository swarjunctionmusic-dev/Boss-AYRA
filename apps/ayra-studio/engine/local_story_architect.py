import json
import urllib.request
from typing import Dict


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:latest"


class LocalStoryArchitect:
    """Real local AI Story Architect powered by Ollama."""

    def __init__(self, model: str = MODEL):
        self.model = model

    def create_story(self, concept: str) -> Dict:
        concept = concept.strip()

        if not concept:
            raise ValueError("Concept cannot be empty.")

        prompt = f"""
You are AYRA Studio Story Architect.

Create a cinematic, emotionally engaging story from this concept:

{concept}

The Boss provides ONLY the concept.
You decide the story structure yourself.

Return ONLY valid JSON with exactly these keys:
{{
  "hook": "...",
  "tone": "...",
  "beginning": "...",
  "middle": "...",
  "climax": "...",
  "ending": "..."
}}

Rules:
- Make the story cinematic and coherent.
- Create strong narrative progression.
- Do not ask the Boss for scenes or story details.
- Do not use markdown.
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))

        response_text = data.get("response", "").strip()

        if not response_text:
            raise RuntimeError("Ollama returned an empty response.")

        story = json.loads(response_text)

        required_keys = {
            "hook",
            "tone",
            "beginning",
            "middle",
            "climax",
            "ending",
        }

        missing = required_keys - story.keys()

        if missing:
            raise RuntimeError(
                f"Story Architect response is missing keys: {sorted(missing)}"
            )

        return story


if __name__ == "__main__":
    architect = LocalStoryArchitect()

    story = architect.create_story(
        "A young girl discovers a mysterious portal inside an abandoned city "
        "and enters a hidden world where time has stopped."
    )

    print("AYRA Local Story Architect: PASS")
    print(json.dumps(story, indent=2, ensure_ascii=False))
