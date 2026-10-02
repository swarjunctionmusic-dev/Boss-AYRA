import os
from pathlib import Path
from urllib.request import urlopen

import fal_client

from generator.providers.base import VideoProvider


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "apps" / "ayra-studio" / "outputs"

FAL_MODEL = "fal-ai/hunyuan-video"


class CloudProviderAdapter(VideoProvider):
    """FAL.ai Hunyuan Video cloud provider adapter."""

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

        width, height = map(
            int,
            resolution.lower().split("x")
        )

        aspect_ratio = (
            "16:9"
            if width / height >= 1.2
            else "9:16"
        )

        result = fal_client.subscribe(
            FAL_MODEL,
            {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": "480p",
                "num_frames": 85,
                "enable_safety_checker": True,
            },
        )

        video_url = result["video"]["url"]

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = OUTPUT_DIR / "cloud_video.mp4"

        with urlopen(video_url, timeout=300) as response:
            output_file.write_bytes(response.read())

        return {
            "video_path": str(output_file),
            "provider": FAL_MODEL,
            "video_url": video_url,
        }

    def capabilities(self) -> dict:
        return {
            "text_to_video": True,
            "image_to_video": False,
            "video_to_video": False,
        }