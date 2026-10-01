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

    def capabilities(self) -> dict:
        return {
            "text_to_video": True,
            "image_to_video": False,
            "video_to_video": False,
        }