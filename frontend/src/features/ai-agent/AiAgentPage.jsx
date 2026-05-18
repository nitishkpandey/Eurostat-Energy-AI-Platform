import { useState, useRef, useEffect } from "react";
import { apiClient } from "../../shared/api/client";
import { Panel } from "../../shared/ui/Panel";

const QUICK_QUESTIONS = [
  "Which country is accelerating GEP growth fastest?",
  "Where is final consumption declining most consistently?",
  "Compare transport vs household demand trajectory.",
  "Which countries have stable long-term GEP trends?",
];

export function AiAgentPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleAskAi = async (overrideQuestion = null) => {
    const textToAsk = overrideQuestion || question;
    if (!textToAsk.trim()) return;

    const userMessage = { role: "user", content: textToAsk.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      // Pass the conversation history to the API for context-aware answers.
      const response = await apiClient.askAi(textToAsk.trim(), messages);
      const aiMessage = { 
        role: "assistant", 
        content: response.answer, 
        mode: response.mode 
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (askError) {
      setError(askError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content ai-page">
      <div className="page-header">
        <p className="page-kicker">Natural Language Intelligence</p>
        <h2>AI Agent</h2>
      </div>

      {error ? <p className="error-banner">{error}</p> : null}

      <div className="chat-layout" style={{ display: "grid", gap: "1.5rem" }}>
        {messages.length === 0 ? (
          <section className="quick-questions-inline" aria-label="Suggested prompts">
            <p style={{ color: "var(--text-muted)", marginBottom: "0.8rem", fontSize: "0.9rem" }}>Try asking:</p>
            <div className="quick-questions-list" style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {QUICK_QUESTIONS.map((candidate) => (
                <button
                  key={candidate}
                  type="button"
                  className="outline-button prompt-capsule-button"
                  onClick={() => handleAskAi(candidate)}
                >
                  {candidate}
                </button>
              ))}
            </div>
          </section>
        ) : (
          <Panel title="Conversation" eyebrow="Chat History">
            <div className="chat-history" style={{ maxHeight: "50vh", overflowY: "auto", padding: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              {messages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`chat-message ${msg.role}`}
                  style={{
                    alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                    backgroundColor: msg.role === "user" ? "var(--brand)" : "var(--surface-3)",
                    color: msg.role === "user" ? "#fff" : "var(--text)",
                    padding: "0.8rem 1.2rem",
                    borderRadius: "12px",
                    maxWidth: "80%",
                    boxShadow: "var(--shadow-sm)"
                  }}
                >
                  {msg.role === "assistant" && msg.mode && (
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "0.4rem", textTransform: "uppercase" }}>
                      Mode: {msg.mode}
                    </div>
                  )}
                  <div style={{ whiteSpace: "pre-wrap", lineHeight: "1.5" }}>{msg.content}</div>
                </div>
              ))}
              {loading && (
                <div style={{ alignSelf: "flex-start", padding: "0.8rem 1.2rem", color: "var(--text-muted)" }}>
                  Analyzing data context...
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          </Panel>
        )}

        <Panel
          title="Ask a Question"
          eyebrow="Assistant Prompt"
        >
          <div className="ai-input" style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAskAi();
                }
              }}
              placeholder="Which countries have the strongest increase in gross electricity production over the last decade?"
              rows={2}
              style={{ flex: 1 }}
            />
            <button onClick={() => handleAskAi()} type="button" disabled={loading}>
              {loading ? "Thinking..." : "Send"}
            </button>
          </div>
        </Panel>
      </div>
    </div>
  );
}

export default AiAgentPage;
