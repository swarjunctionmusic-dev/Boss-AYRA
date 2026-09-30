import json
import urllib.request
import urllib.error

from core.config import STUDIO_URL


def generate_video(
    prompt: str,
    duration: float = 2,
    resolution: str = "704x512",
) -> dict:
    url = f"{STUDIO_URL}/generate"

    payload = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"AYRA Studio se connection nahi ho paaya: {error}"
        ) from error
