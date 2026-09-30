import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"

plan_file = PROJECTS / "scene-plan.json"
plan = json.loads(plan_file.read_text(encoding="utf-8"))

title = plan["project"].get("title", "")
description = plan["project"].get("description", "")

styles = {
    "documentary": "cinematic documentary, realistic visuals, natural lighting, detailed environment",
    "cinematic": "premium cinematic film look, dramatic lighting, realistic composition",
    "anime": "high quality anime cinematic style, detailed characters, dramatic composition",
    "cartoon": "high quality colorful cartoon animation style, expressive characters",
    "educational": "clean educational visual style, clear composition, realistic and informative",
    "horror": "dark atmospheric horror cinematography, moody lighting, suspenseful environment"
}

style = plan["project"].get("style", "documentary")
style_prompt = styles.get(style, styles["documentary"])

for scene in plan["scenes"]:
    scene_number = scene["scene_id"]

    scene["visual_concept"] = (
        f"Scene {scene_number} for the topic '{title}'. "
        f"Determine the most relevant visual representation from the story and context."
    )

    scene["visual_prompt"] = (
        f"{style_prompt}. "
        f"Create a concept-accurate visual for scene {scene_number} "
        f"of a video about '{title}'. "
        f"Overall concept: {description}. "
        f"The visual must directly support the narration and events of this scene. "
        f"Use appropriate locations, characters, objects, era, atmosphere, "
        f"camera composition and lighting according to the subject. "
        f"Do not use generic unrelated imagery."
    )

    scene["visual_source"] = "auto"

plan_file.write_text(
    json.dumps(plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Universal AYRA visual planner ready: {plan_file}")
