"use client";

import React from "react";
import { useAuth } from "@/lib/auth-context";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { KeyRound, LogOut, UserCircle } from "lucide-react";

export default function AccountPage() {
  const { user, logout } = useAuth();

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Account</h1>
        <p className="mt-1 text-sm text-muted">
          Your authenticated session with the Aegis backend.
        </p>
      </div>

      <GlassCard>
        <GlassCardHeader>
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-full border border-accent-border bg-accent-dim">
              <UserCircle className="h-6 w-6 text-accent" aria-hidden="true" />
            </span>
            <div>
              <GlassCardTitle className="text-base">{user?.name ?? "Aegis Admin"}</GlassCardTitle>
              <p className="font-mono text-xs uppercase tracking-wider text-foreground-muted">
                {user?.role ?? "ADMIN"} · principal
              </p>
            </div>
          </div>
        </GlassCardHeader>
        <GlassCardContent className="space-y-4">
          <div className="flex items-start gap-3 rounded-lg border border-border-base bg-background/60 p-4">
            <KeyRound className="mt-0.5 h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
            <p className="text-xs leading-relaxed text-foreground-muted">
              You authenticated with a backend-issued API key. Keys are
              stored hashed on the server and validated per request; this
              console holds yours only for the current browser session.
            </p>
          </div>

          <button
            type="button"
            onClick={logout}
            className="btn-secondary text-block"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            Sign out of this session
          </button>
        </GlassCardContent>
      </GlassCard>

      <GlassCard>
        <GlassCardHeader>
          <GlassCardTitle>How roles work</GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent>
          <dl className="space-y-3 text-sm">
            {[
              ["ADMIN", "Full access: policies, registries, approvals, audit, attack lab"],
              ["OPERATOR", "Registries and attack lab operations"],
              ["APPROVER", "Human-in-the-loop approval queue"],
              ["AUDITOR", "Read-only audit trail access"],
              ["AGENT", "Action evaluation endpoint (for SDK/MCP clients)"],
            ].map(([role, description]) => (
              <div key={role} className="flex flex-col gap-1 border-b border-border-base/60 pb-3 last:border-0 sm:flex-row sm:items-baseline sm:justify-between">
                <dt className="font-mono text-xs font-semibold tracking-wider text-accent">{role}</dt>
                <dd className="text-xs text-foreground-muted sm:text-right">{description}</dd>
              </div>
            ))}
          </dl>
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}
