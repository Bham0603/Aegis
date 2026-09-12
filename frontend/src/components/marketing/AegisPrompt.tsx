"use client";

import React, { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { useReducedMotion } from "framer-motion";
import { ArrowRight, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Aegis Prompt — the cinematic hero prompt.
 *
 * Cycles security questions with a character-by-character typewriter
 * animation (type → hold → delete → next). Rendering is hydration-safe:
 * the animated text only starts on the client after mount, and the
 * server/first paint always shows the static placeholder.
 * With prefers-reduced-motion, a stable question is shown instead.
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
  const reduceMotion = useReducedMotion();
  // Hydration-safe mounted flag: false during SSR/first paint, true on the
  // client after hydration — without setState inside an effect.
  const mounted = useSyncExternalStore(
    emptySubscribe,
    getSnapshot,
    getServerSnapshot
  );
  const [text, setText] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    if (!mounted || reduceMotion) return;

    let cancelled = false;
    const schedule = (fn: () => void, ms: number) => {
      const t = setTimeout(() => {
        if (!cancelled) fn();
      }, ms);
      timers.current.push(t);
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

    schedule(() => typeQuestion(questionIndex, 0), 900);

    return () => {
      cancelled = true;
      timers.current.forEach(clearTimeout);
      timers.current = [];
    };
    // questionIndex intentionally excluded: the loop carries its own index.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mounted, reduceMotion]);

  const showTypewriter = mounted && !reduceMotion;
  const stableQuestion = QUESTIONS[questionIndex];

  return (
    <div className="group relative mx-auto w-full max-w-2xl">
      {/* soft atmospheric glow behind the prompt */}
      <div
        aria-hidden="true"
        className="absolute -inset-x-10 -inset-y-8 rounded-[3rem] bg-accent/10 blur-3xl opacity-60"
      />

      <div
        role="group"
        aria-label="Aegis prompt — example questions you can ask about your agents' security"
        className="relative flex items-center gap-3.5 rounded-2xl border border-border-base bg-[#070707]/95 py-4 pl-5 pr-4 shadow-[0_8px_40px_-12px_rgba(0,0,0,0.9),0_0_32px_-6px_rgba(223,255,63,0.14)] sm:gap-4 sm:py-5 sm:pl-6 sm:pr-5"
      >
        <span
          aria-hidden="true"
          className="hidden shrink-0 items-center gap-2 rounded-full border border-accent-border bg-accent-dim px-2.5 py-1 font-mono text-[10px] font-semibold tracking-[0.14em] text-accent sm:inline-flex"
        >
          <Shield className="h-3 w-3" />
          AEGIS
        </span>

        <p className="min-w-0 flex-1 truncate text-left font-mono text-sm text-foreground-secondary sm:text-base">
          {showTypewriter ? (
            <>
              <span className="sr-only">Example question: </span>
              <span aria-hidden="true">
                {text}
                <span className="prompt-caret" />
              </span>
            </>
          ) : (
            <span aria-hidden="true">
              {mounted && !reduceMotion
                ? stableQuestion
                : PLACEHOLDER}
            </span>
          )}
        </p>

        <span
          aria-hidden="true"
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border transition-colors duration-200",
            "border-border-strong bg-background text-foreground-muted",
            "group-hover:border-accent-border group-hover:bg-accent group-hover:text-black"
          )}
        >
          <ArrowRight className="h-4 w-4" />
        </span>
      </div>
    </div>
  );
}
