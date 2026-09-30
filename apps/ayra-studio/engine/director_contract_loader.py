import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT_FILE = ROOT / "apps" / "ayra-studio" / "engine" / "director.contract.json"

def load_director_contract():
    with CONTRACT_FILE.open("r", encoding="utf-8-sig") as file:
        return json.load(file)

if __name__ == "__main__":
    contract = load_director_contract()

    request = contract["request"]
    quality = contract["quality"]

    print("AYRA Director contract loaded successfully.")
    print(f"Input mode: {request['input_mode']}")
    print(f"Boss provides: {', '.join(request['boss_provides'])}")
    print(f"Director decisions: {len(request['director_decides'])}")
    print(f"Quality priorities: {len(quality['priority'])}")
