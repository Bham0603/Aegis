"use client";

import React, { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { heroConsoleActions, securityScore } from "@/lib/demo-data";
import { StatusDot } from "./StatusDot";
import { cn } from "@/lib/utils";

/**
 * Cinematic live-feel security console for the hero.
 * Backed by isolated demo data (src/lib/demo-data.ts) — illustrative only.
 */
export function SecurityConsole() {
  const [visibleCount, setVisibleCount] = useState(2);
  const [score, setScore] = useState(87);
  const reduceMotion = useReducedMotion();

  // Progressively reveal activity rows, then restart — subtle live cadence.
  useEffect(() => {
    if (reduceMotion) return;
    const interval = setInterval(() => {
      setVisibleCount((count) =>
        count >= heroConsoleActions.length ? 2 : count + 1
      );
    }, 2200);
    return () => clearInterval(interval);
  }, [reduceMotion]);

  const visible = reduceMotion ? heroConsoleActions.length : visibleCount;
  const displayScore = reduceMotion ? securityScore : score;

  // Score gently drifts toward its target.
  useEffect(() => {
    if (reduceMotion) return;
    const interval = setInterval(() => {
      setScore((current) => {
        if (current === securityScore) return current;
        return current < securityScore ? current + 1 : current - 1;
      });
    }, 1400);
    return () => clearInterval(interval);
  }, [reduceMotion]);

  return (
    <div
      role="img"
      aria-label="Aegis security console preview: live agent activity with allowed, review and blocked decisions"
      className="panel-elevated relative overflow-hidden rounded-xl shadow-2xl shadow-black/50"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border-base px-5 py-3.5">
        <div className="flex items-center gap-2.5">
          <span className="text-[11px] font-semibold tracking-[0.18em] text-foreground-muted">
            AEGIS SECURITY
          </span>
          <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-allow/30 bg-allow/10 px-2 py-0.5 text-[10px] font-semibold tracking-wider text-allow">
            <StatusDot tone="safe" pulse />
            SYSTEM PROTECTED
          </span>
        </div>
        <div className="font-mono text-sm">
          <span className="text-accent">{displayScore}</span>
          <span className="text-foreground-muted"> / 100</span>
        </div>
      </div>

      {/* Activity feed */}
      <div className="px-5 py-4">
        <p className="text-[11px] font-semibold tracking-[0.18em] text-foreground-muted">
          LIVE AGENT ACTIVITY
        </p>
        <ul aria-hidden="true" className="mt-3 space-y-2.5">
          {heroConsoleActions.slice(0, visible).map((item, i) => (
            <motion.li
              key={item.action}
              initial={reduceMotion ? false : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: i === visible - 1 ? 0.1 : 0 }}
              className="flex items-center justify-between gap-4 rounded-lg border border-border-base/60 bg-background/60 px-3.5 py-2.5"
            >
              <div className="flex min-w-0 items-center gap-3">
                <StatusDot
                  tone={
                    item.decision === "BLOCKED"
                      ? "block"
                      : item.decision === "REVIEW"
                        ? "review"
                        : "safe"
                  }
                />
                <div className="min-w-0">
                  <p className="truncate text-sm text-foreground">{item.action}</p>
                  <p className="truncate font-mono text-[11px] text-foreground-muted">
                    {item.target}
                  </p>
                </div>
              </div>
              <span
                className={cn(
                  "shrink-0 font-mono text-[11px] font-semibold tracking-wider",
                  item.decision === "BLOCKED" && "text-block",
                  item.decision === "REVIEW" && "text-review",
                  item.decision === "ALLOWED" && "text-allow"
                )}
              >
                {item.decision}
              </span>
            </motion.li>
          ))}
        </ul>
      </div>

      {/* Threat level meter */}
      <div className="border-t border-border-base px-5 py-4">
        <p className="text-[11px] font-semibold tracking-[0.18em] text-foreground-muted">
          THREAT LEVEL
        </p>
        <div className="mt-3 flex items-center gap-2" aria-hidden="true">
          <ThreatSegment label="LOW" active lowlight />
          <ThreatSegment label="MEDIUM" active />
          <ThreatSegment label="HIGH" />
        </div>
      </div>

      {/* Subtle scan line */}
      {!reduceMotion && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-0 top-0 h-full"
        >
          <div className="scan-line h-24 w-full bg-gradient-to-b from-transparent via-accent/5 to-transparent" />
        </div>
      )}
    </div>
  );
}

function ThreatSegment({
  label,
  active,
  lowlight,
}: {
  label: string;
  active?: boolean;
  lowlight?: boolean;
}) {
  return (
    <span
      className={cn(
        "flex-1 rounded-md border py-1.5 text-center font-mono text-[10px] font-semibold tracking-widest transition-colors",
        active
          ? lowlight
            ? "border-allow/30 bg-allow/10 text-allow"
            : "border-border-strong bg-card-elevated text-foreground-muted"
          : "border-border-base/50 bg-transparent text-foreground-muted/40"
      )}
    >
      {label}
    </span>
  );
}
