"use client";

import React, { useState, useRef, useEffect, useSyncExternalStore } from "react";
import { useSafeReducedMotion } from "@/lib/use-safe-reduced-motion";
import { api, ApiError } from "@/lib/api";
import { ArrowRight, Shield } from "lucide-react";

/**
 * Aegis Prompt — the cinematic hero prompt.
 *
 * Cycles security questions with a character-by-character typewriter
 * animation (type → hold → delete → next). Rendering is hydration-safe:
 * the animated text only starts on the client after mount, and the
 * server/first paint always shows the static placeholder.
 * With prefers-reduced-motion, a stable question is shown instead.
 *
 * Visual system: dark solid surface, subtle static border, a single
 * slow lime highlight traveling around the perimeter (see
 * .aegis-prompt-ring in globals.css), soft blurred glow halo, and a
 * broad atmospheric radial glow behind the whole component.
 */

const QUESTIONS = [
  "Show me today's highest-risk agent",
  "Why was this action blocked?",
  "Find suspicious agent activity",
  "Analyze my latest security events",
  "Show me potential prompt injections",
  "Which agent has the highest risk?",
  "Explain the latest threat",
];

const PLACEHOLDER = "Ask Aegis to analyze your agent...";

const TYPE_MS = 55;
const HOLD_MS = 2100;
const DELETE_MS = 26;
const GAP_MS = 500;

const emptySubscribe = () => () => {};
const getSnapshot = () => true;
const getServerSnapshot = () => false;

export function AegisPrompt() {
  const reduceMotion = useSafeReducedMotion();
  // Hydration-safe mounted flag: false during SSR/first paint, true on
  // the client after hydration — no setState inside an effect.
  const mounted = useSyncExternalStore(
    emptySubscribe,
    getSnapshot,
    getServerSnapshot
  );
  const [text, setText] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [inputValue, setInputValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<string | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    if (!mounted || reduceMotion) return;

    let cancelled = false;
    let currentTimer: ReturnType<typeof setTimeout> | null = null;
    
    const schedule = (fn: () => void, ms: number) => {
      if (cancelled) return;
      currentTimer = setTimeout(() => {
        if (!cancelled) fn();
      }, ms);
    };

    const typeQuestion = (qIndex: number, charIndex: number) => {
      if (cancelled) return;
      const question = QUESTIONS[qIndex];
      if (charIndex <= question.length) {
        setText(question.slice(0, charIndex));
        schedule(() => typeQuestion(qIndex, charIndex + 1), TYPE_MS);
      } else {
        // Full question typed — hold, then delete.
        schedule(() => deleteQuestion(qIndex, question.length), HOLD_MS);
      }
    };

    const deleteQuestion = (qIndex: number, charIndex: number) => {
      if (cancelled) return;
      if (charIndex > 0) {
        setText(QUESTIONS[qIndex].slice(0, charIndex - 1));
        schedule(() => deleteQuestion(qIndex, charIndex - 1), DELETE_MS);
      } else {
        const nextIndex = (qIndex + 1) % QUESTIONS.length;
        setQuestionIndex(nextIndex);
        schedule(() => typeQuestion(nextIndex, 0), GAP_MS);
      }
    };

    // Start after the page-load reveal: the prompt wrapper finishes
    // fading in at ~950ms, so typing begins after a deliberate pause.
    schedule(() => typeQuestion(questionIndex, 0), 1400);

    return () => {
      cancelled = true;
      if (currentTimer) clearTimeout(currentTimer);
    };
  }, [mounted, reduceMotion]);

  const showTypewriter = mounted && !reduceMotion;
  const stableQuestion = QUESTIONS[questionIndex];

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const query = inputValue.trim();
    if (!query) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const data = await api.post<{ response: string }>(
        "/api/v1/copilot/ask",
        { query }
      );
      setResponse(data.response);
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        setError("Authentication required. Log in with an API key to ask Aegis.");
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Network error. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="aegis-prompt group relative mx-auto w-full max-w-[740px]"
      tabIndex={0}
      role="group"
      aria-label="Aegis prompt — example questions you can ask about your agents' security"
    >
      {/* Broad atmospheric glow behind the prompt */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-x-6 -inset-y-8 rounded-full bg-accent/[0.04] blur-3xl sm:-inset-x-20 sm:-inset-y-16"
      />

      {/* Soft blurred copy of the perimeter highlight */}
      <div aria-hidden="true" className="aegis-prompt-halo !rounded-[16px]">
        <div className="aegis-prompt-ring aegis-prompt-ring--soft" />
      </div>

      {/* Surface + content. Matching Fused: dark grey #141414, 16px radius, stacked content. */}
      <div className="aegis-prompt-surface relative flex flex-col rounded-[16px] border border-border-base bg-[#141414] p-2">
        <div className="flex items-center gap-3.5 px-4 pt-3 pb-8 sm:px-5">
          <span
            aria-hidden="true"
            className="hidden shrink-0 items-center gap-1.5 rounded-full border border-accent/20 bg-black/40 px-2.5 py-[5px] text-[9px] font-semibold uppercase tracking-[0.18em] text-accent/75 sm:inline-flex"
          >
            <Shield className="h-[11px] w-[11px] text-accent/70" />
            Aegis
          </span>

          <form onSubmit={handleSubmit} className="min-w-0 flex-1 relative flex items-center h-[28px] sm:h-[30px]">
            {(!isFocused && !inputValue) && (
              <div className="pointer-events-none absolute inset-0 flex items-center text-left text-[17px] font-medium leading-normal tracking-[0.01em] text-foreground-secondary sm:text-[19px]">
                {showTypewriter ? (
                  <>
                    <span className="sr-only">Example question: </span>
                    <span aria-hidden="true">
                      {text}
                      <span className="prompt-caret" />
                    </span>
                  </>
                ) : (
                  <span
                    aria-hidden="true"
                    className={mounted && !reduceMotion ? undefined : "text-[#85857C]"}
                  >
                    {mounted && !reduceMotion ? stableQuestion : PLACEHOLDER}
                  </span>
                )}
              </div>
            )}
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              className="w-full bg-transparent text-[17px] font-medium leading-normal tracking-[0.01em] text-foreground-secondary placeholder:text-transparent focus:outline-none focus-visible:outline-none sm:text-[19px] relative z-10"
              style={{ outline: "none", boxShadow: "none" }}
              placeholder={PLACEHOLDER}
              aria-label={PLACEHOLDER}
              disabled={loading}
            />
          </form>
        </div>

        {/* Bottom action row */}
        <div className="mt-auto flex items-center justify-between border-t border-border-base/50 pt-2 px-2">
          <div className="flex items-center gap-2">
            <button 
              type="button" 
              className="rounded-md px-3 py-1.5 text-xs font-medium text-foreground-muted hover:bg-white/5 hover:text-foreground transition-colors"
              onClick={() => {
                setInputValue(QUESTIONS[Math.floor(Math.random() * QUESTIONS.length)]);
                setIsFocused(true);
              }}
              disabled={loading}
            >
              Surprise me
            </button>
          </div>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            aria-label="Submit query"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/5 text-foreground transition-all duration-300 hover:bg-white/10 cursor-pointer disabled:opacity-50"
          >
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div aria-hidden="true" className="aegis-prompt-ring aegis-prompt-ring--crisp !rounded-[16px]" />

      {/* Response Panel */}
      {(response || error || loading) && (
        <div className="absolute top-[calc(100%+16px)] left-0 right-0 rounded-[16px] border border-border-base bg-[#141414] p-5 shadow-[0_10px_40px_rgba(0,0,0,0.6)] z-20 text-left text-[15px] text-foreground-secondary">
          {loading && (
            <div className="flex items-center gap-3 text-accent">
              <Shield className="h-4 w-4 animate-pulse" />
              <span className="animate-pulse font-medium">Aegis is analyzing...</span>
            </div>
          )}
          {error && <div className="text-block font-medium">{error}</div>}
          {response && <div className="leading-relaxed whitespace-pre-wrap">{response}</div>}
        </div>
      )}
    </div>
  );
}
