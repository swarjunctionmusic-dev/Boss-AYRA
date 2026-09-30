from generator.providers.base import VideoProvider
from generator.providers.ltx_adapter import LTXProviderAdapter


class ProviderManager:
    def __init__(self):
        self.providers: dict[str, VideoProvider] = {
            "ltx": LTXProviderAdapter(),
        }

    def get(self, name: str = "ltx") -> VideoProvider:
        if name not in self.providers:
            raise ValueError(f"Unknown video provider: {name}")

        return self.providers[name]
