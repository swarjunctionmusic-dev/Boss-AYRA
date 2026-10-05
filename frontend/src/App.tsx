import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

type ChatMessage = {
  role: "user" | "ayra";
  text: string;
};

type Memory = {
  id: number;
  content: string;
  category: string;
  created_at: string;
};

type Task = {
  id: number;
  title: string;
  description: string;
  status: string;
};

function App() {
  const [activeTab, setActiveTab] = useState("Chat");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [voiceListening, setVoiceListening] = useState(false);

  const [memories, setMemories] = useState<Memory[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [memoryInput, setMemoryInput] = useState("");
  const [taskInput, setTaskInput] = useState("");

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "ayra",
      text: "Hi Boss 👋 I'm ready. Memory, tasks, voice, research, creation — tell me what you need.",
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

  const loadMemory = async () => {
    try {
      const response = await fetch(`${API}/api/memory`);
      const data = await response.json();
      setMemories(data.memories ?? []);
    } catch {
      console.error("Memory service unavailable");
    }
  };

  const loadTasks = async () => {
    try {
      const response = await fetch(`${API}/api/tasks`);
      const data = await response.json();
      setTasks(data.tasks ?? []);
    } catch {
      console.error("Task service unavailable");
    }
  };

  useEffect(() => {
    loadMemory();
    loadTasks();
  }, []);

  const handleSend = async (voiceText?: string) => {
    const text = (voiceText ?? message).trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Server error: ${response.status}`);
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
          text: "Sorry Boss, AYRA backend se connection/API issue aa raha hai. Backend check karo.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startVoiceInput = () => {
    const browser = window as any;
    const SpeechRecognition =
      browser.SpeechRecognition || browser.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setMessages((previous) => [
        ...previous,
        {
          role: "ayra",
          text: "Boss, is browser mein speech recognition available nahi hai. Chrome mein try karo.",
        },
      ]);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.continuous = false;

    setVoiceListening(true);

    recognition.onresult = (event: any) => {
      const text = event.results?.[0]?.[0]?.transcript ?? "";
      if (text) {
        setMessage(text);
        handleSend(text);
      }
    };

    recognition.onerror = () => setVoiceListening(false);
    recognition.onend = () => setVoiceListening(false);

    recognition.start();
  };

  const speak = async (text: string) => {
    if (!text || speaking) return;

    try {
      setSpeaking(true);

      const response = await fetch(`${API}/api/speech`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error("Speech API failed");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);

      audio.onended = () => {
        URL.revokeObjectURL(url);
        setSpeaking(false);
      };

      await audio.play();
    } catch (error) {
      console.error(error);
      setSpeaking(false);
    }
  };

  const addMemory = async () => {
    const content = memoryInput.trim();
    if (!content) return;

    await fetch(`${API}/api/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content,
        category: "boss",
      }),
    });

    setMemoryInput("");
    await loadMemory();
  };

  const removeMemory = async (id: number) => {
    await fetch(`${API}/api/memory/${id}`, {
      method: "DELETE",
    });

    await loadMemory();
  };

  const addTask = async () => {
    const title = taskInput.trim();
    if (!title) return;

    await fetch(`${API}/api/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });

    setTaskInput("");
    await loadTasks();
  };

  const completeTask = async (id: number) => {
    await fetch(`${API}/api/tasks/${id}/complete`, {
      method: "POST",
    });

    await loadTasks();
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
            <span className="eyebrow">AYRA COMMAND CENTER</span>
            <h2>{activeTab}</h2>
          </div>

          <div className="top-actions">
            <button className="boss-button">
              <span className="status-dot"></span>
              BOSS
            </button>
          </div>
        </header>

        {activeTab === "Chat" && (
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
                <span className="eyebrow">AYRA CORE v0.1.1</span>
                <h3>Ready when you are, Boss.</h3>
                <p>
                  Chat, persistent memory, tasks and voice are now connected.
                </p>

                <div className="hero-buttons">
                  <button
                    className="primary-button"
                    onClick={() => setActiveTab("Voice")}
                  >
                    🎙️ Voice Mode
                  </button>
                  <button
                    className="secondary-button"
                    onClick={() => setActiveTab("Tasks")}
                  >
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
                  <strong>{memories.length} Saved</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>⚡</span>
                <div>
                  <small>Tasks</small>
                  <strong>{tasks.length} Total</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>🎙️</span>
                <div>
                  <small>Voice</small>
                  <strong>Ready</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>🎬</span>
                <div>
                  <small>Studio</small>
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
                      {chat.role === "ayra" && (
                        <button
                          className="small-button"
                          onClick={() => speak(chat.text)}
                          title="Speak"
                        >
                          🔊
                        </button>
                      )}
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
                    <button
                      className="small-button"
                      onClick={startVoiceInput}
                      title="Voice input"
                    >
                      {voiceListening ? "🔴" : "🎙️"}
                    </button>
                  </div>

                  <button
                    className="send-button"
                    onClick={() => handleSend()}
                    disabled={loading}
                  >
                    {loading ? "Thinking..." : "Send ➤"}
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === "Voice" && (
          <section className="dashboard">
            <div className="hero-card">
              <div className="ayra-avatar">
                <div className="avatar-ring"></div>
                <div className="avatar-face">
                  <div className="eye left"></div>
                  <div className="eye right"></div>
                  <div className="mouth"></div>
                </div>
              </div>

              <div className="hero-content">
                <span className="eyebrow">VOICE COMMAND</span>
                <h3>{voiceListening ? "I'm listening, Boss..." : "Talk to AYRA"}</h3>
                <p>
                  Browser microphone input + AYRA voice output.
                </p>

                <div className="hero-buttons">
                  <button
                    className="primary-button"
                    onClick={startVoiceInput}
                  >
                    {voiceListening ? "🔴 Listening..." : "🎙️ Start Listening"}
                  </button>

                  <button
                    className="secondary-button"
                    disabled={speaking}
                    onClick={() =>
                      speak("Hi Boss. AYRA is online and ready for your command.")
                    }
                  >
                    {speaking ? "🔊 Speaking..." : "🔊 Test AYRA Voice"}
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === "Memory" && (
          <section className="dashboard">
            <div className="chat-card">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">PERSISTENT MEMORY</span>
                  <h3>AYRA Memory</h3>
                </div>
              </div>

              <div className="chat-input-area">
                <textarea
                  value={memoryInput}
                  onChange={(e) => setMemoryInput(e.target.value)}
                  placeholder="Tell AYRA something to remember..."
                />
                <div className="input-actions">
                  <button className="send-button" onClick={addMemory}>
                    Save Memory +
                  </button>
                </div>
              </div>

              <div className="welcome-message">
                <div className="mini-avatar">🧠</div>
                <div>
                  {memories.length === 0 && (
                    <p>No memories saved yet.</p>
                  )}

                  {memories.map((memory) => (
                    <p key={memory.id}>
                      <strong>{memory.category}:</strong> {memory.content}
                      {" "}
                      <button
                        className="small-button"
                        onClick={() => removeMemory(memory.id)}
                      >
                        🗑️
                      </button>
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === "Tasks" && (
          <section className="dashboard">
            <div className="chat-card">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">TASK AUTOMATION</span>
                  <h3>Boss Tasks</h3>
                </div>
              </div>

              <div className="chat-input-area">
                <textarea
                  value={taskInput}
                  onChange={(e) => setTaskInput(e.target.value)}
                  placeholder="Add a task for AYRA..."
                />

                <div className="input-actions">
                  <button className="send-button" onClick={addTask}>
                    Create Task +
                  </button>
                </div>
              </div>

              <div className="welcome-message">
                <div className="mini-avatar">⚡</div>
                <div>
                  {tasks.length === 0 && <p>No tasks yet.</p>}

                  {tasks.map((task) => (
                    <p key={task.id}>
                      {task.status === "completed" ? "✅ " : "⏳ "}
                      <strong>{task.title}</strong>
                      {task.status !== "completed" && (
                        <button
                          className="small-button"
                          onClick={() => completeTask(task.id)}
                        >
                          ✓
                        </button>
                      )}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {activeTab === "Studio" && (
          <section className="studio-page">
            <div className="studio-heading">
              <div>
                <span className="eyebrow">GENERATED MEDIA</span>
                <h3>AYRA Studio</h3>
                <p>
                  Connected to the existing AYRA Studio video pipeline.
                </p>
              </div>

              <span className="studio-status">
                <span className="status-dot"></span>
                READY
              </span>
            </div>

            <div className="video-card">
              <div className="video-header">
                <div>
                  <span className="eyebrow">VIDEO ENGINE</span>
                  <h3>LTX + Free WAN</h3>
                </div>
                <span className="video-provider">AI VIDEO</span>
              </div>

              <div className="video-info">
                <div>
                  <small>Backend</small>
                  <strong>AYRA Studio :8000</strong>
                </div>

                <div>
                  <small>Provider</small>
                  <strong>LTX</strong>
                </div>

                <div>
                  <small>Fallback</small>
                  <strong>Free WAN</strong>
                </div>

                <div>
                  <small>Status</small>
                  <strong className="success-text">Connected</strong>
                </div>
              </div>

              <div className="hero-buttons">
                <button
                  className="primary-button"
                  onClick={() => window.open("http://localhost:5173", "_blank")}
                >
                  🎬 Open Studio
                </button>
              </div>
            </div>
          </section>
        )}

        {(activeTab === "Research" ||
          activeTab === "Files" ||
          activeTab === "Computer") && (
          <section className="dashboard">
            <div className="hero-card">
              <div className="hero-content">
                <span className="eyebrow">MODULE FOUNDATION</span>
                <h3>{activeTab} module</h3>
                <p>
                  AYRA Core is ready. This module is reserved for the next
                  integration milestone.
                </p>

                <div className="hero-buttons">
                  <button
                    className="primary-button"
                    onClick={() => setActiveTab("Chat")}
                  >
                    💬 Back to Chat
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
