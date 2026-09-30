import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "images"
OUTPUT = ROOT / "output"

ASSETS.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)

images = list(ASSETS.glob("*.jpg")) + list(ASSETS.glob("*.jpeg")) + list(ASSETS.glob("*.png")) + list(ASSETS.glob("*.webp"))

if not images:
    print("AYRA Studio: assets\\images mein abhi koi image nahi hai.")
    print("Ek JPG/PNG image wahan rakho, phir renderer dobara run karenge.")
    raise SystemExit(0)

image = images[0]
output = OUTPUT / "visual-scene-test.mp4"

command = [
    "ffmpeg",
    "-loop", "1",
    "-i", str(image),
    "-t", "5",
    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
    "-r", "30",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-y",
    str(output),
]

subprocess.run(command, check=True)
print(f"AYRA Studio visual scene complete: {output}")
