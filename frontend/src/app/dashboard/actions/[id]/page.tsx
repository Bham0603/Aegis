"use client";

import React, { useEffect, useState, use } from "react";
import { api } from "@/lib/api";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { format } from "date-fns";

interface AuditEvent {
  id: string;
  action_id: string;
  agent_id: string;
  tool_id: string;
  operation: string;
  resource: string;
  environment: string;
  event_type: string;
  decision: string;
  timestamp: string;
  details?: Record<string, unknown>;
  redacted_parameters?: Record<string, unknown>;
}

export default function ActionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchActionHistory = async () => {
      try {
        const history = await api.get<AuditEvent[]>(`/api/v1/audit/actions/${id}`);
        // Sort by timestamp ascending to build timeline
        history.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        setEvents(history);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load action history");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchActionHistory();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center p-12">
        <div className="animate-pulse bg-white/10 h-32 w-full max-w-2xl rounded-xl"></div>
      </div>
    );
  }

  if (error || events.length === 0) {
    return (
      <GlassCard className="max-w-3xl mx-auto mt-12">
        <GlassCardContent className="text-center py-12 text-zinc-400">
          {error || "No audit history found for this action."}
        </GlassCardContent>
      </GlassCard>
    );
  }

  const firstEvent = events[0];
  const lastEvent = events[events.length - 1];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Action Details</h1>
        <p className="mt-1 text-sm text-zinc-400 font-mono">
          ID: {id}
        </p>
      </div>

      <GlassCard>
        <GlassCardHeader>
          <GlassCardTitle>Context</GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-zinc-500 font-medium">Agent ID</dt>
              <dd className="text-zinc-200 mt-1">{firstEvent.agent_id}</dd>
            </div>
            <div>
              <dt className="text-zinc-500 font-medium">Tool ID</dt>
              <dd className="text-zinc-200 mt-1">{firstEvent.tool_id}</dd>
            </div>
            <div>
              <dt className="text-zinc-500 font-medium">Operation</dt>
              <dd className="text-zinc-200 mt-1">{firstEvent.operation}</dd>
            </div>
            <div>
              <dt className="text-zinc-500 font-medium">Environment</dt>
              <dd className="text-zinc-200 mt-1">{firstEvent.environment}</dd>
            </div>
            {firstEvent.resource && (
              <div className="sm:col-span-2">
                <dt className="text-zinc-500 font-medium">Resource</dt>
                <dd className="text-zinc-200 mt-1">{firstEvent.resource}</dd>
              </div>
            )}
            <div className="sm:col-span-2">
              <dt className="text-zinc-500 font-medium">Final Decision</dt>
              <dd className="mt-1">
                <StatusBadge status={lastEvent.decision || "UNKNOWN"} />
              </dd>
            </div>
          </dl>
        </GlassCardContent>
      </GlassCard>

      <div className="pt-4">
        <h3 className="text-lg font-medium text-white mb-6">Evaluation Timeline</h3>
        <div className="relative border-l border-white/10 ml-4 space-y-8">
          {events.map((event) => (
            <div key={event.id} className="relative pl-8">
              <div className="absolute -left-[5px] top-1.5 h-2 w-2 rounded-full bg-blue-500 ring-4 ring-black" />
              <div className="flex flex-col sm:flex-row sm:items-baseline sm:justify-between mb-1">
                <h4 className="text-base font-semibold text-white">
                  {event.event_type.replace(/_/g, " ")}
                </h4>
                <time className="text-xs text-zinc-500 font-mono">
                  {format(new Date(event.timestamp), "HH:mm:ss.SSS")}
                </time>
              </div>
              
              {event.decision && event.decision !== "UNKNOWN" && (
                <div className="mb-2">
                  <StatusBadge status={event.decision} />
                </div>
              )}
              
              {event.details && Object.keys(event.details).length > 0 && (
                <div className="mt-2 bg-black/40 rounded-md p-3 border border-white/5 overflow-x-auto">
                  <pre className="text-xs text-zinc-300 font-mono">
                    {JSON.stringify(event.details, null, 2)}
                  </pre>
                </div>
              )}

              {event.redacted_parameters && Object.keys(event.redacted_parameters).length > 0 && (
                <div className="mt-2 bg-black/40 rounded-md p-3 border border-white/5 overflow-x-auto">
                  <h5 className="text-xs font-medium text-zinc-500 mb-1">Redacted Parameters:</h5>
                  <pre className="text-xs text-zinc-300 font-mono">
                    {JSON.stringify(event.redacted_parameters, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
