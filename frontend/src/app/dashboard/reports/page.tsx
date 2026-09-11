"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import type { AuditEvent } from "@/lib/types";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { ErrorState } from "@/components/ui/ErrorState";
import { format } from "date-fns";

/**
 * Security reports — computed from the real audit trail.
 * No fabricated numbers: every chart derives from fetched events.
 */

export default function ReportsPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        // Evaluate + AI-security events cover decisions and threat detections.
        const [evaluated, aiDetections, approvals] = await Promise.all([
          api
            .get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "ACTION_EVALUATED", limit: 100 }))
            .catch(() => [] as AuditEvent[]),
          api
            .get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "AI_SECURITY_ANALYSIS_COMPLETED", limit: 100 }))
            .catch(() => [] as AuditEvent[]),
          api
            .get<AuditEvent[]>(ENDPOINTS.auditEvents({ event_type: "APPROVAL_REQUESTED", limit: 100 }))
            .catch(() => [] as AuditEvent[]),
        ]);
        const merged = [...evaluated, ...aiDetections, ...approvals];
        merged.sort(
          (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        setEvents(merged);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center p-12">
        <div className="h-32 w-full max-w-2xl animate-pulse rounded-xl bg-card-elevated" />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} title="Failed to load report data" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Reports</h1>
        <p className="mt-1 text-sm text-muted">
          Security analytics computed from your live audit trail — {events.length} recent events.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <DecisionsOverTime events={events} />
        <DecisionBreakdown events={events} />
        <ThreatCategories events={events} />
        <AgentRisk events={events} />
      </div>
    </div>
  );
}

/* ---- Chart helpers (pure SVG, restrained styling) ---- */

function DecisionsOverTime({ events }: { events: AuditEvent[] }) {
  const byDay = new Map<string, { allow: number; review: number; block: number }>();

  events.forEach((e) => {
    const day = format(new Date(e.timestamp), "MMM d");
    const entry = byDay.get(day) ?? { allow: 0, review: 0, block: 0 };
    if (e.final_decision === "ALLOW") entry.allow += 1;
    else if (e.final_decision === "REVIEW") entry.review += 1;
    else if (e.final_decision === "BLOCK") entry.block += 1;
    byDay.set(day, entry);
  });

  const days = Array.from(byDay.entries()).slice(0, 10).reverse();
  const max = Math.max(1, ...days.map(([, d]) => d.allow + d.review + d.block));

  return (
    <GlassCard>
      <GlassCardHeader>
        <GlassCardTitle>Decisions over time</GlassCardTitle>
      </GlassCardHeader>
      <GlassCardContent>
        {days.length === 0 ? (
          <Empty />
        ) : (
          <div className="flex h-44 items-end gap-3" role="img" aria-label="Stacked bar chart of allow, review and block decisions per day">
            {days.map(([day, counts]) => (
              <div key={day} className="flex flex-1 flex-col items-center gap-1.5">
                <div className="flex w-full flex-1 flex-col justify-end gap-0.5">
                  <div className="w-full rounded-t bg-block/80" style={{ height: `${(counts.block / max) * 100}%`, minHeight: counts.block ? 4 : 0 }} title={`BLOCK: ${counts.block}`} />
                  <div className="w-full bg-review/80" style={{ height: `${(counts.review / max) * 100}%`, minHeight: counts.review ? 4 : 0 }} title={`REVIEW: ${counts.review}`} />
                  <div className="w-full rounded-b bg-allow/60" style={{ height: `${(counts.allow / max) * 100}%`, minHeight: counts.allow ? 4 : 0 }} title={`ALLOW: ${counts.allow}`} />
                </div>
                <span className="font-mono text-[10px] text-foreground-muted">{day}</span>
              </div>
            ))}
          </div>
        )}
        <div className="mt-4 flex items-center gap-4 text-[11px] text-foreground-muted">
          <Legend color="bg-allow/60" label="ALLOW" />
          <Legend color="bg-review/80" label="REVIEW" />
          <Legend color="bg-block/80" label="BLOCK" />
        </div>
      </GlassCardContent>
    </GlassCard>
  );
}

function DecisionBreakdown({ events }: { events: AuditEvent[] }) {
  const counts = { allow: 0, review: 0, block: 0, other: 0 };
  events.forEach((e) => {
    if (e.final_decision === "ALLOW") counts.allow += 1;
    else if (e.final_decision === "REVIEW") counts.review += 1;
    else if (e.final_decision === "BLOCK") counts.block += 1;
    else counts.other += 1;
  });

  const total = events.length || 1;

  return (
    <GlassCard>
      <GlassCardHeader>
        <GlassCardTitle>Decision breakdown</GlassCardTitle>
      </GlassCardHeader>
      <GlassCardContent className="space-y-4">
        <Bar label="ALLOW" count={counts.allow} total={total} color="bg-allow/70" />
        <Bar label="REVIEW" count={counts.review} total={total} color="bg-review/80" />
        <Bar label="BLOCK" count={counts.block} total={total} color="bg-block/80" />
        {counts.other > 0 && (
          <Bar label="OTHER" count={counts.other} total={total} color="bg-zinc-600/70" />
        )}
      </GlassCardContent>
    </GlassCard>
  );
}

function ThreatCategories({ events }: { events: AuditEvent[] }) {
  const byType = new Map<string, number>();
  events.forEach((e) => {
    if (e.ai_threat_type) {
      byType.set(e.ai_threat_type, (byType.get(e.ai_threat_type) ?? 0) + 1);
    }
  });
  const entries = Array.from(byType.entries()).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((sum, [, n]) => sum + n, 0);

  return (
    <GlassCard>
      <GlassCardHeader>
        <GlassCardTitle>Threat categories</GlassCardTitle>
      </GlassCardHeader>
      <GlassCardContent className="space-y-4">
        {entries.length === 0 ? (
          <Empty />
        ) : (
          entries.map(([type, count]) => (
            <Bar
              key={type}
              label={type.replace(/_/g, " ")}
              count={count}
              total={total}
              color="bg-accent/60"
            />
          ))
        )}
        <p className="text-[11px] text-foreground-muted">
          AI Security Intelligence findings ({total} total). Enable the AI
          layer in backend settings to populate.
        </p>
      </GlassCardContent>
    </GlassCard>
  );
}

function AgentRisk({ events }: { events: AuditEvent[] }) {
  const byAgent = new Map<string, { max: number; count: number }>();
  events.forEach((e) => {
    if (!e.agent_id || e.risk_score === null) return;
    const entry = byAgent.get(e.agent_id) ?? { max: 0, count: 0 };
    entry.max = Math.max(entry.max, e.risk_score);
    entry.count += 1;
    byAgent.set(e.agent_id, entry);
  });

  const entries = Array.from(byAgent.entries())
    .sort((a, b) => b[1].max - a[1].max)
    .slice(0, 6);

  return (
    <GlassCard>
      <GlassCardHeader>
        <GlassCardTitle>Agent risk — highest observed</GlassCardTitle>
      </GlassCardHeader>
      <GlassCardContent className="space-y-4">
        {entries.length === 0 ? (
          <Empty />
        ) : (
          entries.map(([agentId, { max, count }]) => (
            <div key={agentId}>
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-foreground-muted">
                  {agentId.substring(0, 13)}…
                </span>
                <span className="font-mono text-foreground-muted">
                  {count} actions · max {max}
                </span>
              </div>
              <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-border-base/60">
                <div
                  className={max >= 60 ? "h-full rounded-full bg-block/80" : max >= 30 ? "h-full rounded-full bg-review/80" : "h-full rounded-full bg-allow/70"}
                  style={{ width: `${max}%` }}
                />
              </div>
            </div>
          ))
        )}
      </GlassCardContent>
    </GlassCard>
  );
}

function Bar({
  label,
  count,
  total,
  color,
}: {
  label: string;
  count: number;
  total: number;
  color: string;
}) {
  const pct = Math.round((count / total) * 100);
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-foreground">{label}</span>
        <span className="font-mono text-foreground-muted">
          {count} · {pct}%
        </span>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-border-base/60">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`h-2 w-2 rounded-full ${color}`} aria-hidden="true" />
      {label}
    </span>
  );
}

function Empty() {
  return (
    <p className="py-8 text-center text-sm text-muted">
      No data yet — run agents through Aegis to populate reports.
    </p>
  );
}
