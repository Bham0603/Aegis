"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusDot } from "@/components/marketing/StatusDot";
import { Puzzle, ArrowRight } from "lucide-react";
import Link from "next/link";

/**
 * Extension status page.
 *
 * Honest scope: Aegis ships a VS Code extension (not a browser
 * extension). The backend has no extension-registration/heartbeat API
 * yet, so this page shows the backend connection state and install
 * instructions rather than fabricating a connected-extension feed.
 */

type ApiStatus = "checking" | "online" | "offline";

export default function ExtensionDashboardPage() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [version, setVersion] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const v = await api.get<{ name: string; version: string; env: string }>(ENDPOINTS.version());
        if (!cancelled) {
          setApiStatus("online");
          setVersion(`${v.name} v${v.version} (${v.env})`);
        }
      } catch {
        if (!cancelled) setApiStatus("offline");
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Extension</h1>
        <p className="mt-1 text-sm text-muted">
          Connect the Aegis VS Code extension to your backend.
        </p>
      </div>

      <GlassCard>
        <GlassCardHeader>
          <div className="flex items-center justify-between">
            <GlassCardTitle>AEGIS EXTENSION</GlassCardTitle>
            <span
              className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
              role="status"
            >
              <StatusDot
                tone={apiStatus === "online" ? "safe" : "block"}
                pulse={apiStatus === "online"}
              />
              <span className={apiStatus === "online" ? "text-allow" : "text-block"}>
                {apiStatus === "online"
                  ? "Backend Connected"
                  : apiStatus === "offline"
                    ? "Backend Offline"
                    : "Checking"}
              </span>
            </span>
          </div>
        </GlassCardHeader>
        <GlassCardContent className="space-y-5">
          <dl className="grid grid-cols-1 gap-x-8 gap-y-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-wider text-foreground-muted">Platform</dt>
              <dd className="mt-1 text-foreground">VS Code (1.89+)</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-foreground-muted">Extension version</dt>
              <dd className="mt-1 font-mono text-foreground">1.0.0</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-foreground-muted">Backend</dt>
              <dd className="mt-1 font-mono text-foreground">
                {version ?? (apiStatus === "online" ? "connected" : "unreachable")}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-foreground-muted">Connection state</dt>
              <dd className="mt-1 text-foreground">
                {apiStatus === "online"
                  ? "Reachable from this console"
                  : "Not reachable — start the backend"}
              </dd>
            </div>
          </dl>

          <p className="rounded-lg border border-border-base bg-background/60 p-3.5 text-xs leading-relaxed text-foreground-muted">
            Per-extension heartbeat telemetry (browser, version, last
            heartbeat) requires the extension-registration API, which is not
            implemented yet. This page reports real backend connectivity
            only — no simulated telemetry.
          </p>
        </GlassCardContent>
      </GlassCard>

      <GlassCard>
        <GlassCardHeader>
          <GlassCardTitle>Install the extension</GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent>
          <p className="text-sm leading-relaxed text-muted">
            The extension ships as a packaged <code className="font-mono text-foreground">.vsix</code> in
            the repository. After installing, set your API key via the
            command palette (<code className="font-mono text-foreground">Aegis: Set API Key</code>).
          </p>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-border-base bg-background/70 p-4 font-mono text-xs leading-relaxed text-foreground"><code>{`cd extension
npm install
npm run compile
code --install-extension aegis-security-console-1.0.0.vsix`}</code></pre>
          <Link href="/extension" className="btn-secondary mt-5">
            Full install guide
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </GlassCardContent>
      </GlassCard>

      <div className="flex items-start gap-3 rounded-xl border border-border-base bg-card p-5">
        <Puzzle className="mt-0.5 h-5 w-5 shrink-0 text-accent" aria-hidden="true" />
        <div>
          <p className="text-sm font-semibold text-foreground">Browser extension?</p>
          <p className="mt-1 text-xs leading-relaxed text-muted">
            Aegis does not ship a browser extension today. Browser-based
            agents are protected by routing their tool calls through the SDK,
            REST API or MCP Security Gateway. We won&apos;t claim support that
            doesn&apos;t exist.
          </p>
        </div>
      </div>
    </div>
  );
}
