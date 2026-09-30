import json
import urllib.request
import urllib.error

from core.config import APP_NAME, APP_VERSION


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "llama3.2:latest"


class AYRA:
    def __init__(self):
        self.name = APP_NAME
        self.version = APP_VERSION

    def respond(self, message: str) -> str:
        message = message.strip()

        if not message:
            return "Boss, aapne kuch kaha nahi."

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


if __name__ == "__main__":
    ayra = AYRA()

    print("=" * 40)
    print(f"{ayra.name} v{ayra.version}")
    print("AYRA CORE ONLINE")
    print(f"AI MODEL: {OLLAMA_MODEL}")
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