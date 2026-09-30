import json
from pathlib import Path
from providers.ltx_video_provider import LTXVideoProvider

ROOT = Path(__file__).resolve().parents[1]
PLAN_FILE = ROOT / "projects" / "scene-plan.json"

plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))

scene = plan["scenes"][0]
prompt = scene["visual_prompt"]

print("AYRA DIRECTOR → LTX TEST")
print("Scene:", scene["scene_number"])
print("Prompt:", prompt)

provider = LTXVideoProvider()

result = provider.generate(
    prompt=prompt,
    duration_seconds=2,
    height=512,
    width=704,
)

print("GENERATION: PASS")
print(json.dumps(result, indent=2, ensure_ascii=False))
