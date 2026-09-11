"use client";

import React, { useEffect, useState, use } from "react";
import { api } from "@/lib/api";
import type { AuditEvent } from "@/lib/types";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { RiskMeter } from "@/components/dashboard/RiskBadge";
import { ErrorState } from "@/components/ui/ErrorState";
import { format } from "date-fns";
import Link from "next/link";
import { FileText, User, ShieldAlert, ArrowLeft } from "lucide-react";

/**
 * Threat investigation view — the full security workflow:
 * what happened, why Aegis blocked it, which policy was involved,
 * and recommended next steps. All data is real audit data.
 */
export default function ThreatDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [event, setEvent] = useState<AuditEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const data = await api.get<AuditEvent>(`/api/v1/audit/events/${id}`);
        setEvent(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchEvent();
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
        <BackLink />
        <ErrorState error={error} title="Failed to load threat event" />
      </div>
    );
  }

  if (!event) return null;

  const severity = (event.ai_severity ?? event.threat_severity ?? "UNKNOWN").toUpperCase();
  const threatType = (event.ai_threat_type ?? "UNCLASSIFIED").replace(/_/g, " ");

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href="/dashboard/threats"
            className="mb-3 inline-flex items-center gap-1.5 text-xs text-foreground-muted transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
            Back to threats
          </Link>
          <h1 className="font-mono text-2xl font-bold text-foreground">{threatType}</h1>
          <p className="mt-1 font-mono text-xs text-foreground-muted">
            {event.event_id}
          </p>
        </div>
        <StatusBadge status={event.final_decision ?? "UNKNOWN"} />
      </div>

      {/* Key facts */}
      <div className="grid gap-6 lg:grid-cols-[1fr_240px]">
        <div className="space-y-6">
          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle>Incident summary</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              <dl className="grid grid-cols-1 gap-x-8 gap-y-4 text-sm sm:grid-cols-2">
                <Fact label="Timestamp" mono>
                  {format(new Date(event.timestamp), "MMM d, yyyy · HH:mm:ss.SSS")}
                </Fact>
                <Fact label="Severity" mono>
                  <span
                    className={
                      severity === "CRITICAL"
                        ? "text-critical"
                        : severity === "HIGH"
                          ? "text-high"
                          : severity === "MEDIUM"
                            ? "text-medium"
                            : "text-low"
                    }
                  >
                    {severity}
                  </span>
                </Fact>
                <Fact label="Agent" mono>
                  {event.agent_id ? (
                    <Link href={`/dashboard/agents/${event.agent_id}`} className="text-accent hover:underline">
                      {event.agent_id.substring(0, 13)}…
                    </Link>
                  ) : (
                    "—"
                  )}
                </Fact>
                <Fact label="Source (tool)" mono>
                  {event.tool_id ? `${event.tool_id.substring(0, 13)}…` : "—"}
                </Fact>
                <Fact label="Operation" mono>
                  {event.operation ?? "—"}
                </Fact>
                <Fact label="Resource" mono>
                  {event.resource ?? "—"}
                </Fact>
                <Fact label="Environment" mono>
                  {event.environment ?? "—"}
                </Fact>
                <Fact label="Correlation" mono>
                  {event.correlation_id.substring(0, 13)}…
                </Fact>
                {event.ai_provider && (
                  <Fact label="AI provider" mono>
                    {event.ai_provider}
                    {event.ai_confidence !== null && ` · ${Math.round(event.ai_confidence * 100)}% confidence`}
                  </Fact>
                )}
              </dl>
            </GlassCardContent>
          </GlassCard>

          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle>Why Aegis decided this</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              {event.decision_reasons.length > 0 ? (
                <ul className="space-y-2.5">
                  {event.decision_reasons.map((reason, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed text-foreground">
                      <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-review" aria-hidden="true" />
                      {reason}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted">
                  No decision reasons recorded on this event. See the action timeline.
                </p>
              )}
            </GlassCardContent>
          </GlassCard>

          {event.redacted_parameters && Object.keys(event.redacted_parameters).length > 0 && (
            <GlassCard>
              <GlassCardHeader>
                <GlassCardTitle>Raw event (redacted)</GlassCardTitle>
              </GlassCardHeader>
              <GlassCardContent>
                <pre className="overflow-x-auto rounded-lg bg-background/70 p-4 font-mono text-xs leading-relaxed text-foreground-muted">
                  {JSON.stringify(event.redacted_parameters, null, 2)}
                </pre>
                <p className="mt-3 text-xs text-foreground-muted">
                  Sensitive values were redacted before logging — this is exactly what the audit trail stores.
                </p>
              </GlassCardContent>
            </GlassCard>
          )}
        </div>

        {/* Side column */}
        <div className="space-y-6">
          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle>Risk</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              {event.risk_score !== null ? (
                <RiskMeter score={event.risk_score} />
              ) : (
                <p className="text-sm text-muted">No risk score on this event.</p>
              )}
            </GlassCardContent>
          </GlassCard>

          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle>Recommended action</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent className="space-y-3">
              <p className="text-xs leading-relaxed text-muted">
                {event.final_decision === "BLOCK"
                  ? "No action required — the threat was blocked before execution. Review the agent's recent activity to see whether the behavior repeats."
                  : event.final_decision === "REVIEW"
                    ? "A human decision is required. Open the approval queue to approve or deny this action with justification."
                    : "This event was allowed. If the behavior looks unexpected, tighten the agent's policies."}
              </p>
              <div className="space-y-2">
                {event.action_id && (
                  <Link
                    href={`/dashboard/actions/${event.action_id}`}
                    className="btn-secondary w-full justify-center text-xs"
                  >
                    <FileText className="h-3.5 w-3.5" aria-hidden="true" />
                    View action timeline
                  </Link>
                )}
                {event.agent_id && (
                  <Link
                    href={`/dashboard/agents/${event.agent_id}`}
                    className="btn-secondary w-full justify-center text-xs"
                  >
                    <User className="h-3.5 w-3.5" aria-hidden="true" />
                    View agent
                  </Link>
                )}
                <Link
                  href="/dashboard/policies"
                  className="btn-secondary w-full justify-center text-xs"
                >
                  <ShieldAlert className="h-3.5 w-3.5" aria-hidden="true" />
                  View policies
                </Link>
              </div>
            </GlassCardContent>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}

function Fact({
  label,
  children,
  mono,
}: {
  label: string;
  children: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wider text-foreground-muted">{label}</dt>
      <dd className={`mt-1 text-foreground ${mono ? "font-mono text-xs" : "text-sm"}`}>
        {children}
      </dd>
    </div>
  );
}

function BackLink() {
  return (
    <Link
      href="/dashboard/threats"
      className="inline-flex items-center gap-1.5 text-xs text-foreground-muted transition-colors hover:text-foreground"
    >
      <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
      Back to threats
    </Link>
  );
}
