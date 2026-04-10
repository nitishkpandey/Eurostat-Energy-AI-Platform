import { useState } from "react";

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
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAskAi = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await apiClient.askAi(question.trim());
      setAiResult(response);
    } catch (askError) {
      setError(askError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <div className="page-header">
        <p className="page-kicker">Natural Language Intelligence</p>
        <h2>AI Agent</h2>
      </div>

      {error ? <p className="error-banner">{error}</p> : null}

      <section className="quick-questions-inline" aria-label="Suggested prompts">
        <div className="quick-questions-list">
          {QUICK_QUESTIONS.map((candidate) => (
            <button
              key={candidate}
              type="button"
              className="outline-button prompt-capsule-button"
              onClick={() => setQuestion(candidate)}
            >
              {candidate}
            </button>
          ))}
        </div>
      </section>

      <Panel
        title="Ask a Question"
        eyebrow="Assistant Prompt"
        subtitle="Prompt the assistant with a focused operational question."
      >
        <div className="ai-input">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Which countries have the strongest increase in gross electricity production over the last decade?"
            rows={4}
          />
          <button onClick={handleAskAi} type="button" disabled={loading}>
            {loading ? "Thinking..." : "Ask AI Agent"}
          </button>
        </div>
      </Panel>

      {loading && !aiResult ? <p className="status-banner">Analyzing data context...</p> : null}

      {aiResult ? (
        <Panel title="AI Response" eyebrow="Generated Insight" subtitle={`Mode: ${aiResult.mode || "standard"}`}>
          <article className="ai-response">
            <p>{aiResult.answer}</p>
          </article>
        </Panel>
      ) : null}
    </div>
  );
}

export default AiAgentPage;
