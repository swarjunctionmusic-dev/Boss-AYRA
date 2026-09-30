import os
import shutil
from pathlib import Path

from gradio_client import Client


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "apps" / "ayra-studio" / "outputs"


def generate_video(
    prompt: str,
    negative_prompt: str = (
        "worst quality, inconsistent motion, blurry, jittery, distorted, "
        "extra limbs, deformed face"
    ),
    duration: float = 2,
    height: int = 512,
    width: int = 704,
):
    token = os.environ.get("HF_TOKEN")

    if not token:
        raise RuntimeError(
            "HF_TOKEN is not set. Please set your Hugging Face token first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Connecting to LTX Video...")
    client = Client(
        "Lightricks/ltx-video-distilled",
        token=token,
    )

    print("Generating video...")
    
    result = client.predict(
        prompt=prompt,
        negative_prompt=negative_prompt,
        input_image_filepath=None,
        input_video_filepath=None,
        height_ui=height,
        width_ui=width,
        mode="text-to-video",
        duration_ui=duration,
        ui_frames_to_use=9,
        seed_ui=42,
        randomize_seed=True,
        ui_guidance_scale=1,
        improve_texture_flag=True,
        api_name="/text_to_video",
    )

    video_data = result[0]
    seed = result[1]

    temp_video = video_data["video"]

    source = Path(temp_video)

    if not source.exists():
        raise FileNotFoundError(
            f"LTX generated a video but the file was not found: {source}"
        )

    output_file = OUTPUT_DIR / f"ayra_video_{seed}.mp4"

    shutil.copy2(source, output_file)

    print()
    print("========================================")
    print("AYRA VIDEO GENERATED SUCCESSFULLY")
    print("========================================")
    print(f"Seed   : {seed}")
    print(f"Output : {output_file}")
    print("========================================")

    return output_file


if __name__ == "__main__":
    prompt = (
        "A clearly visible humanoid female AI ROBOT assistant named AYRA, "
        "futuristic mechanical face and body, metallic robotic armor, "
        "glowing cyan-blue eyes, subtle illuminated circuits, "
        "unmistakably a robot and not a human woman, "
        "standing inside a futuristic high-tech AI command center, "
        "cinematic lighting, detailed mechanical design, "
        "slow cinematic camera movement, premium sci-fi film look"
    )

    generate_video(prompt)