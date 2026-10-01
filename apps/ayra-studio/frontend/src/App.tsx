import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState("2");
  const [resolution, setResolution] = useState("704x512");
  const [status, setStatus] = useState("READY");
  const [videoUrl, setVideoUrl] = useState("");
  const [activeProvider, setActiveProvider] = useState("loading...");
  const [selectedProvider, setSelectedProvider] = useState("");
  const [textToVideo, setTextToVideo] = useState(false);
  const [providers, setProviders] = useState<string[]>([]);
const [imageToVideo, setImageToVideo] = useState(false);
const [videoToVideo, setVideoToVideo] = useState(false);
   useEffect(() => {
    const loadProvider = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/providers"
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error("Provider status request failed.");
        }

        setActiveProvider(data.active_provider);
        setProviders(data.providers ?? []);
        setSelectedProvider(data.active_provider);
        setTextToVideo(data.capabilities?.text_to_video ?? false);
setImageToVideo(data.capabilities?.image_to_video ?? false);
setVideoToVideo(data.capabilities?.video_to_video ?? false);
      } catch (error) {
        console.error(error);
        setActiveProvider("offline");
      }
    };

    loadProvider();
  }, []);



  const generateVideo = async () => {
    if (!prompt.trim()) {
      alert("Please enter a video prompt first.");
      return;
    }

    setStatus("GENERATING...");
    setVideoUrl("");

    try {
      const response = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
          duration: Number(duration),
          resolution: resolution,
          provider: selectedProvider,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Backend request failed.");
      }

      setStatus("VIDEO READY");

      const filename = data.filename;

      if (!filename) {
        throw new Error("Backend did not return a video filename.");
      }

      const videoPath =
        "http://127.0.0.1:8000/video/" +
        encodeURIComponent(filename);

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
          <div className="logo">A</div>

          <div>
            <h1>AYRA STUDIO</h1>
            <span>AI VIDEO CREATION</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
         {activeProvider.toUpperCase()} ONLINE
        </div>
        <div className="provider-capabilities">
  <span>TEXT → VIDEO {textToVideo ? "✓" : "✗"}</span>
  <span>IMAGE → VIDEO {imageToVideo ? "✓" : "✗"}</span>
  <span>VIDEO → VIDEO {videoToVideo ? "✓" : "✗"}</span>
</div>
      </header>

      <main className="workspace">
        <section className="creator-panel">
          <div className="section-title">
            <span>CREATE VIDEO</span>
          </div>
          <div className="provider-selector">
  <label>VIDEO PROVIDER</label>

  <select
    value={selectedProvider}
    onChange={(event) =>
      setSelectedProvider(event.target.value)
    }
  >
   {providers.map((provider) => (
  <option key={provider} value={provider}>
    {provider.toUpperCase()}
  </option>
))}
  </select>
</div>

          <label>VIDEO PROMPT</label>

          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Describe the video you want AYRA to create..."
          />

          <div className="settings">
            <div className="setting">
              <label>DURATION</label>

              <select
                value={duration}
                onChange={(event) =>
                  setDuration(event.target.value)
                }
              >
                <option value="2">2 seconds</option>
                <option value="4">4 seconds</option>
                <option value="6">6 seconds</option>
              </select>
            </div>

            <div className="setting">
              <label>RESOLUTION</label>

              <select
                value={resolution}
                onChange={(event) =>
                  setResolution(event.target.value)
                }
              >
                <option value="704x512">704 × 512</option>
                <option value="512x512">512 × 512</option>
                <option value="1280x720">1280 × 720</option>
              </select>
            </div>
          </div>

          <button
            className="generate-button"
            onClick={generateVideo}
          >
            🎬 GENERATE VIDEO
          </button>
        </section>

        <section className="preview-panel">
          <div className="preview-header">
            <span>PREVIEW</span>
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
                  objectFit: "contain",
                  borderRadius: "12px",
                }}
              />
            ) : (
              <>
                <div className="play-icon">▶</div>

                <h2>AYRA VIDEO PREVIEW</h2>

                <p>
                  Your generated video will appear here.
                </p>
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
