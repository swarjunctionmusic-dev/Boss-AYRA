import shutil
from pathlib import Path

from gradio_client import Client

from generator.providers.base import VideoProvider


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "apps" / "ayra-studio" / "outputs"

WAN_SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"


class FreeWanProviderAdapter(VideoProvider):
    """Free Hugging Face Wan2.2 image-to-video provider."""

    def generate(
        self,
        prompt: str,
        duration: float,
        resolution: str,
    ) -> dict:

        raise RuntimeError(
            "Free Wan2.2 provider requires an input image. "
            "Image-to-video integration will be added next."
        )

    def generate_from_image(
        self,
        image_path: str,
        prompt: str,
        duration: float = 3.5,
    ) -> dict:

        source_image = Path(image_path)

        if not source_image.exists():
            raise FileNotFoundError(
                f"Input image not found: {source_image}"
            )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        print("Connecting to FREE Wan2.2 Space...")

        client = Client(WAN_SPACE)

        print("Generating video with FREE Wan2.2...")

        result = client.predict(
            input_image={
                "path": str(source_image),
            },
            prompt=prompt,
            steps=6,
            negative_prompt=(
                "worst quality, low quality, blurry, "
                "distorted, deformed, extra fingers, "
                "extra limbs, bad hands, bad face, "
                "static image, jittery motion"
            ),
            duration_seconds=duration,
            guidance_scale=1,
            guidance_scale_2=1,
            seed=42,
            randomize_seed=True,
            api_name="/generate_video",
        )

        video_data = result[0]
        seed = result[1]

        generated_video = Path(video_data)

        if not generated_video.exists():
            raise FileNotFoundError(
                f"Wan2.2 generated video was not found: "
                f"{generated_video}"
            )

        output_file = (
            OUTPUT_DIR /
            f"free_wan_video_{int(seed)}.mp4"
        )

        shutil.copy2(
            generated_video,
            output_file,
        )

        print()
        print("========================================")
        print("FREE WAN2.2 VIDEO GENERATED")
        print("========================================")
        print(f"Seed   : {seed}")
        print(f"Output : {output_file}")
        print("========================================")

        return {
            "video_path": str(output_file),
            "provider": WAN_SPACE,
            "seed": seed,
        }

    def capabilities(self) -> dict:
        return {
            "text_to_video": False,
            "image_to_video": True,
            "video_to_video": False,
        }