from generator.providers.base import VideoProvider
from generator.ltx_generator import generate_video


class LTXProviderAdapter(VideoProvider):
    """Adapter for AYRA's working LTX generator."""

    def generate(
        self,
        prompt: str,
        duration: float,
        resolution: str,
    ) -> dict:

        width, height = map(
            int,
            resolution.lower().split("x")
        )

        output_file = generate_video(
            prompt=prompt,
            duration=duration,
            height=height,
            width=width,
        )

        return {
            "video_path": str(output_file),
            "provider": "Lightricks/ltx-video-distilled",
        }
