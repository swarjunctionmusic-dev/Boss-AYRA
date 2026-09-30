from pathlib import Path

from generator.providers.base import VideoProvider
from engine.providers.ltx_video_provider import LTXVideoProvider


class LTXProviderAdapter(VideoProvider):
    """Adapter that exposes the existing AYRA LTX provider through VideoProvider."""

    def __init__(self, output_dir=None):
        self.provider = LTXVideoProvider(output_dir=output_dir)

    def generate(
        self,
        prompt: str,
        duration: float,
        resolution: str,
    ) -> dict:
        width, height = map(int, resolution.lower().split("x"))

        return self.provider.generate(
            prompt=prompt,
            duration_seconds=duration,
            width=width,
            height=height,
        )

