"use client";

import React, { useEffect, useRef, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import type { AuditEvent, CopilotMessage } from "@/lib/types";
import { Sparkles, Send, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

/**
 * AEGIS COPILOT — AI security analyst over your real audit data.
 *
 * PROTOTYPE SCOPE (honest): the backend has no /copilot endpoint yet.
 * This interface runs a transparent, rule-based analyst over the
 * live audit trail loaded from the real API. When the backend exposes
 * /api/v1/copilot, answerQuestion() is the single seam to replace.
 */

const SUGGESTED_QUESTIONS = [
  "Why was this action blocked?",
  "Show me the highest-risk event today.",
  "Which agent has the highest risk?",
  "Are any credentials exposed?",
  "What caused my security score to drop?",
  "Explain this prompt injection.",
];

let messageId = 0;
const nextId = () => `msg_${Date.now()}_${messageId++}`;

export default function CopilotPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [conversations] = useState([
    { id: "today", title: "Today's security review" },
    { id: "blocked", title: "Blocked actions analysis" },
  ]);
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: "welcome",
      role: "aegis",
      content:
        "I'm the Aegis Copilot. I answer questions from your live audit trail — events, threats, agents, risk scores and policies. Ask me anything about what your agents did.",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load real audit data the analyst operates over.
  useEffect(() => {
    const load = async () => {
      try {
        const [evaluated, threats, approvals] = await Promise.all([
          api.get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "ACTION_EVALUATED", limit: 100 })).catch(() => [] as AuditEvent[]),
          api.get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "AI_SECURITY_ANALYSIS_COMPLETED", limit: 100 })).catch(() => [] as AuditEvent[]),
          api.get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "APPROVAL_REQUESTED", limit: 100 })).catch(() => [] as AuditEvent[]),
        ]);
        const merged = [...evaluated, ...threats, ...approvals];
        merged.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
        setEvents(merged);
        if (merged.length > 0) setSelectedEvent(merged[0]);
      } finally {
        setEventsLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, thinking]);

  const ask = (question: string) => {
    if (!question.trim() || thinking) return;
    const userMsg: CopilotMessage = {
      id: nextId(),
      role: "user",
      content: question,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setThinking(true);

    // Deterministic analyst — single seam for the future /copilot API.
    setTimeout(() => {
      const answer = analyzeQuestion(question, events);
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: "aegis",
          content: answer.content,
          timestamp: new Date().toISOString(),
          structured: answer.structured,
        },
      ]);
      if (answer.event) setSelectedEvent(answer.event);
      setThinking(false);
    }, 450);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] min-h-[540px] flex-col gap-4">
      <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-[220px_1fr_280px]">
        {/* Left: conversation history */}
        <aside className="panel hidden flex-col overflow-hidden rounded-xl lg:flex" aria-label="Conversation history">
          <div className="border-b border-border-base px-4 py-3">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
              Conversations
            </p>
          </div>
          <ul className="flex-1 overflow-y-auto p-2">
            {conversations.map((c) => (
              <li key={c.id}>
                <button
                  type="button"
                  className="w-full rounded-lg px-3 py-2 text-left text-sm text-foreground-muted transition-colors hover:bg-card-elevated hover:text-foreground"
                >
                  {c.title}
                </button>
              </li>
            ))}
          </ul>
          <p className="border-t border-border-base p-3 text-[10px] leading-relaxed text-foreground-muted">
            Prototype: deterministic analyst over live audit data. LLM-backed
            answers arrive with the /copilot API.
          </p>
        </aside>

        {/* Center: conversation */}
        <section className="panel flex flex-col overflow-hidden rounded-xl" aria-label="Copilot conversation">
          <div className="flex items-center justify-between border-b border-border-base px-5 py-3">
            <span className="inline-flex items-center gap-2 text-[11px] font-semibold tracking-[0.18em] text-foreground-muted">
              <Sparkles className="h-4 w-4 text-accent" aria-hidden="true" />
              AEGIS COPILOT
            </span>
            <span className="font-mono text-[10px] text-foreground-muted">
              {eventsLoading ? "loading audit trail…" : `${events.length} events analyzed`}
            </span>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "max-w-[85%] rounded-xl px-4 py-3",
                  message.role === "user"
                    ? "ml-auto rounded-tr-sm border border-border-base bg-card-elevated"
                    : "rounded-tl-sm border border-accent-border/30 bg-accent-dim/30"
                )}
              >
                <p className="text-sm leading-relaxed text-foreground">
                  {message.content}
                </p>
                {message.structured && (
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    {message.structured.risk !== undefined && (
                      <span className="rounded-full border border-border-strong bg-card px-2.5 py-0.5 font-mono text-[10px] text-foreground-muted">
                        Risk: <span className="font-semibold text-block">{message.structured.risk} / 100</span>
                      </span>
                    )}
                    {message.structured.level && (
                      <span className="rounded-full border border-border-strong bg-card px-2.5 py-0.5 font-mono text-[10px] text-foreground-muted">
                        Level: <span className="font-semibold text-foreground">{message.structured.level}</span>
                      </span>
                    )}
                    {message.structured.policy && (
                      <span className="rounded-full border border-border-strong bg-card px-2.5 py-0.5 font-mono text-[10px] text-foreground-muted">
                        Policy: <span className="font-semibold text-foreground">{message.structured.policy}</span>
                      </span>
                    )}
                    {message.structured.agent && (
                      <span className="rounded-full border border-border-strong bg-card px-2.5 py-0.5 font-mono text-[10px] text-foreground-muted">
                        Agent: <span className="font-semibold text-foreground">{message.structured.agent}</span>
                      </span>
                    )}
                  </div>
                )}
                <p className={cn("mt-2 text-right font-mono text-[10px] text-foreground-muted", message.role === "aegis" && "text-left")}>
                  {format(new Date(message.timestamp), "HH:mm:ss")}
                </p>
              </div>
            ))}
            {thinking && (
              <div className="max-w-[60%] rounded-xl rounded-tl-sm border border-accent-border/30 bg-accent-dim/20 px-4 py-3">
                <p className="flex items-center gap-2 text-sm text-foreground-muted">
                  <span className="h-1.5 w-1.5 rounded-full bg-accent pulse-dot" aria-hidden="true" />
                  Analyzing audit trail…
                </p>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Suggested questions */}
          <div className="flex flex-wrap gap-2 border-t border-border-base px-5 py-3">
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => ask(q)}
                className="rounded-full border border-border-base bg-card px-3 py-1 text-xs text-foreground-muted transition-colors hover:border-border-strong hover:text-foreground"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <form
            className="flex items-center gap-3 border-t border-border-base px-5 py-4"
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
          >
            <label htmlFor="copilot-input" className="sr-only">
              Ask the Aegis Copilot
            </label>
            <input
              id="copilot-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about threats, agents, policies…"
              className="glass-input flex-1 px-3.5 py-2.5 text-sm placeholder:text-foreground-muted/60"
            />
            <button
              type="submit"
              disabled={!input.trim() || thinking}
              aria-label="Send question"
              className="btn-primary disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Send className="h-4 w-4" aria-hidden="true" />
            </button>
          </form>
        </section>

        {/* Right: security context */}
        <aside className="panel hidden flex-col overflow-hidden rounded-xl lg:flex" aria-label="Security context">
          <div className="border-b border-border-base px-4 py-3">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
              Security context
            </p>
          </div>
          {selectedEvent ? (
            <div className="flex-1 space-y-4 overflow-y-auto p-4 text-sm">
              <ContextRow label="Event" value={selectedEvent.event_type.replace(/_/g, " ")} />
              <ContextRow label="Time" value={format(new Date(selectedEvent.timestamp), "MMM d, HH:mm:ss")} />
              <ContextRow
                label="Decision"
                value={selectedEvent.final_decision ?? "—"}
                tone={
                  selectedEvent.final_decision === "BLOCK"
                    ? "text-block"
                    : selectedEvent.final_decision === "REVIEW"
                      ? "text-review"
                      : "text-allow"
                }
              />
              {selectedEvent.risk_score !== null && (
                <ContextRow label="Risk" value={`${selectedEvent.risk_score} / 100 · ${selectedEvent.risk_level ?? "—"}`} />
              )}
              {selectedEvent.agent_id && (
                <ContextRow label="Agent" value={`${selectedEvent.agent_id.substring(0, 13)}…`} mono />
              )}
              {selectedEvent.ai_threat_type && (
                <ContextRow label="Threat" value={selectedEvent.ai_threat_type.replace(/_/g, " ")} />
              )}
              {selectedEvent.decision_reasons.length > 0 && (
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">Reasons</p>
                  <ul className="mt-2 space-y-1.5">
                    {selectedEvent.decision_reasons.slice(0, 5).map((reason, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-xs leading-relaxed text-foreground-muted">
                        <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0 text-review" aria-hidden="true" />
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-1 items-center justify-center p-4">
              <p className="text-center text-xs text-foreground-muted">
                {eventsLoading
                  ? "Loading audit events…"
                  : "Ask a question — related events appear here."}
              </p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

function ContextRow({
  label,
  value,
  mono,
  tone,
}: {
  label: string;
  value: string;
  mono?: boolean;
  tone?: string;
}) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-border-base/50 pb-2.5">
      <span className="text-[10px] uppercase tracking-wider text-foreground-muted">{label}</span>
      <span className={cn("text-right text-xs", mono && "font-mono", tone ?? "text-foreground")}>
        {value}
      </span>
    </div>
  );
}

/* ---- Deterministic analyst over the real audit trail ---- */

function analyzeQuestion(
  question: string,
  events: AuditEvent[]
): { content: string; structured?: CopilotMessage["structured"]; event?: AuditEvent } {
  const q = question.toLowerCase();

  const blocked = events.filter((e) => e.final_decision === "BLOCK");
  const withRisk = events.filter((e) => e.risk_score !== null);

  // Why was this action blocked?
  if (q.includes("why") && q.includes("block")) {
    const latest = blocked[0];
    if (!latest) {
      return { content: "No blocked actions are present in the current audit window. Every evaluated action was allowed or sent to review." };
    }
    return {
      content: `The most recent blocked action (${latest.action_id ? latest.action_id.substring(0, 13) + "…" : "unknown"}) was blocked with risk ${latest.risk_score ?? "—"}/100 (${latest.risk_level ?? "—"}). Recorded reasons: ${latest.decision_reasons.slice(0, 3).join("; ") || "see action timeline"}.`,
      structured: {
        risk: latest.risk_score ?? undefined,
        level: latest.risk_level ?? undefined,
        agent: latest.agent_id ? latest.agent_id.substring(0, 8) : undefined,
        actionId: latest.action_id ?? undefined,
      },
      event: latest,
    };
  }

  // Highest-risk event
  if (q.includes("highest-risk") || q.includes("most dangerous") || (q.includes("highest") && q.includes("risk"))) {
    const sorted = [...withRisk].sort((a, b) => (b.risk_score ?? 0) - (a.risk_score ?? 0));
    const top = sorted[0];
    if (!top) {
      return { content: "No risk-scored events are available in the current audit window yet." };
    }
    return {
      content: `The highest-risk event was a ${top.final_decision ?? "evaluated"} action (risk ${top.risk_score}/100, ${top.risk_level}) at ${format(new Date(top.timestamp), "HH:mm:ss")}. ${top.ai_threat_type ? `AI threat classification: ${top.ai_threat_type.replace(/_/g, " ").toLowerCase()}. ` : ""}${top.decision_reasons[0] ?? ""}`,
      structured: {
        risk: top.risk_score ?? undefined,
        level: top.risk_level ?? undefined,
        agent: top.agent_id ? top.agent_id.substring(0, 8) : undefined,
      },
      event: top,
    };
  }

  // Which agent has the highest risk?
  if (q.includes("agent") && (q.includes("highest") || q.includes("risk"))) {
    const byAgent = new Map<string, { max: number; level: string }>();
    withRisk.forEach((e) => {
      if (!e.agent_id) return;
      const cur = byAgent.get(e.agent_id);
      if (!cur || (e.risk_score ?? 0) > cur.max) {
        byAgent.set(e.agent_id, { max: e.risk_score ?? 0, level: e.risk_level ?? "—" });
      }
    });
    const ranked = Array.from(byAgent.entries()).sort((a, b) => b[1].max - a[1].max);
    if (ranked.length === 0) {
      return { content: "No agent activity with risk scores is recorded in the current audit window." };
    }
    const [agentId, { max, level }] = ranked[0];
    return {
      content: `The highest-risk agent is ${agentId.substring(0, 13)}… with a peak risk score of ${max}/100 (${level}) across ${withRisk.filter((e) => e.agent_id === agentId).length} scored actions.`,
      structured: { agent: agentId.substring(0, 8), risk: max, level },
    };
  }

  // Credentials exposed?
  if (q.includes("credential") || q.includes("exposed") || q.includes("secret")) {
    const redacted = events.filter(
      (e) =>
        e.redacted_parameters &&
        Object.values(e.redacted_parameters).some(
          (v) => v === "[REDACTED]"
        )
    );
    if (redacted.length === 0) {
      return { content: "No sensitive values appeared in recent actions. Aegis redacts keys, tokens and credentials before they reach the audit trail — check the Sensitive Data page for redaction markers." };
    }
    return {
      content: `${redacted.length} recent actions contained sensitive parameters. Every value was redacted by Aegis before logging — plaintext secrets are never stored. The most recent is action ${redacted[0].action_id?.substring(0, 13) ?? "unknown"}… from ${redacted[0].timestamp ? format(new Date(redacted[0].timestamp), "HH:mm") : "—"}. Review them on the Sensitive Data page.`,
      event: redacted[0],
    };
  }

  // Security score drop
  if (q.includes("score") && q.includes("drop")) {
    const recent = withRisk.slice(0, 20);
    const avg = recent.length
      ? Math.round(recent.reduce((s, e) => s + (e.risk_score ?? 0), 0) / recent.length)
      : 0;
    return {
      content: recent.length === 0
        ? "No risk-scored activity yet, so the security score hasn't moved. It drops as risk scores and blocked actions accumulate — see Reports for trends."
        : `Recent activity averages a risk score of ${avg}/100 across ${recent.length} actions, with ${blocked.length} blocked in the current window. Blocked actions and high-risk reviews are the primary contributors to score movement. See Reports for the full trend.`,
    };
  }

  // Prompt injection
  if (q.includes("prompt injection") || q.includes("injection")) {
    const injections = events.filter(
      (e) => e.ai_threat_type?.includes("INJECTION") || e.ai_threat_type?.includes("PROMPT")
    );
    if (injections.length === 0) {
      return { content: "No prompt-injection detections are recorded in the current window. AI Security Intelligence analysis must be enabled and a provider configured for semantic injection detection; deterministic detectors cover dangerous patterns, payloads and malformed actions in the meantime." };
    }
    return {
      content: `${injections.length} prompt-injection findings are recorded. The most recent: ${injections[0].ai_threat_type?.replace(/_/g, " ").toLowerCase()} at ${format(new Date(injections[0].timestamp), "HH:mm:ss")}, severity ${injections[0].ai_severity ?? "—"}, decision ${injections[0].final_decision ?? "—"}.`,
      event: injections[0],
    };
  }

  // Default: summary
  const allowCount = events.filter((e) => e.final_decision === "ALLOW").length;
  const reviewCount = events.filter((e) => e.final_decision === "REVIEW").length;
  return {
    content: `From the live audit trail: ${events.length} recent events — ${allowCount} allowed, ${reviewCount} in review, ${blocked.length} blocked. Ask me about blocked actions, highest-risk events, agent risk, credentials or prompt injections for specifics.`,
  };
}
