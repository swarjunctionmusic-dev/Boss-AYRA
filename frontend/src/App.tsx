import { useState } from "react";
import "./App.css";

type ChatMessage = {
  role: "user" | "ayra";
  text: string;
};

function App() {
  const [activeTab, setActiveTab] = useState("Chat");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "ayra",
      text: "Hi Boss 👋 I'm ready. Tell me what you want to research, create, automate or control.",
    },
  ]);

  const menuItems = [
    { name: "Chat", icon: "💬" },
    { name: "Voice", icon: "🎙️" },
    { name: "Tasks", icon: "⚡" },
    { name: "Research", icon: "🔎" },
    { name: "Files", icon: "📁" },
    { name: "Memory", icon: "🧠" },
    { name: "Computer", icon: "💻" },
    { name: "Studio", icon: "🎬" },
  ];

  const handleSend = async () => {
    const text = message.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "ayra",
          text: data.reply,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          role: "ayra",
          text: "Sorry Boss, backend se connection nahi ho pa raha. Please check karo ki AYRA backend running hai.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ayra-app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-orb">A</div>
          <div>
            <h1>AYRA</h1>
            <span>PERSONAL AI</span>
          </div>
        </div>

        <div className="boss-card">
          <div className="status-dot"></div>
          <div>
            <strong>Boss Mode</strong>
            <small>System Online</small>
          </div>
        </div>

        <nav>
          {menuItems.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activeTab === item.name ? "active" : ""}`}
              onClick={() => setActiveTab(item.name)}
            >
              <span>{item.icon}</span>
              {item.name}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <span>⚙️</span>
            Settings
          </button>

          <div className="system-status">
            <span className="status-dot"></span>
            <div>
              <strong>All Systems</strong>
              <small>Operational</small>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">
              {activeTab === "Studio" ? "AI VIDEO STUDIO" : "COMMAND CENTER"}
            </span>
            <h2>{activeTab}</h2>
          </div>

          <div className="top-actions">
            <button className="icon-button">🔔</button>
            <button className="boss-button">
              <span className="status-dot"></span>
              BOSS
            </button>
          </div>
        </header>

        {activeTab === "Studio" ? (
          <section className="studio-page">
            <div className="studio-heading">
              <div>
                <span className="eyebrow">GENERATED MEDIA</span>
                <h3>AYRA Studio</h3>
                <p>
                  Real AI-generated video from the AYRA Director → LTX pipeline.
                </p>
              </div>

              <span className="studio-status">
                <span className="status-dot"></span>
                VIDEO READY
              </span>
            </div>

            <div className="video-card">
              <div className="video-header">
                <div>
                  <span className="eyebrow">SCENE 01</span>
                  <h3>The Last Light</h3>
                </div>
                <span className="video-provider">
                  LTX VIDEO
                </span>
              </div>

              <div className="video-preview">
                <video
                  controls
                  preload="metadata"
                  src="/generated/scene-01.mp4"
                >
                  Your browser does not support video playback.
                </video>
              </div>

              <div className="video-info">
                <div>
                  <small>Provider</small>
                  <strong>Lightricks LTX Video</strong>
                </div>

                <div>
                  <small>Pipeline</small>
                  <strong>Director → LTX</strong>
                </div>

                <div>
                  <small>Format</small>
                  <strong>MP4</strong>
                </div>

                <div>
                  <small>Status</small>
                  <strong className="success-text">Generated</strong>
                </div>
              </div>
            </div>

            <div className="studio-scenes">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">TIMELINE</span>
                  <h3>Generated Scenes</h3>
                </div>
              </div>

              <div className="scene-strip">
                <div className="scene-card active-scene">
                  <span>01</span>
                  <strong>Scene 01</strong>
                  <small>Generated MP4</small>
                </div>

                <div className="scene-card">
                  <span>02</span>
                  <strong>Scene 02</strong>
                  <small>Waiting</small>
                </div>

                <div className="scene-card">
                  <span>03</span>
                  <strong>Scene 03</strong>
                  <small>Waiting</small>
                </div>

                <div className="scene-card">
                  <span>04</span>
                  <strong>Scene 04</strong>
                  <small>Waiting</small>
                </div>

                <div className="scene-card">
                  <span>05</span>
                  <strong>Scene 05</strong>
                  <small>Waiting</small>
                </div>

                <div className="scene-card">
                  <span>06</span>
                  <strong>Scene 06</strong>
                  <small>Waiting</small>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <section className="dashboard">
            <div className="hero-card">
              <div className="hero-glow"></div>

              <div className="ayra-avatar">
                <div className="avatar-ring"></div>
                <div className="avatar-face">
                  <div className="eye left"></div>
                  <div className="eye right"></div>
                  <div className="mouth"></div>
                </div>
              </div>

              <div className="hero-content">
                <span className="eyebrow">AYRA CORE</span>
                <h3>Ready when you are, Boss.</h3>
                <p>
                  Your personal AI command center for conversations,
                  research, automation, files and computer control.
                </p>

                <div className="hero-buttons">
                  <button className="primary-button">
                    🎙️ Start Voice Mode
                  </button>
                  <button className="secondary-button">
                    ⚡ New Task
                  </button>
                </div>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <span>🧠</span>
                <div>
                  <small>Memory</small>
                  <strong>Ready</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>🔎</span>
                <div>
                  <small>Research</small>
                  <strong>Online</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>💻</span>
                <div>
                  <small>Computer</small>
                  <strong>Connected</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>🎬</span>
                <div>
                  <small>AYRA Studio</small>
                  <strong>Ready</strong>
                </div>
              </div>
            </div>

            <div className="chat-card">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">CONVERSATION</span>
                  <h3>Talk to AYRA</h3>
                </div>

                <span className="online-badge">
                  <span className="status-dot"></span>
                  ONLINE
                </span>
              </div>

              <div className="welcome-message">
                <div className="mini-avatar">A</div>

                <div>
                  <strong>AYRA</strong>

                  {messages.map((chat, index) => (
                    <p key={index}>
                      {chat.role === "user" ? "👤 " : ""}
                      {chat.text}
                    </p>
                  ))}

                  {loading && <p>AYRA is thinking... 🧠</p>}
                </div>
              </div>

              <div className="chat-input-area">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type a command for AYRA..."
                  disabled={loading}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                />

                <div className="input-actions">
                  <div>
                    <button className="small-button">📎</button>
                    <button className="small-button">🎙️</button>
                  </div>

                  <button
                    className="send-button"
                    onClick={handleSend}
                    disabled={loading}
                  >
                    {loading ? "Thinking..." : "Send ➤"}
                  </button>
                </div>
              </div>
            </div>

            <div className="quick-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">SHORTCUTS</span>
                  <h3>Quick Actions</h3>
                </div>
              </div>

              <div className="quick-grid">
                <button>
                  <span>🔬</span>
                  <strong>Research</strong>
                  <small>Deep research a topic</small>
                </button>

                <button onClick={() => setActiveTab("Studio")}>
                  <span>🎬</span>
                  <strong>Create Video</strong>
                  <small>Open AYRA Studio</small>
                </button>

                <button>
                  <span>💻</span>
                  <strong>Control Computer</strong>
                  <small>Manage your PC</small>
                </button>

                <button>
                  <span>📁</span>
                  <strong>Manage Files</strong>
                  <small>Work with your files</small>
                </button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
