"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import {
  dashboardPreviewMetrics,
  dashboardPreviewActivity,
  threatBreakdown,
} from "@/lib/demo-data";
import { StatusDot } from "./StatusDot";
import { cn } from "@/lib/utils";

/**
 * Realistic dashboard preview built as a coherent product visualization.
 * Uses isolated demo data — not a screenshot.
 */
export function DashboardPreview() {
  const reduceMotion = useReducedMotion();

  return (
    <div className="panel-elevated overflow-hidden rounded-xl shadow-2xl shadow-black/60">
      {/* Window bar */}
      <div className="flex items-center justify-between border-b border-border-base bg-card px-5 py-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold tracking-widest text-foreground">AEGIS</span>
          <span className="text-[10px] text-foreground-muted">/ Command Center</span>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-allow/30 bg-allow/10 px-2 py-0.5 text-[10px] font-semibold text-allow">
          <StatusDot tone="safe" pulse />
          PROTECTED
        </span>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 divide-border-base sm:grid-cols-4 sm:divide-x lg:divide-x">
        {dashboardPreviewMetrics.map((metric, i) => (
          <motion.div
            key={metric.label}
            initial={reduceMotion ? false : { opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.07 }}
            className="p-4 sm:p-5"
          >
            <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
              {metric.label}
            </p>
            <p className="mt-1.5 font-mono text-xl font-bold text-foreground sm:text-2xl">
              {metric.value}
              {metric.suffix && (
                <span className="text-sm text-foreground-muted">{metric.suffix}</span>
              )}
            </p>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-px border-t border-border-base bg-border-base/40 lg:grid-cols-2">
        {/* Live activity */}
        <div className="bg-card p-5">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
            Live Activity
          </p>
          <ul className="mt-3 space-y-2" aria-hidden="true">
            {dashboardPreviewActivity.map((item) => (
              <li
                key={item.action + item.target}
                className="flex items-center justify-between gap-3 rounded-md border border-border-base/60 bg-background/50 px-3 py-2"
              >
                <div className="flex min-w-0 items-center gap-2.5">
                  <StatusDot
                    tone={
                      item.decision === "BLOCKED"
                        ? "block"
                        : item.decision === "REVIEW"
                          ? "review"
                          : "safe"
                    }
                  />
                  <span className="truncate text-xs text-foreground">{item.action}</span>
                  <span className="hidden truncate font-mono text-[10px] text-foreground-muted sm:inline">
                    {item.target}
                  </span>
                </div>
                <span
                  className={cn(
                    "shrink-0 font-mono text-[10px] font-semibold",
                    item.decision === "BLOCKED" && "text-block",
                    item.decision === "REVIEW" && "text-review",
                    item.decision === "ALLOWED" && "text-allow"
                  )}
                >
                  {item.decision}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Threat breakdown */}
        <div className="bg-card p-5">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
            Threat Breakdown
          </p>
          <ul className="mt-3 space-y-3" aria-hidden="true">
            {threatBreakdown.map((threat) => (
              <li key={threat.label}>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-foreground">{threat.label}</span>
                  <span className="font-mono text-foreground-muted">{threat.count}</span>
                </div>
                <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-border-base/60">
                  <motion.div
                    initial={reduceMotion ? false : { width: 0 }}
                    whileInView={{ width: `${threat.share}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-full rounded-full bg-accent/70"
                  />
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
