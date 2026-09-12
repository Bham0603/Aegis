"use client";

import { useSafeReducedMotion } from "@/lib/use-safe-reduced-motion";

import React, { useEffect, useState, useSyncExternalStore } from "react";
import { motion } from "framer-motion";
import { Sparkles, ArrowUpRight } from "lucide-react";
import { copilotPreviewConversation } from "@/lib/demo-data";
import { cn } from "@/lib/utils";

const emptySubscribe = () => () => {};
const getSnapshot = () => true;
const getServerSnapshot = () => false;

const EXAMPLE_QUESTIONS = [
  "Why was this action blocked?",
  "Show me the highest-risk event today.",
  "Which agent has the highest risk?",
  "Are any credentials exposed?",
  "Explain this prompt injection.",
];

/**
 * Marketing preview of the Aegis Copilot â€” an AI security analyst over
 * your real audit data. This preview is illustrative only.
 */
export function CopilotPreview() {
  const [questionIndex, setQuestionIndex] = useState(0);
  const [typed, setTyped] = useState("");
  const reduceMotion = useSafeReducedMotion();
  // Hydration-safe mounted flag: the server/first client render always
  // shows the full question; the typewriter only starts after mount.
  const mounted = useSyncExternalStore(emptySubscribe, getSnapshot, getServerSnapshot);
  const question = EXAMPLE_QUESTIONS[questionIndex];

  // Rotate suggested questions with a typing cadence.
  useEffect(() => {
    if (!mounted || reduceMotion) return;
    let cancelled = false;
    const typer = setInterval(() => {
      if (cancelled) return;
      setTyped((current) => {
        if (current === question) return current;
        return question.slice(0, current.length + 1);
      });
    }, 45);
    return () => {
      cancelled = true;
      clearInterval(typer);
    };
  }, [mounted, question, reduceMotion]);

  const typedText =
    mounted && !reduceMotion ? typed || question.slice(0, 1) : question;

  useEffect(() => {
    if (!mounted || reduceMotion) return;
    const rotate = setInterval(
      () => setQuestionIndex((i) => (i + 1) % EXAMPLE_QUESTIONS.length),
      6000
    );
    return () => clearInterval(rotate);
  }, [mounted, reduceMotion]);

  const answer = copilotPreviewConversation[1];

  return (
    <div className="panel-elevated overflow-hidden rounded-xl shadow-2xl shadow-black/50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border-base px-5 py-3.5">
        <span className="inline-flex items-center gap-2 text-[11px] font-semibold tracking-[0.18em] text-foreground-muted">
          <Sparkles className="h-4 w-4 text-accent" aria-hidden="true" />
          AEGIS COPILOT
        </span>
        <span className="font-mono text-[10px] text-foreground-muted/60">
          answers from your security data
        </span>
      </div>

      {/* Conversation */}
      <div className="space-y-4 px-5 py-5">
        <div className="ml-auto max-w-[85%] rounded-xl rounded-tr-sm border border-border-base bg-card px-4 py-2.5">
          <p className="text-sm text-foreground">{typedText}</p>
        </div>

        <motion.div
          initial={reduceMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: reduceMotion ? 0 : 0.6 }}
          className="max-w-[92%] rounded-xl rounded-tl-sm border border-accent-border/40 bg-accent-dim/40 px-4 py-3"
        >
          <p className="text-sm leading-relaxed text-foreground">
            {answer.content}
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-border-strong bg-card px-2.5 py-0.5 font-mono text-[10px] text-foreground-muted">
              Risk: <span className="font-semibold text-block">{answer.structured?.risk} / 100</span>
            </span>
            <span className="rounded-full border border-border-strong bg-card px-2.5 py-0.5 font-mono text-[10px] text-foreground-muted">
              Policy: <span className="font-semibold text-foreground">{answer.structured?.policy}</span>
            </span>
          </div>
        </motion.div>
      </div>

      {/* Input */}
      <div className="border-t border-border-base px-5 py-4">
        <div className="flex items-center gap-3 rounded-lg border border-border-base bg-background px-3.5 py-2.5">
          <span
            aria-hidden="true"
            className={cn("h-1.5 w-1.5 rounded-full bg-accent", !reduceMotion && "pulse-dot")}
          />
          <p className="flex-1 truncate text-sm text-foreground-muted">
            Ask about threats, agents, policiesâ€¦
          </p>
          <ArrowUpRight className="h-4 w-4 text-foreground-muted/60" aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}