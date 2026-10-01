from generator.providers.base import VideoProvider


class CloudProviderAdapter(VideoProvider):
    """Base adapter for a future cloud video provider."""

    def generate(
        self,
        prompt: str,
        duration: float,
        resolution: str,
    ) -> dict:
        raise RuntimeError(
            "Cloud video provider is not configured yet."
        )

    def capabilities(self) -> dict:
        return {
            "text_to_video": True,
            "image_to_video": False,
            "video_to_video": False,
        }
