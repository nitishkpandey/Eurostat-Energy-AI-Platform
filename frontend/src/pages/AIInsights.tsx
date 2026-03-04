/** AI Insights page – ask natural-language questions about the energy data. */
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { askInsight } from "../api/client";
import Spinner from "../components/Spinner";
import ErrorAlert from "../components/ErrorAlert";

const EXAMPLE_QUESTIONS = [
  "Which country's GEP is rising fastest?",
  "Which regions have declining final energy consumption?",
  "Show countries with stable GEP trends",
  "What is the average energy production in Europe?",
  "Compare energy consumption across sectors",
];

export default function AIInsights() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<{ q: string; answer: string; mode: string }[]>([]);

  const { mutate, isPending, error } = useMutation({
    mutationFn: askInsight,
    onSuccess: (data) => {
      setHistory((prev) => [{ q: question, answer: data.answer, mode: data.mode }, ...prev]);
      setQuestion("");
    },
  });

  const handleAsk = () => {
    if (!question.trim()) return;
    mutate(question.trim());
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">AI Insights</h2>
        <p className="text-sm text-slate-400 mt-1">
          Ask natural language questions about European energy data. Powered by semantic search
          (TF-IDF RAG) over precomputed country–indicator insights.
        </p>
      </div>

      {/* Example questions */}
      <div className="card">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
          💡 Example Questions
        </p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => setQuestion(q)}
              className="text-xs px-3 py-1.5 rounded-full bg-primary/15 text-primary hover:bg-primary/30 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="card flex gap-3 items-start">
        <textarea
          className="select-field flex-1 resize-none"
          rows={2}
          placeholder="e.g. Which country has the highest electricity production?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleAsk();
            }
          }}
        />
        <button
          className="btn-primary whitespace-nowrap"
          onClick={handleAsk}
          disabled={isPending || !question.trim()}
        >
          {isPending ? <Spinner size={18} /> : "🔍 Ask AI"}
        </button>
      </div>

      {error && <ErrorAlert message="Failed to get an answer. Please try again." />}

      {/* Answer history */}
      {history.map((item, i) => (
        <div key={i} className="card space-y-3">
          <div className="flex items-start gap-2">
            <span className="text-primary font-bold text-lg">Q</span>
            <p className="text-white text-sm font-medium">{item.q}</p>
          </div>
          <div className="flex items-start gap-2 pt-2 border-t border-border">
            <span className="text-emerald-400 font-bold text-lg">A</span>
            <div className="text-slate-300 text-sm whitespace-pre-line leading-relaxed flex-1">
              {/* Render simple markdown bold (**text**) */}
              {item.answer.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
                part.startsWith("**") && part.endsWith("**") ? (
                  <strong key={j} className="text-white font-semibold">
                    {part.slice(2, -2)}
                  </strong>
                ) : (
                  <span key={j}>{part}</span>
                )
              )}
            </div>
          </div>
          <div className="flex justify-end">
            <span className="text-xs text-slate-500 px-2 py-0.5 rounded-full bg-white/5">
              mode: {item.mode}
            </span>
          </div>
        </div>
      ))}

      {history.length === 0 && !isPending && (
        <div className="card text-center py-12">
          <p className="text-4xl mb-3">🤖</p>
          <p className="text-slate-400">Ask a question above to get AI-powered insights.</p>
        </div>
      )}
    </div>
  );
}
