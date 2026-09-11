"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { StatusDot } from "./StatusDot";

/**
 * Extension preview — honest to the shipped product:
 * Aegis ships today as a VS Code extension (extension/ directory),
 * not a browser extension. This visualization shows the IDE panel.
 */
export function ExtensionPreview() {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5 }}
      className="panel-elevated overflow-hidden rounded-xl shadow-2xl shadow-black/50"
    >
      {/* IDE window chrome */}
      <div className="flex items-center justify-between border-b border-border-base bg-card px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-semibold tracking-widest text-foreground">
            VS CODE
          </span>
          <span className="font-mono text-[10px] text-foreground-muted">
            aegis-security-console
          </span>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-allow/30 bg-allow/10 px-2 py-0.5 text-[10px] font-semibold text-allow">
          <StatusDot tone="safe" pulse />
          CONNECTED
        </span>
      </div>

      <div className="flex">
        {/* Activity bar */}
        <div className="flex w-10 flex-col items-center gap-4 border-r border-border-base bg-background py-4" aria-hidden="true">
          <span className="h-6 w-6 rounded bg-accent/20" />
          <span className="h-6 w-6 rounded bg-border-base/60" />
          <span className="h-6 w-6 rounded bg-border-base/60" />
        </div>

        {/* Panel content */}
        <div className="flex-1 p-5">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
            Aegis Developer Security Console
          </p>

          <div className="mt-4 space-y-2.5">
            <div className="flex items-center justify-between rounded-md border border-border-base bg-background/60 px-3.5 py-2.5">
              <span className="text-xs text-foreground">Environment status</span>
              <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold text-allow">
                <StatusDot tone="safe" />
                PROTECTED
              </span>
            </div>
            <div className="flex items-center justify-between rounded-md border border-border-base bg-background/60 px-3.5 py-2.5">
              <span className="text-xs text-foreground">Pending approvals</span>
              <span className="font-mono text-xs text-foreground">1</span>
            </div>
            <div className="flex items-center justify-between rounded-md border border-block/40 bg-block/10 px-3.5 py-2.5">
              <span className="text-xs text-foreground">Last blocked action</span>
              <span className="font-mono text-[10px] font-semibold text-block">
                19:42:26 · db.delete
              </span>
            </div>
          </div>

          <p className="mt-4 font-mono text-[10px] text-foreground-muted">
            Commands: Aegis: Set API Key · Approve · Deny · Run Attack Lab
          </p>
        </div>
      </div>
    </motion.div>
  );
}
