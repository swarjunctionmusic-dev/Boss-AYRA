from backend.config import ACTIVE_VIDEO_PROVIDER
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import json
import sys
from pathlib import Path
from urllib.parse import unquote

HOST = "127.0.0.1"
PORT = 8000

# AYRA Studio root
STUDIO_ROOT = Path(__file__).resolve().parents[1]

# Generator folder
GENERATOR_DIR = STUDIO_ROOT / "generator"

# Generated videos folder
OUTPUT_DIR = STUDIO_ROOT / "outputs"

# Temporary input images folder
INPUT_IMAGE_DIR = STUDIO_ROOT / "assets" / "images"

# Python ko generator folder ka path do
sys.path.insert(0, str(GENERATOR_DIR))

from generator.provider_manager import ProviderManager


provider_manager = ProviderManager()


class AYRAHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.end_headers()

    def do_GET(self):

        # Serve generated video
        if self.path.startswith("/video/"):

            filename = unquote(
                self.path[len("/video/"):]
            )

            # Security: only allow filename
            safe_filename = Path(filename).name

            video_file = OUTPUT_DIR / safe_filename

            if not video_file.exists():
                self.send_json(
                    {
                        "success": False,
                        "error": "Video file not found."
                    },
                    404
                )
                return

            try:
                file_size = video_file.stat().st_size

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "video/mp4"
                )
                self.send_header(
                    "Content-Length",
                    str(file_size)
                )
                self.send_header(
                    "Accept-Ranges",
                    "bytes"
                )
                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )
                self.end_headers()

                with open(video_file, "rb") as video:

                    while True:
                        chunk = video.read(
                            1024 * 1024
                        )

                        if not chunk:
                            break

                        self.wfile.write(chunk)

                return

            except Exception as error:

                print(
                    "Video serving error:",
                    error
                )

                return

        # Provider information
        if self.path == "/providers":

            self.send_json(
                {
                    "success": True,
                    "active_provider": ACTIVE_VIDEO_PROVIDER,
                    "providers":
                        provider_manager.available_providers(),
                    "capabilities":
                        provider_manager.capabilities(
                            ACTIVE_VIDEO_PROVIDER
                        ),
                }
            )

            return

        # Unknown GET endpoint
        self.send_json(
            {
                "success": False,
                "error": "Endpoint not found"
            },
            404
        )

    def do_POST(self):

        # -------------------------------------------------
        # NORMAL TEXT-TO-VIDEO ENDPOINT
        # -------------------------------------------------

        if self.path == "/generate":

            self.handle_text_to_video()

            return

        # -------------------------------------------------
        # FREE WAN IMAGE-TO-VIDEO ENDPOINT
        # -------------------------------------------------

        if self.path == "/generate-image-video":

            self.handle_image_to_video()

            return

        # -------------------------------------------------
        # UNKNOWN POST ENDPOINT
        # -------------------------------------------------

        self.send_json(
            {
                "success": False,
                "error": "Endpoint not found"
            },
            404
        )

    def read_json_body(self):

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        raw_data = self.rfile.read(
            content_length
        )

        return json.loads(
            raw_data.decode("utf-8")
        )

    def handle_text_to_video(self):

        try:

            data = self.read_json_body()

            prompt = data.get(
                "prompt",
                ""
            ).strip()

            requested_provider = data.get(
                "provider",
                ACTIVE_VIDEO_PROVIDER
            )

            if not prompt:

                self.send_json(
                    {
                        "success": False,
                        "error":
                            "Video prompt is required."
                    },
                    400
                )

                return

            duration = float(
                data.get(
                    "duration",
                    2
                )
            )

            resolution = data.get(
                "resolution",
                "704x512"
            )

            try:

                width, height = map(
                    int,
                    resolution.split("x")
                )

            except Exception:

                self.send_json(
                    {
                        "success": False,
                        "error":
                            "Invalid resolution format."
                    },
                    400
                )

                return

            print()
            print("===================================")
            print("       AYRA VIDEO REQUEST")
            print("===================================")
            print("Provider  :", requested_provider)
            print("Prompt    :", prompt)
            print("Duration  :", duration)
            print("Resolution:", resolution)
            print("===================================")
            print("Generating video...")
            print()

            provider = provider_manager.get(
                requested_provider
            )

            result = provider.generate(
                prompt=prompt,
                duration=duration,
                resolution=resolution
            )

            output_file = Path(
                result["video_path"]
            )

            print()
            print("===================================")
            print("       AYRA VIDEO READY")
            print("===================================")
            print("Provider:", result.get("provider"))
            print("Output  :", output_file)
            print("===================================")
            print()

            self.send_json(
                {
                    "success": True,
                    "message":
                        "AYRA video generated successfully.",
                    "provider":
                        result.get("provider"),
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution,
                    "filename":
                        output_file.name,
                    "path":
                        str(output_file)
                }
            )

        except Exception as error:

            print()
            print("AYRA BACKEND ERROR")
            print("------------------")
            print(error)
            print()

            self.send_json(
                {
                    "success": False,
                    "error": str(error)
                },
                500
            )

    def handle_image_to_video(self):

        try:

            data = self.read_json_body()

            provider_name = data.get(
                "provider",
                "free_wan"
            )

            prompt = data.get(
                "prompt",
                ""
            ).strip()

            image_data = data.get(
                "image",
                ""
            )

            duration = float(
                data.get(
                    "duration",
                    3.5
                )
            )

            if provider_name != "free_wan":

                self.send_json(
                    {
                        "success": False,
                        "error":
                            "This endpoint is currently "
                            "for the free_wan provider only."
                    },
                    400
                )

                return

            if not prompt:

                self.send_json(
                    {
                        "success": False,
                        "error":
                            "Video prompt is required."
                    },
                    400
                )

                return

            if not image_data:

                self.send_json(
                    {
                        "success": False,
                        "error":
                            "Input image is required."
                    },
                    400
                )

                return

            # ---------------------------------------------
            # Decode Base64 image
            # ---------------------------------------------

            if "," in image_data:

                image_data = image_data.split(
                    ",",
                    1
                )[1]

            try:

                image_bytes = base64.b64decode(
                    image_data
                )

            except Exception:

                self.send_json(
                    {
                        "success": False,
                        "error":
                            "Invalid Base64 image data."
                    },
                    400
                )

                return

            INPUT_IMAGE_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            image_file = (
                INPUT_IMAGE_DIR /
                "free_wan_input.png"
            )

            image_file.write_bytes(
                image_bytes
            )

            print()
            print("===================================")
            print("       FREE WAN IMAGE REQUEST")
            print("===================================")
            print("Provider :", provider_name)
            print("Image    :", image_file)
            print("Prompt   :", prompt)
            print("Duration :", duration)
            print("===================================")
            print("Sending request to FREE Wan2.2...")
            print()

            provider = provider_manager.get(
                provider_name
            )

            if not hasattr(
                provider,
                "generate_from_image"
            ):

                raise RuntimeError(
                    "Selected provider does not support "
                    "image-to-video generation."
                )

            result = provider.generate_from_image(
                image_path=str(image_file),
                prompt=prompt,
                duration=duration
            )

            output_file = Path(
                result["video_path"]
            )

            print()
            print("===================================")
            print("       FREE WAN VIDEO READY")
            print("===================================")
            print("Provider:", result.get("provider"))
            print("Seed    :", result.get("seed"))
            print("Output  :", output_file)
            print("===================================")
            print()

            self.send_json(
                {
                    "success": True,
                    "message":
                        "Free Wan2.2 video generated successfully.",
                    "provider":
                        result.get("provider"),
                    "prompt": prompt,
                    "duration": duration,
                    "filename":
                        output_file.name,
                    "path":
                        str(output_file),
                    "seed":
                        result.get("seed")
                }
            )

        except Exception as error:

            print()
            print("FREE WAN BACKEND ERROR")
            print("----------------------")
            print(error)
            print()

            self.send_json(
                {
                    "success": False,
                    "error": str(error)
                },
                500
            )


if __name__ == "__main__":

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    INPUT_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    server = HTTPServer(
        (HOST, PORT),
        AYRAHandler
    )

    print("")
    print("===================================")
    print("        AYRA STUDIO BACKEND")
    print("===================================")
    print(
        f"Server running at http://{HOST}:{PORT}"
    )
    print("Endpoint: POST /generate")
    print(
        "Free Wan endpoint: "
        "POST /generate-image-video"
    )
    print(
        "Video route: GET /video/<filename>"
    )
    print("LTX Generator: CONNECTED")
    print("FREE WAN: CONNECTED")
    print("===================================")
    print("")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\nAYRA backend stopped.")

    finally:

        server.server_close()