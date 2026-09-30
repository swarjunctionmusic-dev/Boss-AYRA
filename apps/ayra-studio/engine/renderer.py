import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

def render_title_scene(title: str, output_name: str = "scene.mp4", duration: int = 5):
    output = OUTPUT / output_name

    filter_text = (
        "drawtext="
        "fontfile='C\\:/Windows/Fonts/arial.ttf':"
        f"text='{title}':"
        "fontcolor=white:"
        "fontsize=96:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2"
    )

    command = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "color=c=0x0b1020:s=1920x1080:r=30",
        "-vf", filter_text,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-y",
        str(output),
    ]

    subprocess.run(command, check=True)
    print(f"AYRA Studio render complete: {output}")


if __name__ == "__main__":
    render_title_scene("AYRA STUDIO", "renderer-test.mp4", 5)
