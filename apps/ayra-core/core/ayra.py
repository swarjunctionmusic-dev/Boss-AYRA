from core.config import APP_NAME, APP_VERSION


class AYRA:
    def __init__(self):
        self.name = APP_NAME
        self.version = APP_VERSION

    def respond(self, message: str) -> str:
        message = message.strip()

        if not message:
            return "Boss, aapne kuch kaha nahi."

        return f"{self.name}: I received your message — {message}"


if __name__ == "__main__":
    ayra = AYRA()

    print("=" * 40)
    print(f"{ayra.name} v{ayra.version}")
    print("AYRA CORE ONLINE")
    print("=" * 40)

    while True:
        try:
            message = input("Boss > ")

            if message.lower() in {"exit", "quit"}:
                print("AYRA: Goodbye, Boss.")
                break

            print(ayra.respond(message))

        except KeyboardInterrupt:
            print("\nAYRA: Goodbye, Boss.")
            break
