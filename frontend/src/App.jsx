import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I'm TechWise. I can help you record, retrieve, and evaluate software engineering decisions."
    }
  ]);

  const [loading, setLoading] = useState(false);

  // Load saved theme
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("techwise-theme") === "dark";
  });

  // Save theme whenever it changes
  useEffect(() => {
    localStorage.setItem(
      "techwise-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMessage = message.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: userMessage
      }
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: userMessage
          })
        }
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            data.response ||
            "I couldn't generate a response."
        }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            "TechWise is currently unable to process your request. Please make sure the backend is running and try again."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const useSuggestion = (text) => {
    setMessage(text);
  };

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>

      {/* ================= HEADER ================= */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            T
          </div>

          <div>
            <h1>TechWise</h1>

            <p>
              AI Software Engineering Decision Agent
            </p>
          </div>

        </div>

        <div className="header-actions">

          <div className="status">
            <span className="status-dot"></span>
            Agent Online
          </div>

          <button
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle theme"
          >
            {darkMode ? "☀" : "☾"}
          </button>

        </div>

      </header>


      {/* ================= MAIN ================= */}

      <main className="main">

        {/* ================= LEFT SIDEBAR ================= */}

        <aside className="sidebar">

          <div className="sidebar-heading">

            <div>
              <h2>TechWise Agent</h2>

              <p>
                What the agent can do
              </p>
            </div>

          </div>


          {/* FEATURE 1 */}

          <div className="feature-card">

            <div className="feature-icon memory">
              🧠
            </div>

            <div className="feature-content">

              <h3>Decision Memory</h3>

              <p>
                Store software engineering decisions
                with their context and reasoning.
              </p>

              <span className="tool-label">
                record_decision
              </span>

            </div>

          </div>


          {/* FEATURE 2 */}

          <div className="feature-card">

            <div className="feature-icon search">
              🔎
            </div>

            <div className="feature-content">

              <h3>Decision Retrieval</h3>

              <p>
                Search previous decisions and
                understand why they were made.
              </p>

              <span className="tool-label">
                retrieve_decisions
              </span>

            </div>

          </div>


          {/* FEATURE 3 */}

          <div className="feature-card">

            <div className="feature-icon impact">
              ⚡
            </div>

            <div className="feature-content">

              <h3>Impact Analysis</h3>

              <p>
                Evaluate whether an existing decision
                still fits a changed requirement.
              </p>

              <span className="tool-label">
                analyze_impact
              </span>

            </div>

          </div>


          {/* QUICK ACTIONS */}

          <div className="quick-actions">

            <h3>Quick Actions</h3>

            <button
              onClick={() =>
                useSuggestion(
                  "Record a new software engineering decision"
                )
              }
            >
              <span>＋</span>
              Record a decision
            </button>

            <button
              onClick={() =>
                useSuggestion(
                  "Why did we choose React?"
                )
              }
            >
              <span>🔎</span>
              Search memory
            </button>

            <button
              onClick={() =>
                useSuggestion(
                  "Should we reconsider our current technology choice?"
                )
              }
            >
              <span>⚡</span>
              Evaluate decision
            </button>

          </div>

        </aside>


        {/* ================= CHAT ================= */}

        <section className="chat-section">

          <div className="chat-card">

            {/* CHAT HEADER */}

            <div className="chat-header">

              <div className="chat-title">

                <div className="chat-avatar">
                  T
                </div>

                <div>
                  <h2>Decision Assistant</h2>

                  <p>
                    Ask TechWise about your
                    software engineering decisions.
                  </p>
                </div>

              </div>

              <div className="chat-status">
                ● Ready
              </div>

            </div>


            {/* CHAT BODY */}

            <div className="messages">

              {messages.map((msg, index) => (

                <div
                  key={index}
                  className={`message ${msg.role}`}
                >

                  {msg.role === "assistant" && (
                    <div className="message-avatar">
                      T
                    </div>
                  )}

                  <div className="message-content">

                    <div className="message-label">
                      {msg.role === "user"
                        ? "You"
                        : "TechWise"}
                    </div>

                    <div className="message-bubble">
                      {msg.text}
                    </div>

                  </div>

                </div>

              ))}


              {/* THINKING */}

              {loading && (

                <div className="message assistant">

                  <div className="message-avatar">
                    T
                  </div>

                  <div className="message-content">

                    <div className="message-label">
                      TechWise
                    </div>

                    <div className="message-bubble thinking">

                      <span></span>
                      <span></span>
                      <span></span>

                      <em>
                        Thinking...
                      </em>

                    </div>

                  </div>

                </div>

              )}

            </div>


            {/* SUGGESTIONS */}

            <div className="suggestions">

              <button
                onClick={() =>
                  useSuggestion(
                    "Why did we choose React?"
                  )
                }
              >
                Why did we choose React?
              </button>

              <button
                onClick={() =>
                  useSuggestion(
                    "Record a new software engineering decision"
                  )
                }
              >
                Record a decision
              </button>

              <button
                onClick={() =>
                  useSuggestion(
                    "Should we reconsider our current technology choice?"
                  )
                }
              >
                Evaluate a decision
              </button>

            </div>


            {/* INPUT */}

            <div className="input-area">

              <textarea
                value={message}
                onChange={(e) =>
                  setMessage(e.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask TechWise about a software decision..."
                rows="2"
              />

              <button
                className="send-button"
                onClick={sendMessage}
                disabled={
                  loading ||
                  !message.trim()
                }
              >
                {loading ? "..." : "Send"}

                {!loading && (
                  <span>➜</span>
                )}
              </button>

            </div>


            <p className="input-hint">
              Enter to send&nbsp;&nbsp;•&nbsp;&nbsp;
              Shift + Enter for a new line
            </p>

          </div>

        </section>

      </main>


      {/* ================= FOOTER ================= */}

      <footer>

        <span>TechWise</span>

        <span>LLM</span>

        <span>Agent Tools</span>

        <span>Persistent Memory</span>

      </footer>

    </div>
  );
}

export default App;