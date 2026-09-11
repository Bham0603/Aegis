"use client";

import React, { useEffect, useState, use } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import type { Policy } from "@/lib/types";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { ErrorState } from "@/components/ui/ErrorState";
import { format } from "date-fns";
import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

/**
 * Policy detail — rules, conditions and effects, exactly as the
 * deterministic policy engine evaluates them.
 */
export default function PolicyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchPolicy = async () => {
      try {
        const data = await api.get<Policy>(ENDPOINTS.policy(id));
        setPolicy(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchPolicy();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center p-12">
        <div className="h-32 w-full max-w-2xl animate-pulse rounded-xl bg-card-elevated" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl space-y-4">
        <Link
          href="/dashboard/policies"
          className="inline-flex items-center gap-1.5 text-xs text-foreground-muted transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
          Back to policies
        </Link>
        <ErrorState error={error} title="Failed to load policy" />
      </div>
    );
  }

  if (!policy) return null;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <Link
          href="/dashboard/policies"
          className="mb-3 inline-flex items-center gap-1.5 text-xs text-foreground-muted transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
          Back to policies
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-foreground">{policy.name}</h1>
          <span
            className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[10px] font-bold tracking-wider ${
              policy.status === "ACTIVE"
                ? "border-allow/30 bg-allow/10 text-allow"
                : "border-border-strong bg-card text-foreground-muted"
            }`}
          >
            <ShieldCheck className="h-3 w-3" aria-hidden="true" />
            {policy.status}
          </span>
        </div>
        <p className="mt-1 font-mono text-xs text-foreground-muted">
          {policy.id} · v{policy.version} · priority {policy.priority}
        </p>
      </div>

      {policy.description && (
        <p className="max-w-2xl text-sm leading-relaxed text-muted">
          {policy.description}
        </p>
      )}

      <GlassCard>
        <GlassCardHeader>
          <GlassCardTitle>Rules ({policy.rules.length})</GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent className="space-y-5">
          {policy.rules.length === 0 ? (
            <p className="text-sm text-muted">
              This policy has no rules — it has no effect on evaluation.
            </p>
          ) : (
            policy.rules.map((rule, i) => (
              <div key={i} className="rounded-lg border border-border-base bg-background/60 p-4">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[11px] uppercase tracking-wider text-foreground-muted">
                    Rule {String(i + 1).padStart(2, "0")}
                  </span>
                  <span
                    className={`rounded-full border px-3 py-0.5 font-mono text-[11px] font-bold tracking-widest ${
                      rule.effect === "ALLOW"
                        ? "border-allow/40 bg-allow/10 text-allow"
                        : rule.effect === "REVIEW"
                          ? "border-review/40 bg-review/10 text-review"
                          : "border-block/40 bg-block/10 text-block"
                    }`}
                  >
                    {rule.effect}
                  </span>
                </div>
                <pre className="mt-3 overflow-x-auto font-mono text-xs leading-relaxed text-foreground-muted">
                  {JSON.stringify(rule.condition, null, 2)}
                </pre>
                <p className="mt-2 text-[11px] leading-relaxed text-foreground-muted">
                  Conditions map field paths to operator maps (e.g.{" "}
                  <code className="font-mono">&quot;parameters.path&quot;: {"{"}&quot;eq&quot;: &quot;/etc/passwd&quot;{"}"}</code>
                  ). When every operator matches, this rule&apos;s effect applies.
                </p>
              </div>
            ))
          )}
        </GlassCardContent>
      </GlassCard>

      <div className="flex items-center justify-between text-xs text-foreground-muted">
        <span>
          Created {format(new Date(policy.created_at), "MMM d, yyyy")} · Updated{" "}
          {format(new Date(policy.updated_at), "MMM d, yyyy")}
        </span>
        <span>Evaluated with strict precedence — highest priority wins</span>
      </div>
    </div>
  );
}
