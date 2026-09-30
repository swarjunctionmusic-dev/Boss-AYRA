from abc import ABC, abstractmethod


class VideoProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        duration: float,
        resolution: str,
    ) -> dict:
        pass
