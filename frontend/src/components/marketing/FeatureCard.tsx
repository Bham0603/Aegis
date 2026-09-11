"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { StatusDot } from "./StatusDot";

/**
 * Mini visualization for the Prompt Injection Defense feature card.
 * Shows untrusted content flowing toward the agent and being intercepted.
 */
export function InjectionViz() {
  return (
    <div className="space-y-2" aria-hidden="true">
      <div className="flex items-center gap-2 rounded-md border border-border-base bg-background/60 px-3 py-2">
        <StatusDot tone="neutral" />
        <span className="font-mono text-[10px] text-foreground-muted">webpage content</span>
      </div>
      <div className="flex items-center gap-2 rounded-md border border-border-base bg-background/60 px-3 py-2">
        <StatusDot tone="neutral" />
        <span className="font-mono text-[10px] text-foreground-muted">tool output</span>
      </div>
      <div className="flex items-center gap-2 rounded-md border border-block/40 bg-block/10 px-3 py-2">
        <StatusDot tone="block" />
        <span className="font-mono text-[10px] font-semibold text-block">
          &quot;ignore previous instructions&quot; → BLOCKED
        </span>
      </div>
    </div>
  );
}

/** Tool call protection: an action intercepted before execution. */
export function ToolCallViz() {
  return (
    <div aria-hidden="true" className="space-y-2">
      <div className="rounded-md border border-border-base bg-background/60 px-3 py-2">
        <p className="font-mono text-[10px] text-foreground-muted">
          tool: db.delete(table: &quot;users&quot;)
        </p>
      </div>
      <div className="flex items-center gap-2 px-1">
        <span className="font-mono text-[10px] text-foreground-muted">aegis →</span>
        <span className="rounded-full border border-block/40 bg-block/10 px-2 py-0.5 font-mono text-[10px] font-bold text-block">
          NOT EXECUTED
        </span>
      </div>
    </div>
  );
}

/** Sensitive data: redaction markers protecting secrets. */
export function SensitiveDataViz() {
  return (
    <div className="space-y-1.5 font-mono text-[10px]" aria-hidden="true">
      {["api_key", "token", "password", "private_key"].map((key) => (
        <div
          key={key}
          className="flex items-center justify-between rounded-md border border-border-base bg-background/60 px-3 py-1.5"
        >
          <span className="text-foreground-muted">{key}</span>
          <span className="rounded-full border border-allow/30 bg-allow/10 px-2 py-0.5 text-[9px] font-semibold text-allow">
            [REDACTED]
          </span>
        </div>
      ))}
    </div>
  );
}

/** Unauthorized action: behavior outside policy scope. */
export function UnauthorizedActionViz() {
  return (
    <div className="space-y-2" aria-hidden="true">
      <div className="flex items-center justify-between rounded-md border border-border-base bg-background/60 px-3 py-2">
        <span className="font-mono text-[10px] text-foreground-muted">browser.read</span>
        <span className="font-mono text-[10px] font-semibold text-allow">ALLOW</span>
      </div>
      <div className="flex items-center justify-between rounded-md border border-border-base bg-background/60 px-3 py-2">
        <span className="font-mono text-[10px] text-foreground-muted">fs.write /etc</span>
        <span className="font-mono text-[10px] font-semibold text-block">BLOCK</span>
      </div>
      <div className="flex items-center justify-between rounded-md border border-review/40 bg-review/10 px-3 py-2">
        <span className="font-mono text-[10px] text-foreground-muted">net.export data</span>
        <span className="font-mono text-[10px] font-semibold text-review">REVIEW</span>
      </div>
    </div>
  );
}

/** Feature card with custom mini visualization. */
export function FeatureCard({
  index,
  title,
  description,
  children,
}: {
  index: string;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.article
      initial={reduceMotion ? false : { opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.45 }}
      className="panel panel-interactive flex flex-col gap-4 rounded-xl p-6"
    >
      <div className="flex items-start justify-between">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <span className="font-mono text-[11px] text-foreground-muted/60">{index}</span>
      </div>
      {children}
      <p className="mt-auto text-sm leading-relaxed text-muted">{description}</p>
    </motion.article>
  );
}
