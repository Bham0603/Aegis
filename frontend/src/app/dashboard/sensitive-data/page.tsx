"use client";

import React, { useEffect, useMemo, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import type { AuditEvent, SensitiveDataFinding } from "@/lib/types";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { ErrorState } from "@/components/ui/ErrorState";
import { RiskBadge } from "@/components/dashboard/RiskBadge";
import Link from "next/link";
import { format } from "date-fns";
import { Lock, Search } from "lucide-react";

/**
 * Sensitive Data findings.
 *
 * Derived entirely from the real audit trail: Aegis redacts sensitive
 * parameters before logging (app/core/redaction.py). This view surfaces
 * those [REDACTED] markers as findings so operators can see where
 * secrets were involved in agent actions — without ever exposing them.
 */

const CATEGORY_BY_KEY: Record<string, SensitiveDataFinding["category"]> = {
  api_key: "API Key",
  key: "API Key",
  token: "Token",
  access_token: "Token",
  bearer: "Token",
  password: "Credential",
  secret: "Credential",
  private_key: "Confidential File",
  authorization: "Credential",
};

function categorize(key: string): SensitiveDataFinding["category"] {
  const lower = key.toLowerCase();
  for (const [needle, category] of Object.entries(CATEGORY_BY_KEY)) {
    if (lower.includes(needle)) return category;
  }
  return "Personal Information";
}

function isRedacted(value: unknown): boolean {
  return value === "[REDACTED]" || (typeof value === "string" && value.includes("[REDACTED]"));
}

function collectFindings(event: AuditEvent): SensitiveDataFinding[] {
  if (!event.redacted_parameters) return [];
  const findings: SensitiveDataFinding[] = [];
  const walk = (params: Record<string, unknown>, prefix = "") => {
    for (const [key, value] of Object.entries(params)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      if (typeof value === "object" && value !== null) {
        walk(value as Record<string, unknown>, fullKey);
      } else if (isRedacted(value)) {
        findings.push({
          id: `${event.event_id}:${fullKey}`,
          category: categorize(key),
          parameterKey: fullKey,
          redactedValue: String(value),
          actionId: event.action_id ?? event.event_id,
          agentId: event.agent_id,
          timestamp: event.timestamp,
          environment: event.environment,
          severity:
            (event.risk_level as SensitiveDataFinding["severity"]) ?? "NONE",
          status: event.final_decision ?? "UNKNOWN",
        });
      }
    }
  };
  walk(event.redacted_parameters);
  return findings;
}

export default function SensitiveDataPage() {
  const [findings, setFindings] = useState<SensitiveDataFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [query, setQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");

  useEffect(() => {
    const fetch = async () => {
      try {
        // Redaction markers appear across evaluated actions — pull recent history.
        const [evaluated, received] = await Promise.all([
          api
            .get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "ACTION_EVALUATED", limit: 100 }))
            .catch(() => [] as AuditEvent[]),
          api
            .get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "ACTION_RECEIVED", limit: 100 }))
            .catch(() => [] as AuditEvent[]),
        ]);
        const all = [...evaluated, ...received];
        const collected = all.flatMap(collectFindings);
        // Newest first, deduplicated by id
        const seen = new Set<string>();
        const unique = collected.filter((f) => {
          if (seen.has(f.id)) return false;
          seen.add(f.id);
          return true;
        });
        unique.sort(
          (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        setFindings(unique);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const categories = useMemo(
    () => ["ALL", ...Array.from(new Set(findings.map((f) => f.category)))],
    [findings]
  );

  const filtered = useMemo(
    () =>
      findings.filter(
        (f) =>
          (categoryFilter === "ALL" || f.category === categoryFilter) &&
          (query === "" ||
            f.parameterKey.toLowerCase().includes(query.toLowerCase()) ||
            f.actionId.toLowerCase().includes(query.toLowerCase()) ||
            (f.agentId ?? "").toLowerCase().includes(query.toLowerCase()))
      ),
    [findings, query, categoryFilter]
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Sensitive Data</h1>
          <p className="mt-1 text-sm text-muted">
            Where sensitive values appeared in agent actions — redacted by
            Aegis before logging, never stored in plaintext.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-foreground-muted" aria-hidden="true" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search keys, actions…"
              aria-label="Search findings"
              className="glass-input py-2 pl-9 pr-3 text-sm w-48 sm:w-56"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            aria-label="Filter by category"
            className="glass-input px-2.5 py-2 text-sm"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === "ALL" ? "All Categories" : c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load sensitive data findings" />
      ) : loading ? (
        <GlassCard className="w-full">
          <div className="flex justify-center p-12">
            <div className="h-8 w-3/4 animate-pulse rounded bg-card-elevated" />
          </div>
        </GlassCard>
      ) : filtered.length === 0 ? (
        <GlassCard className="w-full">
          <GlassCardContent className="py-12 text-center">
            <Lock className="mx-auto h-8 w-8 text-foreground-muted/50" aria-hidden="true" />
            <p className="mt-3 text-sm text-muted">
              No sensitive-data findings in recent actions. Values are
              redacted before they ever reach the audit trail.
            </p>
          </GlassCardContent>
        </GlassCard>
      ) : (
        <GlassCard className="w-full overflow-hidden">
          <GlassCardHeader>
            <GlassCardTitle>
              Findings ({filtered.length})
            </GlassCardTitle>
          </GlassCardHeader>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border-base/60">
              <thead className="bg-card-elevated/60">
                <tr>
                  {["Category", "Parameter", "Action", "Agent", "Environment", "Risk", "Decision", "Time"].map(
                    (h) => (
                      <th
                        key={h}
                        scope="col"
                        className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-foreground-muted"
                      >
                        {h}
                      </th>
                    )
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-border-base/60">
                {filtered.map((finding) => (
                  <tr key={finding.id} className="transition-colors hover:bg-card/60">
                    <td className="whitespace-nowrap px-4 py-3">
                      <span className="inline-flex items-center gap-1.5 text-sm text-foreground">
                        <Lock className="h-3.5 w-3.5 text-review" aria-hidden="true" />
                        {finding.category}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs text-foreground">
                        {finding.parameterKey}
                      </span>
                      <span className="ml-2 rounded-full border border-allow/30 bg-allow/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-allow">
                        [REDACTED]
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/dashboard/actions/${finding.actionId}`}
                        className="font-mono text-xs text-accent hover:underline"
                      >
                        {finding.actionId.substring(0, 8)}…
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs text-foreground-muted">
                        {finding.agentId ? `${finding.agentId.substring(0, 8)}…` : "—"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs uppercase text-foreground-muted">
                        {finding.environment ?? "—"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge level={finding.severity} />
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={
                          finding.status === "BLOCK"
                            ? "font-mono text-xs font-semibold text-block"
                            : finding.status === "REVIEW"
                              ? "font-mono text-xs font-semibold text-review"
                              : "font-mono text-xs font-semibold text-allow"
                        }
                      >
                        {finding.status}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <time className="font-mono text-xs text-foreground-muted">
                        {format(new Date(finding.timestamp), "MMM d, HH:mm")}
                      </time>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
