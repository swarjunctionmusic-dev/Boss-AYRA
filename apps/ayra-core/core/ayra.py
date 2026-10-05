import json
import urllib.request
import urllib.error
import os
import subprocess
import sys
from pathlib import Path


# Ensure the AYRA Core project root is importable when ayra.py
# is launched directly as a script.
AYRA_CORE_ROOT = Path(__file__).resolve().parents[1]

if str(AYRA_CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(AYRA_CORE_ROOT))


def run_startup_auto_update():
    """
    Check for a Boss AYRA update before starting the assistant.
    If an update is installed successfully, restart AYRA automatically.
    """
    if os.getenv("AYRA_SKIP_AUTO_UPDATE") == "1":
        return

    root_dir = Path(__file__).resolve().parents[3]
    updater = root_dir / "scripts" / "updater" / "updater.py"

    if not updater.exists():
        print("AYRA AUTO-UPDATE: updater not found, continuing startup.")
        return

    print()
    print("=" * 40)
    print("AYRA AUTO-UPDATE")
    print("=" * 40)

    try:
        result = subprocess.run(
            [sys.executable, str(updater), "update"],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.stdout:
            print(result.stdout, end="")

        if result.stderr:
            print(result.stderr, end="")

        if "UPDATE SUCCESSFUL" in result.stdout:
            print()
            print("AYRA AUTO-UPDATE: Update installed.")
            print("AYRA AUTO-UPDATE: Restarting AYRA...")

            os.execv(
                sys.executable,
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    *sys.argv[1:],
                ],
            )

        if result.returncode != 0:
            print(
                f"AYRA AUTO-UPDATE: Check/update failed "
                f"(exit code {result.returncode})."
            )
            print("AYRA AUTO-UPDATE: Continuing normal startup.")

    except subprocess.TimeoutExpired:
        print("AYRA AUTO-UPDATE: Timed out after 10 minutes.")
        print("AYRA AUTO-UPDATE: Continuing normal startup.")

    except Exception as error:
        print(f"AYRA AUTO-UPDATE: {error}")
        print("AYRA AUTO-UPDATE: Continuing normal startup.")


from core.config import APP_NAME, APP_VERSION

# Keep AYRA Core display version synchronized with the updater.
try:
    _version_file = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "updater"
        / "version.json"
    )

    if _version_file.exists():
        with _version_file.open("r", encoding="utf-8-sig") as _file:
            _version_data = json.load(_file)

        APP_VERSION = str(_version_data.get("version", APP_VERSION))
except Exception:
    pass
from core.studio_client import generate_video


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "llama3.2:latest"


class AYRA:
    def __init__(self):
        self.name = APP_NAME
        self.version = APP_VERSION

    def is_video_request(self, message: str) -> bool:
        text = message.lower()

        video_words = [
            "video banao",
            "video bana",
            "video create",
            "create video",
            "make video",
            "generate video",
            "video generate",
            "video बनाओ",
            "ayra,",
            "वीडियो बनाओ",
        ]

        return any(word in text for word in video_words)

    def video_prompt(self, message: str) -> str:
        text = message.strip()
        text_lower = text.lower()

        remove_phrases = [
            "video banao",
            "video bana",
            "video create",
            "create video",
            "make video",
            "generate video",
            "video generate",
            "video बनाओ",
            "ayra,",
            "वीडियो बनाओ",
        ]

        for phrase in remove_phrases:
            text = text.replace(phrase, "")

        text = text.strip(" :-,.")

        if text.lower().startswith("ayra,"):
            text = text[5:].strip()

        if not text:
            return (
                "A cinematic futuristic AI scene featuring AYRA, "
                "a humanoid AI robot inside a high-tech command center"
            )

        return text

    def create_video(self, message: str) -> str:
        prompt = self.video_prompt(message)

        print()
        print("========================================")
        print("AYRA → STUDIO COMMAND")
        print("========================================")
        print(f"Video Prompt: {prompt}")
        print("Sending request to AYRA Studio...")
        print("========================================")

        try:
            result = generate_video(
                prompt=prompt,
                duration=2,
                resolution="704x512",
            )

            if not result.get("success"):
                return "Boss, AYRA Studio video request failed."

            filename = result.get("filename", "unknown")

            return (
                f"Boss, video successfully generated.\n"
                f"File: {filename}"
            )

        except Exception as error:
            return (
                "Boss, Studio video generation could not be completed.\n"
                f"Reason: {error}"
            )

    def ask_ai(self, message: str) -> str:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are AYRA, a friendly AI assistant. "
                        "Address the user as Boss. "
                        "Be helpful, concise, and natural."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            "stream": False,
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))

            return result["message"]["content"].strip()

        except urllib.error.URLError as error:
            return f"Boss, Ollama se connection nahi ho paaya: {error}"

        except Exception as error:
            return f"Boss, AI response mein error aaya: {error}"

    def respond(self, message: str) -> str:
        message = message.strip()

        if not message:
            return "Boss, aapne kuch kaha nahi."

        if self.is_video_request(message):
            return self.create_video(message)

        return self.ask_ai(message)


if __name__ == "__main__":
    run_startup_auto_update()

    ayra = AYRA()

    print("=" * 40)
    print(f"{ayra.name} v{ayra.version}")
    print("AYRA CORE ONLINE")
    print(f"AI MODEL: {OLLAMA_MODEL}")
    print("STUDIO CONTROL: ENABLED")
    print("=" * 40)

    while True:
        try:
            message = input("Boss > ")

            if message.lower() in {"exit", "quit"}:
                print("AYRA: Goodbye, Boss.")
                break

            print(f"AYRA > {ayra.respond(message)}")

        except KeyboardInterrupt:
            print("\nAYRA: Goodbye, Boss.")
            break

