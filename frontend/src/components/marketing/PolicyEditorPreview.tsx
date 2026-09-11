"use client";

import React, { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { demoPolicies } from "@/lib/demo-data";
import { cn } from "@/lib/utils";
import { StatusDot } from "./StatusDot";

type Effect = "ALLOW" | "REVIEW" | "BLOCK";

/**
 * Interactive policy editor preview. Visitors can toggle effects; the
 * production policy engine exposes the same ALLOW / REVIEW / BLOCK
 * effects (see app/models/policy.py PolicyEffect).
 */
export function PolicyEditorPreview() {
  const [policies, setPolicies] = useState(demoPolicies);
  const reduceMotion = useReducedMotion();

  const cycleEffect = (index: number) => {
    setPolicies((current) =>
      current.map((policy, i) => {
        if (i !== index) return policy;
        const next: Effect =
          policy.effect === "ALLOW"
            ? "REVIEW"
            : policy.effect === "REVIEW"
              ? "BLOCK"
              : "ALLOW";
        return { ...policy, effect: next };
      })
    );
  };

  return (
    <div className="panel-elevated overflow-hidden rounded-xl">
      <div className="flex items-center justify-between border-b border-border-base px-5 py-3.5">
        <div>
          <p className="text-sm font-semibold text-foreground">Production Agent</p>
          <p className="font-mono text-[10px] text-foreground-muted">
            agent: research-agent-01
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-allow/30 bg-allow/10 px-2.5 py-0.5 text-[10px] font-semibold text-allow">
          <StatusDot tone="safe" pulse />
          POLICY ACTIVE
        </span>
      </div>

      <ul className="divide-y divide-border-base/60" role="list">
        {policies.map((policy, i) => (
          <motion.li
            key={policy.capability}
            initial={reduceMotion ? false : { opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay: i * 0.04 }}
            className="flex items-center justify-between gap-4 px-5 py-3"
          >
            <span className="text-sm text-foreground">{policy.capability}</span>
            <button
              type="button"
              onClick={() => cycleEffect(i)}
              aria-label={`${policy.capability}: currently ${policy.effect}. Activate to change.`}
              className={cn(
                "min-w-[86px] rounded-full border px-3 py-1 font-mono text-[11px] font-bold tracking-widest transition-all duration-200",
                policy.effect === "ALLOW" &&
                  "border-allow/40 bg-allow/10 text-allow",
                policy.effect === "REVIEW" &&
                  "border-review/40 bg-review/10 text-review",
                policy.effect === "BLOCK" &&
                  "border-block/40 bg-block/10 text-block"
              )}
            >
              {policy.effect}
            </button>
          </motion.li>
        ))}
      </ul>

      <p className="border-t border-border-base bg-background/60 px-5 py-3 text-[11px] text-foreground-muted">
        Click an effect to cycle ALLOW → REVIEW → BLOCK. Changes are
        illustrative — real policies are enforced server-side by the
        deterministic Aegis Policy Engine.
      </p>
    </div>
  );
}
