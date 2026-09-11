"use client";

import React from "react";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";

/**
 * Settings page — surfaces the environment configuration the frontend
 * actually uses. Read-only where values are server-side; no secrets
 * are ever displayed.
 */
export default function SettingsPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="mt-1 text-sm text-muted">
          Console configuration and environment connections.
        </p>
      </div>

      <GlassCard>
        <GlassCardHeader>
          <GlassCardTitle>Environment</GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent>
          <dl className="space-y-4 text-sm">
            <div className="flex items-baseline justify-between gap-4 border-b border-border-base/60 pb-3">
              <dt className="text-foreground-muted">Aegis backend URL</dt>
              <dd className="font-mono text-foreground">{apiUrl}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-4 border-b border-border-base/60 pb-3">
              <dt className="text-foreground-muted">API base path</dt>
              <dd className="font-mono text-foreground">/api/v1</dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-foreground-muted">Session storage</dt>
              <dd className="text-foreground">API key (browser session only — never persisted to disk)</dd>
            </div>
          </dl>
          <p className="mt-4 text-xs leading-relaxed text-foreground-muted">
            Configure the backend location via{" "}
            <code className="rounded bg-card px-1.5 py-0.5 font-mono text-[11px] text-foreground">
              NEXT_PUBLIC_API_URL
            </code>{" "}
            in <code className="font-mono text-[11px] text-foreground">frontend/.env</code>.
            Server-side settings (policies, engines, providers) are managed by
            the backend — see <code className="font-mono text-[11px] text-foreground">docs/</code>.
          </p>
        </GlassCardContent>
      </GlassCard>

      <GlassCard>
        <GlassCardHeader>
          <GlassCardTitle>Security</GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent className="space-y-3 text-sm leading-relaxed text-muted">
          <p>
            This console runs entirely client-side against your backend. The
            dashboard never receives secrets beyond your own API key, which is
            held in the browser session store and sent as a Bearer header.
          </p>
          <p>
            Authorization is enforced by the backend on every request —
            role-gated by principal type (Admin, Operator, Approver,
            Auditor, Agent). The UI hiding a route is convenience, not the
            security boundary.
          </p>
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}
