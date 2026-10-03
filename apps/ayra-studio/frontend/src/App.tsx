import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState("2");
  const [resolution, setResolution] = useState("704x512");

  const [status, setStatus] = useState("READY");
  const [videoUrl, setVideoUrl] = useState("");

  const [activeProvider, setActiveProvider] =
    useState("loading...");

  const [selectedProvider, setSelectedProvider] =
    useState("");

  const [textToVideo, setTextToVideo] =
    useState(false);

  const [imageToVideo, setImageToVideo] =
    useState(false);

  const [videoToVideo, setVideoToVideo] =
    useState(false);

  const [providers, setProviders] =
    useState<string[]>([]);

  const [selectedImage, setSelectedImage] =
    useState<File | null>(null);

  const [imagePreview, setImagePreview] =
    useState("");

  useEffect(() => {
    const loadProvider = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/providers"
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error(
            "Provider status request failed."
          );
        }

        setActiveProvider(
          data.active_provider
        );

        setProviders(
          data.providers ?? []
        );

        setSelectedProvider(
          data.active_provider
        );

        const activeCapabilities =
          data.capabilities?.[
            data.active_provider
          ] ?? data.capabilities ?? {};

        setTextToVideo(
          activeCapabilities.text_to_video ?? false
        );

        setImageToVideo(
          activeCapabilities.image_to_video ?? false
        );

        setVideoToVideo(
          activeCapabilities.video_to_video ?? false
        );
      } catch (error) {
        console.error(error);
        setActiveProvider("offline");
      }
    };

    loadProvider();
  }, []);

  const handleProviderChange = (
    provider: string
  ) => {
    setSelectedProvider(provider);

    setVideoUrl("");
    setStatus("READY");

    /*
      Provider capability data is loaded
      again so the UI can reflect the
      selected provider.
    */

    fetch(
      "http://127.0.0.1:8000/providers"
    )
      .then((response) => response.json())
      .then((data) => {
        const capabilities =
          data.capabilities?.[provider];

        setTextToVideo(
          capabilities?.text_to_video ?? false
        );

        setImageToVideo(
          capabilities?.image_to_video ?? false
        );

        setVideoToVideo(
          capabilities?.video_to_video ?? false
        );
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const handleImageChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedImage(file);

    const previewUrl =
      URL.createObjectURL(file);

    setImagePreview(previewUrl);

    setStatus("IMAGE READY");
  };

  const generateVideo = async () => {
    if (!prompt.trim()) {
      alert(
        "Please enter a video prompt first."
      );
      return;
    }

    if (
      selectedProvider === "free_wan" &&
      !selectedImage
    ) {
      alert(
        "FREE_WAN ke liye pehle ek image select karo."
      );
      return;
    }

    setStatus("GENERATING...");
    setVideoUrl("");

    try {
      if (
        selectedProvider === "free_wan"
      ) {
        const imageBase64 =
          await fileToBase64(
            selectedImage!
          );

        const response = await fetch(
          "http://127.0.0.1:8000/generate-image-video",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              provider: "free_wan",
              prompt: prompt,
              image: imageBase64,
              duration: Number(duration),
            }),
          }
        );

        const data =
          await response.json();

        if (
          !response.ok ||
          !data.success
        ) {
          throw new Error(
            data.error ||
              "FREE_WAN request failed."
          );
        }

        setStatus("VIDEO READY");

        const filename =
          data.filename;

        if (!filename) {
          throw new Error(
            "Backend did not return a video filename."
          );
        }

        const videoPath =
          "http://127.0.0.1:8000/video/" +
          encodeURIComponent(
            filename
          );

        setVideoUrl(videoPath);

        alert(
          "AYRA VIDEO GENERATED SUCCESSFULLY!\n\n" +
            "File: " +
            filename
        );

        return;
      }

      const response = await fetch(
        "http://127.0.0.1:8000/generate",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
            duration: Number(duration),
            resolution: resolution,
            provider:
              selectedProvider,
          }),
        }
      );

      const data =
        await response.json();

      if (
        !response.ok ||
        !data.success
      ) {
        throw new Error(
          data.error ||
            "Backend request failed."
        );
      }

      setStatus("VIDEO READY");

      const filename =
        data.filename;

      if (!filename) {
        throw new Error(
          "Backend did not return a video filename."
        );
      }

      const videoPath =
        "http://127.0.0.1:8000/video/" +
        encodeURIComponent(
          filename
        );

      setVideoUrl(videoPath);

      alert(
        "AYRA VIDEO GENERATED SUCCESSFULLY!\n\n" +
          "File: " +
          filename +
          "\n\n" +
          "Duration: " +
          data.duration +
          " seconds\n" +
          "Resolution: " +
          data.resolution
      );
    } catch (error) {
      console.error(error);

      setStatus("ERROR");

      alert(
        "AYRA video generation failed.\n\n" +
          (error instanceof Error
            ? error.message
            : "Unknown error")
      );
    }
  };

  return (
    <div className="studio">
      <header className="topbar">
        <div className="brand">
          <div className="logo">
            A
          </div>

          <div>
            <h1>AYRA STUDIO</h1>
            <span>
              AI VIDEO CREATION
            </span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          {activeProvider.toUpperCase()}{" "}
          ONLINE
        </div>

        <div className="provider-capabilities">
          <span>
            TEXT → VIDEO{" "}
            {textToVideo
              ? "✓"
              : "✗"}
          </span>

          <span>
            IMAGE → VIDEO{" "}
            {imageToVideo
              ? "✓"
              : "✗"}
          </span>

          <span>
            VIDEO → VIDEO{" "}
            {videoToVideo
              ? "✓"
              : "✗"}
          </span>
        </div>
      </header>

      <main className="workspace">
        <section className="creator-panel">
          <div className="section-title">
            <span>
              CREATE VIDEO
            </span>
          </div>

          <div className="provider-selector">
            <label>
              VIDEO PROVIDER
            </label>

            <select
              value={
                selectedProvider
              }
              onChange={(event) =>
                handleProviderChange(
                  event.target.value
                )
              }
            >
              {providers.map(
                (provider) => (
                  <option
                    key={provider}
                    value={provider}
                  >
                    {provider.toUpperCase()}
                  </option>
                )
              )}
            </select>
          </div>

          <label>
            VIDEO PROMPT
          </label>

          <textarea
            value={prompt}
            onChange={(event) =>
              setPrompt(
                event.target.value
              )
            }
            placeholder="Describe the video you want AYRA to create..."
          />

          {selectedProvider ===
            "free_wan" && (
            <div className="image-upload">
              <label>
                INPUT IMAGE
              </label>

              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={
                  handleImageChange
                }
              />

              {imagePreview && (
                <div className="image-preview">
                  <img
                    src={imagePreview}
                    alt="Selected input"
                  />
                </div>
              )}
            </div>
          )}

          <div className="settings">
            <div className="setting">
              <label>
                DURATION
              </label>

              <select
                value={duration}
                onChange={(event) =>
                  setDuration(
                    event.target.value
                  )
                }
              >
                <option value="2">
                  2 seconds
                </option>

                <option value="4">
                  4 seconds
                </option>

                <option value="6">
                  6 seconds
                </option>
              </select>
            </div>

            <div className="setting">
              <label>
                RESOLUTION
              </label>

              <select
                value={resolution}
                onChange={(event) =>
                  setResolution(
                    event.target.value
                  )
                }
              >
                <option value="704x512">
                  704 × 512
                </option>

                <option value="512x512">
                  512 × 512
                </option>

                <option value="1280x720">
                  1280 × 720
                </option>
              </select>
            </div>
          </div>

          <button
            className="generate-button"
            onClick={
              generateVideo
            }
          >
            🎬 GENERATE VIDEO
          </button>
        </section>

        <section className="preview-panel">
          <div className="preview-header">
            <span>
              PREVIEW
            </span>

            <span className="preview-status">
              {status}
            </span>
          </div>

          <div className="video-placeholder">
            {videoUrl ? (
              <video
                key={videoUrl}
                src={videoUrl}
                controls
                autoPlay
                playsInline
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit:
                    "contain",
                  borderRadius:
                    "12px",
                }}
              />
            ) : (
              <>
                <div className="play-icon">
                  ▶
                </div>

                <h2>
                  AYRA VIDEO PREVIEW
                </h2>

                <p>
                  Your generated
                  video will appear
                  here.
                </p>
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

async function fileToBase64(
  file: File
): Promise<string> {
  return new Promise(
    (resolve, reject) => {
      const reader =
        new FileReader();

      reader.onload = () => {
        resolve(
          String(reader.result)
        );
      };

      reader.onerror = () => {
        reject(
          new Error(
            "Image could not be read."
          )
        );
      };

      reader.readAsDataURL(file);
    }
  );
}

export default App;