"use client";

import React from "react";
import { StatusDot } from "@/components/marketing/StatusDot";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/lib/types";

const LEVEL_TEXT: Record<string, string> = {
  LOW: "text-low",
  MEDIUM: "text-medium",
  HIGH: "text-high",
  CRITICAL: "text-critical",
  NONE: "text-foreground-muted",
};

const LEVEL_BG: Record<string, string> = {
  LOW: "border-low/30 bg-low/10",
  MEDIUM: "border-medium/30 bg-medium/10",
  HIGH: "border-high/30 bg-high/10",
  CRITICAL: "border-critical/30 bg-critical/10",
  NONE: "border-border-strong bg-card",
};

/** Risk level chip with color + text + ARIA (never color alone). */
export function RiskBadge({
  level,
  score,
  className,
}: {
  level: string | null | undefined;
  score?: number | null;
  className?: string;
}) {
  const normalized = (level ?? "NONE").toUpperCase();
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-semibold",
        LEVEL_BG[normalized] ?? LEVEL_BG.NONE,
        LEVEL_TEXT[normalized] ?? LEVEL_TEXT.NONE,
        className
      )}
      aria-label={`Risk level ${normalized}${score !== undefined && score !== null ? `, score ${score}` : ""}`}
    >
      <StatusDot
        tone={
          normalized === "CRITICAL" || normalized === "HIGH"
            ? "block"
            : normalized === "MEDIUM"
              ? "review"
              : normalized === "LOW"
                ? "safe"
                : "neutral"
        }
      />
      {normalized}
      {score !== undefined && score !== null && (
        <span className="opacity-70">· {score}</span>
      )}
    </span>
  );
}

/** Risk score meter for detail views. */
export function RiskMeter({ score, className }: { score: number; className?: string }) {
  const level: RiskLevel =
    score >= 80 ? "CRITICAL" : score >= 60 ? "HIGH" : score >= 30 ? "MEDIUM" : "LOW";
  const barColor =
    level === "CRITICAL" || level === "HIGH"
      ? "bg-block"
      : level === "MEDIUM"
        ? "bg-review"
        : "bg-allow";

  return (
    <div className={className} aria-label={`Risk score ${score} of 100, level ${level}`}>
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-2xl font-bold text-foreground">{score}</span>
        <span className="font-mono text-xs text-foreground-muted">/ 100</span>
      </div>
      <div
        role="meter"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuetext={`${score}, ${level} risk`}
        className="mt-2 h-1.5 overflow-hidden rounded-full bg-border-base/60"
      >
        <div className={cn("h-full rounded-full", barColor)} style={{ width: `${score}%` }} />
      </div>
      <p className="mt-2 font-mono text-[11px] uppercase tracking-widest text-foreground-muted">
        {level}
      </p>
    </div>
  );
}
