"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { demoTimeline } from "@/lib/demo-data";
import { cn } from "@/lib/utils";

/** Elegant security timeline with subtle motion. */
export function SecurityTimeline() {
  const reduceMotion = useReducedMotion();

  const tones = {
    neutral: "neutral",
    safe: "safe",
    warn: "review",
    block: "block",
  } as const;

  return (
    <ol className="relative space-y-0 border-l border-border-strong pl-6">
      {demoTimeline.map((entry, i) => {
        const tone = tones[entry.tone as keyof typeof tones] ?? "neutral";
        return (
          <motion.li
            key={entry.time + entry.label}
            initial={reduceMotion ? false : { opacity: 0, x: -8 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.4, delay: i * 0.06 }}
            className="relative pb-7 last:pb-0"
          >
            <span
              aria-hidden="true"
              className={cn(
                "absolute -left-[27px] top-1 h-2.5 w-2.5 rounded-full border-2 border-background",
                tone === "safe" && "bg-allow",
                tone === "review" && "bg-review",
                tone === "block" && "bg-block",
                tone === "neutral" && "bg-zinc-500"
              )}
            />
            <p className="font-mono text-xs text-foreground-muted">{entry.time}</p>
            <p className="mt-0.5 text-sm text-foreground">{entry.label}</p>
          </motion.li>
        );
      })}
    </ol>
  );
}
