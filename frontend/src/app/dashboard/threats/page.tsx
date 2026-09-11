"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorState } from "@/components/ui/ErrorState";
import Link from "next/link";
import { format } from "date-fns";

// ---- Backend-aligned type (app/domain/audit.py AuditEvent) ----
// AI_SECURITY_ANALYSIS_COMPLETED events contain ai_threat_type, ai_severity, ai_confidence
interface AuditEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  action_id: string | null;
  agent_id: string | null;
  ai_threat_type: string | null;
  ai_severity: string | null;
  ai_confidence: number | null;
  ai_provider: string | null;
}

export default function ThreatsPage() {
  const [threats, setThreats] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        // AI_SECURITY_ANALYSIS_COMPLETED is the authoritative event type for AI threat detections.
        // /api/v1/threats/ does NOT exist — we source from the audit log.
        const events = await api.get<AuditEvent[]>(
          ENDPOINTS.auditEvents({ event_type: "AI_SECURITY_ANALYSIS_COMPLETED", limit: 100 })
        );
        setThreats(events);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchThreats();
  }, []);

  const columns = [
    {
      header: "Action ID",
      cell: (item: AuditEvent) =>
        item.action_id ? (
          <Link
            href={`/dashboard/actions/${item.action_id}`}
            className="text-blue-400 hover:text-blue-300 font-mono text-xs"
          >
            {item.action_id.substring(0, 8)}...
          </Link>
        ) : (
          <span className="text-zinc-600 font-mono text-xs">—</span>
        ),
    },
    {
      header: "Timestamp",
      cell: (item: AuditEvent) =>
        format(new Date(item.timestamp), "MMM d, HH:mm:ss"),
    },
    {
      header: "Threat Type",
      cell: (item: AuditEvent) => (
        <div className="flex flex-col">
          <span className="text-zinc-200">{item.ai_threat_type || "UNKNOWN"}</span>
          {item.ai_provider && (
            <span className="text-[10px] text-purple-400 font-semibold uppercase tracking-wider mt-0.5">
              {item.ai_provider}
            </span>
          )}
        </div>
      ),
    },
    {
      header: "Severity",
      cell: (item: AuditEvent) => {
        const sev = (item.ai_severity || "UNKNOWN").toUpperCase();
        let colorClass = "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
        if (sev === "CRITICAL") colorClass = "bg-red-500/10 text-red-400 border-red-500/20";
        else if (sev === "HIGH") colorClass = "bg-orange-500/10 text-orange-400 border-orange-500/20";
        else if (sev === "MEDIUM") colorClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";
        else if (sev === "LOW") colorClass = "bg-blue-500/10 text-blue-400 border-blue-500/20";

        return (
          <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${colorClass}`}>
            {sev}
          </span>
        );
      },
    },
    {
      header: "Confidence",
      cell: (item: AuditEvent) =>
        item.ai_confidence !== null ? (
          <span className="text-zinc-300 text-sm">
            {(item.ai_confidence * 100).toFixed(0)}%
          </span>
        ) : (
          <span className="text-zinc-600 text-sm">—</span>
        ),
    },
    {
      header: "",
      cell: (item: AuditEvent) => (
        <Link
          href={`/dashboard/threats/${item.event_id}`}
          className="glass-button px-3 py-1.5 text-accent text-xs inline-block"
        >
          Investigate
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Center</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Monitor AI-detected semantic threats and security analysis results.
        </p>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load threats" />
      ) : (
        <DataTable
          data={threats}
          columns={columns}
          keyExtractor={(item) => item.event_id}
          loading={loading}
        />
      )}
    </div>
  );
}
