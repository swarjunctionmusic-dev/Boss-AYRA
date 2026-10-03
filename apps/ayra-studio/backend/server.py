import base64
import json
import sys
from pathlib import Path
from urllib.parse import unquote
from http.server import BaseHTTPRequestHandler, HTTPServer

from generator.provider_manager import ProviderManager


HOST = "127.0.0.1"
PORT = 8000

STUDIO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_DIR = STUDIO_ROOT / "generator"

OUTPUT_DIR = STUDIO_ROOT / "outputs"
INPUT_IMAGE_DIR = STUDIO_ROOT / "assets" / "images"

sys.path.insert(0, str(GENERATOR_DIR.parent))


provider_manager = ProviderManager()


class AYRAHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        # CORS
        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def _read_json(self):
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        raw_body = self.rfile.read(content_length)

        if not raw_body:
            return {}

        return json.loads(
            raw_body.decode("utf-8")
        )

    def do_OPTIONS(self):
        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

        self.end_headers()

    def do_GET(self):

        # ----------------------------------------
        # PROVIDERS
        # ----------------------------------------

        if self.path == "/providers":

            active_provider = "ltx"

            providers = (
                provider_manager.available_providers()
            )

            capabilities = {
                name: provider_manager.capabilities(name)
                for name in providers
            }

            self._send_json(
                {
                    "success": True,
                    "active_provider": active_provider,
                    "providers": providers,
                    "capabilities": capabilities,
                }
            )

            return

        # ----------------------------------------
        # VIDEO
        # ----------------------------------------

        if self.path.startswith("/video/"):

            filename = unquote(
                self.path[len("/video/"):]
            )

            filename = Path(filename).name

            video_file = OUTPUT_DIR / filename

            if not video_file.exists():
                self._send_json(
                    {
                        "success": False,
                        "error": "Video file not found.",
                    },
                    status=404,
                )
                return

            try:
                data = video_file.read_bytes()

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "video/mp4",
                )

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*",
                )

                self.send_header(
                    "Content-Length",
                    str(len(data)),
                )

                self.end_headers()

                self.wfile.write(data)

            except Exception as error:
                self._send_json(
                    {
                        "success": False,
                        "error": str(error),
                    },
                    status=500,
                )

            return

        # ----------------------------------------
        # UNKNOWN GET ROUTE
        # ----------------------------------------

        self._send_json(
            {
                "success": False,
                "error": "Route not found.",
            },
            status=404,
        )

    def do_POST(self):

        # ----------------------------------------
        # STANDARD VIDEO GENERATION
        # ----------------------------------------

        if self.path == "/generate":
            self.handle_text_to_video()
            return

        # ----------------------------------------
        # IMAGE TO VIDEO
        # ----------------------------------------

        if self.path == "/generate-image-video":
            self.handle_image_to_video()
            return

        # ----------------------------------------
        # UNKNOWN POST ROUTE
        # ----------------------------------------

        self._send_json(
            {
                "success": False,
                "error": "Route not found.",
            },
            status=404,
        )

    def handle_text_to_video(self):

        try:
            payload = self._read_json()

            prompt = str(
                payload.get("prompt", "")
            ).strip()

            duration = float(
                payload.get("duration", 2)
            )

            resolution = str(
                payload.get(
                    "resolution",
                    "704x512",
                )
            )

            provider_name = str(
                payload.get(
                    "provider",
                    "ltx",
                )
            ).strip()

            if not prompt:
                self._send_json(
                    {
                        "success": False,
                        "error": "Video prompt is required.",
                    },
                    status=400,
                )
                return

            print()
            print("========================================")
            print("AYRA STUDIO VIDEO REQUEST")
            print("========================================")
            print(f"Provider   : {provider_name}")
            print(f"Duration   : {duration}")
            print(f"Resolution : {resolution}")
            print(f"Prompt     : {prompt}")
            print("========================================")

            provider = provider_manager.get(
                provider_name
            )

            capabilities = (
                provider.capabilities()
            )

            if not capabilities.get(
                "text_to_video",
                False,
            ):
                self._send_json(
                    {
                        "success": False,
                        "error": (
                            f"Provider '{provider_name}' "
                            "does not support text-to-video."
                        ),
                    },
                    status=400,
                )
                return

            result = provider.generate(
                prompt=prompt,
                duration=duration,
                resolution=resolution,
            )

            video_path = Path(
                result["video_path"]
            )

            if not video_path.exists():
                raise FileNotFoundError(
                    f"Generated video not found: "
                    f"{video_path}"
                )

            filename = video_path.name

            self._send_json(
                {
                    "success": True,
                    "filename": filename,
                    "video_path": str(video_path),
                    "provider": result.get(
                        "provider",
                        provider_name,
                    ),
                    "duration": duration,
                    "resolution": resolution,
                }
            )

        except Exception as error:

            print()
            print("AYRA VIDEO GENERATION ERROR")
            print(error)
            print()

            self._send_json(
                {
                    "success": False,
                    "error": str(error),
                },
                status=500,
            )

    def handle_image_to_video(self):

        try:
            payload = self._read_json()

            provider_name = str(
                payload.get(
                    "provider",
                    "free_wan",
                )
            ).strip()

            prompt = str(
                payload.get("prompt", "")
            ).strip()

            duration = float(
                payload.get(
                    "duration",
                    3.5,
                )
            )

            image_data = payload.get(
                "image",
                "",
            )

            if not prompt:
                self._send_json(
                    {
                        "success": False,
                        "error": "Video prompt is required.",
                    },
                    status=400,
                )
                return

            if not image_data:
                self._send_json(
                    {
                        "success": False,
                        "error": "Input image is required.",
                    },
                    status=400,
                )
                return

            print()
            print("========================================")
            print("AYRA IMAGE TO VIDEO REQUEST")
            print("========================================")
            print(f"Provider : {provider_name}")
            print(f"Duration : {duration}")
            print(f"Prompt   : {prompt}")
            print("========================================")

            # ----------------------------------------
            # REMOVE DATA URL PREFIX
            # ----------------------------------------

            if "," in image_data:
                image_data = image_data.split(
                    ",",
                    1,
                )[1]

            image_bytes = base64.b64decode(
                image_data
            )

            INPUT_IMAGE_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            input_image = (
                INPUT_IMAGE_DIR /
                "free_wan_input.png"
            )

            input_image.write_bytes(
                image_bytes
            )

            # ----------------------------------------
            # GET PROVIDER
            # ----------------------------------------

            provider = provider_manager.get(
                provider_name
            )

            capabilities = (
                provider.capabilities()
            )

            if not capabilities.get(
                "image_to_video",
                False,
            ):
                self._send_json(
                    {
                        "success": False,
                        "error": (
                            f"Provider '{provider_name}' "
                            "does not support image-to-video."
                        ),
                    },
                    status=400,
                )
                return

            # ----------------------------------------
            # IMAGE TO VIDEO
            # ----------------------------------------

            if not hasattr(
                provider,
                "generate_from_image",
            ):
                self._send_json(
                    {
                        "success": False,
                        "error": (
                            f"Provider '{provider_name}' "
                            "does not implement "
                            "generate_from_image()."
                        ),
                    },
                    status=400,
                )
                return

            result = provider.generate_from_image(
                image_path=str(input_image),
                prompt=prompt,
                duration=duration,
            )

            video_path = Path(
                result["video_path"]
            )

            if not video_path.exists():
                raise FileNotFoundError(
                    f"Generated video not found: "
                    f"{video_path}"
                )

            filename = video_path.name

            self._send_json(
                {
                    "success": True,
                    "filename": filename,
                    "video_path": str(video_path),
                    "provider": result.get(
                        "provider",
                        provider_name,
                    ),
                    "seed": result.get(
                        "seed"
                    ),
                    "duration": duration,
                }
            )

        except Exception as error:

            print()
            print("AYRA IMAGE TO VIDEO ERROR")
            print(error)
            print()

            self._send_json(
                {
                    "success": False,
                    "error": str(error),
                },
                status=500,
            )


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    INPUT_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    server = HTTPServer(
        (HOST, PORT),
        AYRAHandler,
    )

    print()
    print("========================================")
    print("        AYRA STUDIO BACKEND")
    print("========================================")
    print(f"Server  : http://{HOST}:{PORT}")
    print()
    print("Endpoint: POST /generate")
    print(
        "Free Wan endpoint: "
        "POST /generate-image-video"
    )
    print(
        "Provider endpoint: "
        "GET /providers"
    )
    print(
        "Video route: "
        "GET /video/<filename>"
    )
    print()
    print("LTX Generator: CONNECTED")
    print("FREE WAN: CONNECTED")
    print("CORS: ENABLED")
    print("========================================")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("Stopping AYRA Studio backend...")

    finally:
        server.server_close()


if __name__ == "__main__":
    main()