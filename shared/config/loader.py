import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / "shared" / "config" / "ayra.config.json"

def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8-sig") as file:
        return json.load(file)

if __name__ == "__main__":
    config = load_config()
    print("AYRA configuration loaded successfully.")
    print(f"App: {config['app']['name']}")
    print(f"Studio: {config['app']['studio_name']}")
    print(f"AI strategy: {config['ai']['strategy']}")
    print(f"Visual strategy: {config['ai']['visuals']['strategy']}")
    print(f"Render engine: {config['render']['engine']}")
