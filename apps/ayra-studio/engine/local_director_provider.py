from typing import Any, Dict

from director_provider import DirectorProvider


class LocalDirectorProvider(DirectorProvider):
    """Provider-independent local fallback for AYRA Director."""

    def create_plan(
        self,
        concept: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        concept = concept.strip()

        if not concept:
            raise ValueError("Concept cannot be empty.")

        context = context or {}

        return {
            "status": "ready",
            "concept": concept,
            "mode": "local_provider",
            "message": "Concept accepted by AYRA Director.",
            "context": context,
        }
