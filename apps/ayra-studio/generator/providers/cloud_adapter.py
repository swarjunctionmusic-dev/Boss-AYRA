import os

import fal_client

from generator.providers.base import VideoProvider


class CloudProviderAdapter(VideoProvider):
    """FAL.ai cloud video provider adapter."""

    def generate(
        self,
        prompt: str,
        duration: float,
        resolution: str,
    ) -> dict:

        if not os.environ.get("FAL_KEY"):
            raise RuntimeError(
                "FAL_KEY is not configured."
            )

        raise RuntimeError(
            "FAL cloud generation endpoint is ready to be configured."
        )

    def capabilities(self) -> dict:
        return {
            "text_to_video": True,
            "image_to_video": False,
            "video_to_video": False,
        }