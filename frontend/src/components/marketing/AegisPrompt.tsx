"use client";

import React, { useState, useRef, useEffect, useSyncExternalStore } from "react";
import { useSafeReducedMotion } from "@/lib/use-safe-reduced-motion";
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

    // Start after the page-load reveal: the prompt wrapper finishes
    // fading in at ~950ms, so typing begins after a deliberate pause.
    schedule(() => typeQuestion(questionIndex, 0), 1400);

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
    <div
      className="aegis-prompt group relative mx-auto w-full max-w-[540px]"
      tabIndex={0}
      role="group"
      aria-label="Aegis prompt — example questions you can ask about your agents' security"
    >
      {/* Broad atmospheric glow behind the prompt (same lighting system
          as the perimeter highlight — lime, low opacity, fading outward). */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-x-6 -inset-y-8 rounded-full bg-accent/[0.06] blur-3xl sm:-inset-x-14 sm:-inset-y-12"
      />

      {/* Soft blurred copy of the perimeter highlight — a small glow
          trailing the crisp line. Painted under the surface so its
          inner bleed never shows; outward bleed reads as a halo. */}
      <div aria-hidden="true" className="aegis-prompt-halo">
        <div className="aegis-prompt-ring aegis-prompt-ring--soft" />
      </div>

      {/* Surface + content. Solid near-black, slight elevation,
          static hairline border; the crisp ring paints over its edge. */}
      <div className="aegis-prompt-surface relative flex items-center gap-3.5 rounded-[22px] border border-border-base bg-[#0F0F0F] py-4 pl-5 pr-4 sm:gap-4 sm:py-[17px] sm:pl-6 sm:pr-5">
        <span
          aria-hidden="true"
          className="hidden shrink-0 items-center gap-1.5 rounded-full border border-accent/20 bg-black/40 px-2.5 py-[5px] text-[9px] font-semibold uppercase tracking-[0.18em] text-accent/75 sm:inline-flex"
        >
          <Shield className="h-[11px] w-[11px] text-accent/70" />
          Aegis
        </span>

        <p className="min-w-0 flex-1 truncate text-left text-[17px] font-medium leading-normal tracking-[0.01em] text-foreground-secondary sm:text-[19px]">
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
        </p>

        <span
          aria-hidden="true"
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-accent/70 transition-all duration-300 group-hover:translate-x-[3px] group-hover:text-accent"
        >
          <ArrowRight className="h-[18px] w-[18px]" />
        </span>
      </div>

      {/* Crisp perimeter highlight — conic gradient masked to a thin
          1.5px ring, so the center stays dark and text is never
          overpainted. Never receives pointer events. */}
      <div aria-hidden="true" className="aegis-prompt-ring aegis-prompt-ring--crisp" />
    </div>
  );
}
