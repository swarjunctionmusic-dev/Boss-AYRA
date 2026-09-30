import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
ENGINE = ROOT / "engine"

PROJECTS.mkdir(parents=True, exist_ok=True)

request_file = ENGINE / "concept_request.json"
output_file = PROJECTS / "scene-plan.json"

request = json.loads(request_file.read_text(encoding="utf-8-sig"))

concept = request.get("concept", "").strip()

if not concept:
    raise ValueError("concept_request.json mein concept dena zaroori hai.")

from local_story_architect import LocalStoryArchitect
from local_ai_director import LocalAIDirector
from director_plan_validator import DirectorPlanValidator

story = LocalStoryArchitect().create_story(concept)

director = LocalAIDirector()

plan = director.create_plan(
    concept,
    story,
)

validation = DirectorPlanValidator().validate(plan)

if not validation["valid"]:
    raise RuntimeError(
        "Director plan validation failed: "
        + json.dumps(validation, ensure_ascii=False)
    )

project = {
    "title": plan.get("title", request.get("title", "AYRA Studio Project")),
    "concept": concept,
    "description": request.get("description", ""),
    "video_type": plan.get(
        "video_type",
        request.get("video_type", "anime")
    ),
    "visual_style": plan.get(
        "visual_style",
        request.get("visual_style", "anime")
    ),
    "duration_minutes": plan["total_duration_seconds"] / 60,
    "scene_count": len(plan["scenes"]),
    "aspect_ratio": request.get("aspect_ratio", "16:9"),
    "resolution": request.get("resolution", "1920x1080"),
    "fps": request.get("fps", 30),
    "language": request.get("language", "Hindi")
}

output_plan = {
    "project": project,
    "story": story,
    "scenes": plan["scenes"]
}

output_file.write_text(
    json.dumps(output_plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("AYRA REAL SCENE PIPELINE: PASS")
print(f"Saved: {output_file}")
print(f"Scenes: {len(plan['scenes'])}")
print(f"Duration: {plan['total_duration_seconds']} seconds")
