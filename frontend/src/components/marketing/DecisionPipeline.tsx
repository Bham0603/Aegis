"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowDown } from "lucide-react";

const PIPELINE_STAGES = [
  { label: "ACTION", desc: "Agent intent is intercepted" },
  { label: "CONTEXT", desc: "Agent, tool and session verified" },
  { label: "THREAT ANALYSIS", desc: "Deterministic detectors run" },
  { label: "RISK SCORE", desc: "Explainable 0–100 assessment" },
  { label: "POLICY", desc: "Rules evaluated with precedence" },
  { label: "DECISION", desc: "ALLOW · REVIEW · BLOCK" },
] as const;

/** Vertical decision pipeline: the OBSERVE → DETECT → DECIDE → ENFORCE mental model. */
export function DecisionPipeline() {
  const reduceMotion = useReducedMotion();

  return (
    <ol className="relative space-y-0">
      {PIPELINE_STAGES.map((stage, i) => {
        const isFinal = i === PIPELINE_STAGES.length - 1;
        return (
          <motion.li
            key={stage.label}
            initial={reduceMotion ? false : { opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.4, delay: i * 0.05 }}
            className="relative"
          >
            <div className="flex items-center gap-4 py-2.5">
              <span
                aria-hidden="true"
                className="flex h-8 w-14 shrink-0 items-center justify-center rounded-md border border-border-base bg-card font-mono text-[10px] font-semibold text-foreground-muted"
              >
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <p className="font-mono text-sm font-semibold tracking-wider text-foreground">
                  {stage.label}
                </p>
                <p className="mt-0.5 text-xs text-foreground-muted">{stage.desc}</p>
              </div>
            </div>
            {!isFinal && (
              <ArrowDown
                aria-hidden="true"
                className="ml-[23px] h-4 w-4 text-border-strong"
              />
            )}
          </motion.li>
        );
      })}
    </ol>
  );
}
