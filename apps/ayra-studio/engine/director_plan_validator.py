import json
from typing import Dict, List


REQUIRED_SCENE_FIELDS = [
    "scene_number",
    "duration_seconds",
    "purpose",
    "narration",
    "characters",
    "location",
    "objects",
    "visual_prompt",
    "camera",
    "lighting",
    "music",
    "sound_effects",
    "transition",
    "continuity_notes",
]


class DirectorPlanValidator:
    """Validate AYRA Studio Director plans before rendering."""

    def validate(self, plan: Dict) -> Dict:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(plan, dict):
            errors.append("Plan must be a JSON object.")
            return self._result(errors, warnings)

        if not plan.get("title"):
            errors.append("Missing plan title.")

        scenes = plan.get("scenes")

        if not isinstance(scenes, list) or not scenes:
            errors.append("Plan must contain at least one scene.")
            return self._result(errors, warnings)

        total_duration = 0

        for index, scene in enumerate(scenes, start=1):
            if not isinstance(scene, dict):
                errors.append(f"Scene {index} is not an object.")
                continue

            for field in REQUIRED_SCENE_FIELDS:
                if field not in scene:
                    errors.append(f"Scene {index}: missing '{field}'.")

            duration = scene.get("duration_seconds", 0)

            if not isinstance(duration, (int, float)) or duration <= 0:
                errors.append(
                    f"Scene {index}: duration_seconds must be greater than zero."
                )
            else:
                total_duration += duration

            if not scene.get("location"):
                errors.append(f"Scene {index}: missing location.")

            if not scene.get("visual_prompt"):
                errors.append(f"Scene {index}: missing visual_prompt.")

            if not scene.get("camera"):
                warnings.append(f"Scene {index}: camera direction is empty.")

            if not scene.get("lighting"):
                warnings.append(f"Scene {index}: lighting direction is empty.")

            if scene.get("narration") is None:
                warnings.append(f"Scene {index}: narration is empty.")

            if not scene.get("continuity_notes"):
                warnings.append(
                    f"Scene {index}: continuity notes are empty."
                )

        declared_duration = plan.get("total_duration_seconds")

        if isinstance(declared_duration, (int, float)):
            if abs(total_duration - declared_duration) > 0.5:
                errors.append(
                    f"Duration mismatch: scenes total {total_duration}s, "
                    f"plan declares {declared_duration}s."
                )

        result = self._result(errors, warnings)
        result["calculated_duration_seconds"] = total_duration
        result["scene_count"] = len(scenes)

        return result

    @staticmethod
    def _result(errors: List[str], warnings: List[str]) -> Dict:
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }


if __name__ == "__main__":
    from local_ai_director import LocalAIDirector
    from local_story_architect import LocalStoryArchitect

    concept = (
        "A young girl discovers a mysterious portal inside an abandoned city "
        "and enters a hidden world where time has stopped."
    )

    story = LocalStoryArchitect().create_story(concept)
    plan = LocalAIDirector().create_plan(concept, story)

    result = DirectorPlanValidator().validate(plan)

    print("AYRA Director Plan Validator")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["valid"]:
        print("VALIDATION: PASS")
    else:
        print("VALIDATION: FAIL")
