"use client";

import React, { useEffect, useState, use } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import type { Agent, AuditEvent } from "@/lib/types";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { RiskMeter } from "@/components/dashboard/RiskBadge";
import { ErrorState } from "@/components/ui/ErrorState";
import { format } from "date-fns";
import Link from "next/link";
import { ArrowLeft, ShieldAlert } from "lucide-react";

/**
 * Agent detail — recent activity, threat history, current risk.
 * Real registry + audit data only.
 */
export default function AgentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [agent, setAgent] = useState<Agent | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchAgent = async () => {
      try {
        const [agentData, agentEvents] = await Promise.all([
          api.get<Agent>(ENDPOINTS.agent(id)),
          api.get<AuditEvent[]>(ENDPOINTS.auditEvents({ agent_id: id, limit: 50 })),
        ]);
        setAgent(agentData);
        setEvents(agentEvents);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchAgent();
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
          href="/dashboard/agents"
          className="inline-flex items-center gap-1.5 text-xs text-foreground-muted transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
          Back to agents
        </Link>
        <ErrorState error={error} title="Failed to load agent" />
      </div>
    );
  }

  if (!agent) return null;

  // Derive real risk from this agent's events
  const riskEvents = events.filter((e) => e.risk_score !== null);
  const maxRisk = riskEvents.reduce((m, e) => Math.max(m, e.risk_score ?? 0), 0);
  const blocked = events.filter((e) => e.final_decision === "BLOCK");
  const reviews = events.filter((e) => e.final_decision === "REVIEW");

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href="/dashboard/agents"
            className="mb-3 inline-flex items-center gap-1.5 text-xs text-foreground-muted transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
            Back to agents
          </Link>
          <h1 className="text-2xl font-bold text-foreground">{agent.name}</h1>
          <p className="mt-1 font-mono text-xs text-foreground-muted">{agent.id}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <StatusBadge status={agent.status} />
          {agent.trust_classification && (
            <span className="font-mono text-[10px] uppercase tracking-wider text-foreground-muted">
              trust: {agent.trust_classification}
            </span>
          )}
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Events (50 window)" value={String(events.length)} />
        <Stat label="Blocked" value={String(blocked.length)} tone="text-block" />
        <Stat label="In review" value={String(reviews.length)} tone="text-review" />
        <Stat label="Peak risk" value={maxRisk > 0 ? `${maxRisk}` : "—"} tone={maxRisk >= 60 ? "text-block" : maxRisk >= 30 ? "text-review" : "text-allow"} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
        {/* Recent activity */}
        <GlassCard className="overflow-hidden">
          <GlassCardHeader>
            <GlassCardTitle>Recent activity</GlassCardTitle>
          </GlassCardHeader>
          <div className="max-h-[420px] overflow-y-auto">
            {events.length === 0 ? (
              <p className="py-10 text-center text-sm text-muted">
                No recorded activity for this agent yet.
              </p>
            ) : (
              <ul className="divide-y divide-border-base/60">
                {events.map((event) => (
                  <li key={event.event_id} className="flex items-center justify-between gap-3 px-6 py-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm text-foreground">
                        {event.event_type.replace(/_/g, " ")}
                      </p>
                      <p className="font-mono text-[11px] text-foreground-muted">
                        {format(new Date(event.timestamp), "MMM d, HH:mm:ss")}
                        {event.operation && ` · ${event.operation}`}
                      </p>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      {event.risk_score !== null && (
                        <span className="font-mono text-xs text-foreground-muted">
                          {String(event.risk_score).padStart(2, "0")}
                        </span>
                      )}
                      <StatusBadge status={event.final_decision || "UNKNOWN"} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </GlassCard>

        {/* Current risk + threat history */}
        <div className="space-y-6">
          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle>Current risk</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              {maxRisk > 0 ? (
                <RiskMeter score={maxRisk} />
              ) : (
                <p className="text-sm text-muted">No risk-scored activity.</p>
              )}
            </GlassCardContent>
          </GlassCard>

          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle>Threat history</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent className="space-y-3">
              {blocked.length === 0 ? (
                <p className="text-xs leading-relaxed text-muted">
                  No blocked actions recorded for this agent.
                </p>
              ) : (
                <ul className="space-y-2.5">
                  {blocked.slice(0, 5).map((event) => (
                    <li key={event.event_id} className="flex items-start gap-2">
                      <ShieldAlert className="mt-0.5 h-3.5 w-3.5 shrink-0 text-block" aria-hidden="true" />
                      <div className="min-w-0">
                        <p className="truncate text-xs text-foreground">
                          {event.operation ?? "action"} blocked
                        </p>
                        <p className="font-mono text-[10px] text-foreground-muted">
                          {format(new Date(event.timestamp), "MMM d, HH:mm")}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
              <p className="pt-2 text-[11px] leading-relaxed text-foreground-muted">
                Policy assignments for this agent are managed in{" "}
                <Link href="/dashboard/policies" className="text-accent hover:underline">
                  Policies
                </Link>
                .
              </p>
            </GlassCardContent>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <div className="panel rounded-xl p-4">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-foreground-muted">
        {label}
      </p>
      <p className={`mt-1.5 font-mono text-xl font-bold ${tone ?? "text-foreground"}`}>
        {value}
      </p>
    </div>
  );
}
