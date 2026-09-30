import json
from pathlib import Path
from typing import Any, Dict


class StoryArchitect:
    """Builds the narrative blueprint from Boss's concept."""

    def create_story(
        self,
        concept: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        concept = concept.strip()

        if not concept:
            raise ValueError("Concept cannot be empty.")

        context = context or {}

        return {
            "concept": concept,
            "story": {
                "hook": "",
                "tone": context.get("tone", "cinematic"),
                "beginning": "",
                "middle": "",
                "climax": "",
                "ending": ""
            },
            "status": "story_blueprint_ready"
        }


if __name__ == "__main__":
    architect = StoryArchitect()

    result = architect.create_story(
        "A young girl discovers a mysterious portal inside an abandoned city."
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
