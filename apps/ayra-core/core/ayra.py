import json
import urllib.request
import urllib.error

from core.config import APP_NAME, APP_VERSION
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




