import { useState } from "react";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("Chat");
  const [message, setMessage] = useState("");

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

  const handleSend = () => {
    if (!message.trim()) return;
    setMessage("");
  };

  return (
    <div className="ayra-app">

      {/* SIDEBAR */}
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
              className={`nav-item ${
                activeTab === item.name ? "active" : ""
              }`}
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

      {/* MAIN AREA */}
      <main className="main">

        {/* TOP BAR */}
        <header className="topbar">
          <div>
            <span className="eyebrow">COMMAND CENTER</span>
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

        {/* DASHBOARD */}
        <section className="dashboard">

          {/* HERO */}
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

          {/* QUICK STATS */}
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

          {/* CHAT */}
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
                <p>
                  Hi Boss 👋 I'm ready. Tell me what you want to
                  research, create, automate or control.
                </p>
              </div>
            </div>

            <div className="chat-input-area">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a command for AYRA..."
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
                >
                  Send ➤
                </button>
              </div>
            </div>
          </div>

          {/* QUICK ACTIONS */}
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

              <button>
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
      </main>
    </div>
  );
}

export default App;