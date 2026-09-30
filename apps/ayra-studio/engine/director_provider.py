from abc import ABC, abstractmethod
from typing import Any, Dict


class DirectorProvider(ABC):
    """Common interface for every AYRA Director AI provider."""

    @abstractmethod
    def create_plan(
        self,
        concept: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Convert a Boss concept into a complete production plan."""
        raise NotImplementedError
