from pathlib import Path
from gradio_client import Client

LTX_SPACE = "Lightricks/ltx-video-distilled"

class LTXVideoProvider:
    """Real AYRA Studio provider for LTX Video via Hugging Face Gradio."""

    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or Path(__file__).resolve().parents[2] / "output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = Client(LTX_SPACE)

    def generate(
        self,
        prompt,
        negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted",
        image_path=None,
        duration_seconds=2,
        height=512,
        width=704,
        seed=42,
        randomize_seed=True,
        guidance_scale=1,
        improve_texture=True,
    ):
        if not prompt or not prompt.strip():
            raise ValueError("LTX prompt cannot be empty.")

        result = self.client.predict(
            prompt.strip(),
            negative_prompt,
            str(image_path) if image_path else None,
            None,
            height,
            width,
            "image-to-video" if image_path else "text-to-video",
            duration_seconds,
            9,
            seed,
            randomize_seed,
            guidance_scale,
            improve_texture,
            api_name="/text_to_video",
        )

        generated = result[0]
        returned_seed = result[1]

        source_video = Path(generated["video"])

        if not source_video.exists():
            raise FileNotFoundError(
                f"LTX returned a video path that does not exist: {source_video}"
            )

        destination = self.output_dir / f"ltx_scene_{returned_seed}.mp4"
        destination.write_bytes(source_video.read_bytes())

        return {
            "video_path": str(destination),
            "seed": returned_seed,
            "provider": "Lightricks/ltx-video-distilled",
        }
