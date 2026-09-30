import json
import os
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
PROJECTS = ROOT / "projects"

request_file = ENGINE / "concept_request.json"
output_file = PROJECTS / "ai-directed-plan.json"

request = json.loads(request_file.read_text(encoding="utf-8-sig"))

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set.")

client = OpenAI(api_key=api_key)

title = request.get("title", "").strip()
concept = request.get("concept", "").strip()
description = request.get("description", "").strip()
video_type = request.get("video_type", "cinematic")
visual_style = request.get("visual_style", "cinematic")
duration = request.get("duration_minutes", 5)
language = request.get("language", "Hindi")
aspect_ratio = request.get("aspect_ratio", "16:9")
resolution = request.get("resolution", "1920x1080")

director_prompt = f"""
You are AYRA Studio's professional AI Film Director.

The user gives you ONLY a video concept.
You must independently design the complete video.

Do NOT ask the user to provide scenes.
Do NOT use a fixed scene template.
Do NOT assume a fixed number of scenes.

Decide the scene count yourself based on story pacing, narrative importance,
visual changes, emotional beats and the requested duration.

Create a professional production plan containing:

1. Story structure
2. Opening hook
3. Scene-by-scene narration
4. Visual concept for every scene
5. Detailed visual-generation prompt
6. Characters
7. Locations
8. Important objects
9. Era/time context when relevant
10. Camera framing and movement
11. Lighting and atmosphere
12. Music direction
13. Sound-effect direction
14. Subtitle text
15. Transition
16. Approximate scene duration
17. Visual acquisition recommendation:
    - web_search
    - ai_generate
    - stock_or_public_domain
    - hybrid
18. Continuity instructions so characters, locations and visual style remain
    consistent throughout the video.

The final plan must feel like it was created by a professional director,
screenwriter and storyboard artist.

The video must have a strong beginning, coherent middle and satisfying ending.

Do not invent factual claims for documentaries without marking them for
research verification.

Return ONLY valid JSON.

VIDEO REQUEST:
Title: {title}
Concept: {concept}
Description: {description}
Video type: {video_type}
Visual style: {visual_style}
Duration minutes: {duration}
Language: {language}
Aspect ratio: {aspect_ratio}
Resolution: {resolution}

JSON structure:

{{
  "project": {{
    "title": "...",
    "concept": "...",
    "video_type": "...",
    "visual_style": "...",
    "duration_minutes": 0,
    "language": "...",
    "aspect_ratio": "...",
    "resolution": "...",
    "director_notes": "...",
    "story_arc": {{
      "hook": "...",
      "beginning": "...",
      "middle": "...",
      "climax": "...",
      "ending": "..."
    }}
  }},
  "scenes": [
    {{
      "scene_id": 1,
      "duration_seconds": 0,
      "purpose": "...",
      "narration": "...",
      "visual_concept": "...",
      "visual_prompt": "...",
      "visual_source": "ai_generate",
      "characters": [],
      "locations": [],
      "objects": [],
      "camera": {{
        "shot": "...",
        "movement": "...",
        "lens_feel": "..."
      }},
      "lighting": "...",
      "atmosphere": "...",
      "music": "...",
      "sound_effects": [],
      "subtitle": "...",
      "transition": "...",
      "continuity_notes": "..."
    }}
  ]
}}
"""

response = client.responses.create(
    model="gpt-5.6-luna",
    instructions=director_prompt,
    input="Create the complete AI-directed production plan now."
)

raw = response.output_text.strip()

if raw.startswith("```"):
    raw = raw.replace("```json", "", 1).replace("```", "", 1).strip()

plan = json.loads(raw)

output_file.write_text(
    json.dumps(plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("AYRA AI Director plan created successfully.")
print(f"Output: {output_file}")
print(f"Title: {plan['project']['title']}")
print(f"Scenes decided by AI Director: {len(plan['scenes'])}")
print("AYRA chose the scenes automatically from the concept.")
