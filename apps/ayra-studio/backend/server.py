from backend.config import ACTIVE_VIDEO_PROVIDER
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
from pathlib import Path
from urllib.parse import unquote

HOST = "127.0.0.1"
PORT = 8000

# AYRA Studio root
STUDIO_ROOT = Path(__file__).resolve().parents[1]

# LTX generator folder
GENERATOR_DIR = STUDIO_ROOT / "generator"

# Generated videos folder
OUTPUT_DIR = STUDIO_ROOT / "outputs"

# Python ko generator folder ka path do
sys.path.insert(0, str(GENERATOR_DIR))

# Existing LTX generator import
from generator.provider_manager import ProviderManager

provider_manager = ProviderManager()


class AYRAHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):

        # Serve generated video
        if self.path.startswith("/video/"):

            filename = unquote(
                self.path[len("/video/"):]
            )

            # Security: only allow filename, not folders
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
                        chunk = video.read(1024 * 1024)

                        if not chunk:
                            break

                        self.wfile.write(chunk)

                return

            except Exception as error:

                print("Video serving error:", error)

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

        if self.path != "/generate":
            self.send_json(
                {
                    "success": False,
                    "error": "Endpoint not found"
                },
                404
            )
            return

        try:

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            raw_data = self.rfile.read(
                content_length
            )

            data = json.loads(
                raw_data.decode("utf-8")
            )

            prompt = data.get(
                "prompt",
                ""
            ).strip()

            if not prompt:
                self.send_json(
                    {
                        "success": False,
                        "error": "Video prompt is required."
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
                        "error": "Invalid resolution format."
                    },
                    400
                )

                return

            print()
            print("===================================")
            print("       AYRA LTX VIDEO REQUEST")
            print("===================================")
            print("Prompt    :", prompt)
            print("Duration  :", duration)
            print("Resolution:", resolution)
            print("===================================")
            print("Generating video...")
            # Video generation through Provider Manager
            provider = provider_manager.get(ACTIVE_VIDEO_PROVIDER)

            result = provider.generate(
                prompt=prompt,
                duration=duration,
                resolution=resolution
            )

            output_file = Path(result["video_path"])

            print()
            print("===================================")
            print("       AYRA VIDEO READY")
            print("===================================")
            print("Output:", output_file)
            print("===================================")
            print()

            self.send_json(
                {
                    "success": True,
                    "message": "AYRA video generated successfully.",
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution,
                    "filename": output_file.name,
                    "path": str(output_file)
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


if __name__ == "__main__":

    OUTPUT_DIR.mkdir(
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
    print("Video route: GET /video/<filename>")
    print("LTX Generator: CONNECTED")
    print("===================================")
    print("")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\nAYRA backend stopped.")

    finally:

        server.server_close()

