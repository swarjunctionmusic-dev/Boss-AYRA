import json
import urllib.request
from typing import Dict


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:latest"


class LocalAIDirector:
    """AYRA Studio AI Director powered by local Ollama."""

    def __init__(self, model: str = MODEL):
        self.model = model

    def create_plan(self, concept: str, story: Dict) -> Dict:
        concept = concept.strip()

        if not concept:
            raise ValueError("Concept cannot be empty.")

        prompt = f"""
You are AYRA Studio's professional AI Film Director.

The Boss provides ONLY a concept.
The Boss does NOT provide scenes, characters, narration, camera,
visual prompts, music, sound effects, or editing instructions.

You must independently create ALL creative production decisions.

CONCEPT:
{concept}

STORY:
{json.dumps(story, ensure_ascii=False)}

Create a cinematic production plan for a 60-second proof-of-pipeline video.

The result must feel like a real director's production plan,
not a generic template.

Return ONLY valid JSON.

Required top-level keys:
title
video_type
visual_style
total_duration_seconds
scenes

Create exactly 6 scenes.

Every scene MUST contain:
scene_number
duration_seconds
purpose
narration
characters
location
objects
visual_prompt
camera
lighting
music
sound_effects
transition
continuity_notes

STRICT CREATIVE RULES:

1. NARRATION
- Every scene must have useful narration.
- Narration must move the story forward.
- Keep narration concise enough for the scene duration.
- Never return an empty narration field.

2. CHARACTERS
- Decide which characters appear.
- Describe their visible identity consistently.
- Include age range, gender presentation, clothing, hairstyle,
  important facial/visual traits and emotional state when relevant.
- If the scene has no character, explicitly write "No characters".

3. LOCATION
- Give a specific cinematic location.
- Avoid generic phrases such as "a place" or "somewhere".
- Keep locations consistent with the story.

4. OBJECTS
- Identify important story-relevant objects.
- Do not use empty strings.
- If there are no important objects, write "None".

5. VISUAL PROMPT
Every visual_prompt must be detailed enough for an image/video generator.

It must describe:
subject + environment + action + composition + atmosphere +
style + lighting + important visual details.

Do NOT write generic prompts like:
"Establishing shot of the city."

Instead create a complete generation-ready description.

6. CAMERA
Specify cinematic camera language such as:
wide establishing shot,
slow dolly forward,
tracking shot,
close-up,
low angle,
over-the-shoulder,
orbit shot,
handheld,
crane shot,
etc.

7. LIGHTING
Specify the actual lighting mood and source:
overcast daylight, moonlight, neon rim light,
warm sunset, volumetric fog, practical lights, etc.

8. MUSIC
Every scene must specify a music direction.
Example:
"Low atmospheric strings building tension."
Never leave music empty.

9. SOUND EFFECTS
Every scene must specify relevant SFX.
Example:
"distant wind, metal creaks, footsteps."
If none are appropriate, write "None".

10. TRANSITIONS
Choose an appropriate transition:
cut, fade, dissolve, match cut, whip pan,
dip to black, etc.

11. CONTINUITY
Continuity notes must explain what visual details must remain
consistent between this scene and surrounding scenes.

Never leave continuity_notes empty.

12. STYLE
The visual style must match the requested video type.
For anime use cinematic anime aesthetics.
For cartoon use coherent cartoon design.
For documentary use realistic documentary cinematography.
For cinematic content use film-like composition and lighting.

13. STORY COHERENCE
Each scene must have a clear narrative purpose.
The six scenes should form:
setup → discovery → escalation → conflict → climax → resolution.

14. NO QUESTIONS
Never ask the Boss for additional creative details.
Make reasonable creative decisions yourself.

15. JSON
Do not use markdown.
Do not put explanations outside JSON.
Do not return null values for creative fields.
All creative fields must contain useful text.

The final total_duration_seconds must be 60.
Scene durations may initially vary, but the Python code will normalize
the final timeline to exactly 60 seconds.
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "num_predict": 3500,
                "temperature": 0.75
            }
        }

        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=600) as response:
            data = json.loads(response.read().decode("utf-8"))

        response_text = data.get("response", "").strip()

        if not response_text:
            raise RuntimeError("Ollama returned an empty Director response.")

        plan = json.loads(response_text)

        scenes = plan.get("scenes")

        if not isinstance(scenes, list) or not scenes:
            raise RuntimeError("Director returned an empty scene list.")

        target_duration = 60
        scene_count = len(scenes)

        base_duration = target_duration // scene_count
        remainder = target_duration % scene_count

        for index, scene in enumerate(scenes):
            scene["scene_number"] = index + 1
            scene["duration_seconds"] = (
                base_duration + (1 if index < remainder else 0)
            )

            for field, fallback in {
                "narration": "No narration.",
                "characters": "No characters.",
                "location": "Undetermined location.",
                "objects": "None.",
                "visual_prompt": "Cinematic story-relevant visual.",
                "camera": "Cinematic establishing shot.",
                "lighting": "Natural cinematic lighting.",
                "music": "Atmospheric background music.",
                "sound_effects": "None.",
                "transition": "Cut.",
                "continuity_notes": "Maintain visual continuity with surrounding scenes."
            }.items():
                if not scene.get(field):
                    scene[field] = fallback

        plan["total_duration_seconds"] = target_duration

        return plan


if __name__ == "__main__":
    from local_story_architect import LocalStoryArchitect

    concept = (
        "A young girl discovers a mysterious portal inside an abandoned city "
        "and enters a hidden world where time has stopped."
    )

    story = LocalStoryArchitect().create_story(concept)

    director = LocalAIDirector()
    plan = director.create_plan(concept, story)

    print("AYRA Local AI Director: PASS")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
