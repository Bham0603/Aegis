"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { ErrorState } from "@/components/ui/ErrorState";
import Link from "next/link";
import { format } from "date-fns";
import { Filter } from "lucide-react";

// ---- Backend-aligned type (app/domain/audit.py AuditEvent) ----
interface AuditEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  action_id: string | null;
  agent_id: string | null;
  tool_id: string | null;
  final_decision: string | null;
}

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [filterDecision, setFilterDecision] = useState<string>("");

  useEffect(() => {
    const fetchAudit = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.get<AuditEvent[]>(
          ENDPOINTS.auditEvents({ limit: 100, decision: filterDecision || undefined })
        );
        setEvents(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAudit();
  }, [filterDecision]);

  const columns = [
    {
      header: "Event ID",
      cell: (item: AuditEvent) => (
        <span className="font-mono text-xs text-zinc-400">
          {item.event_id.substring(0, 12)}...
        </span>
      ),
    },
    {
      header: "Timestamp",
      cell: (item: AuditEvent) =>
        format(new Date(item.timestamp), "MMM d, HH:mm:ss.SSS"),
    },
    {
      header: "Event Type",
      cell: (item: AuditEvent) => (
        <span className="text-zinc-300 text-xs font-semibold tracking-wide">
          {item.event_type}
        </span>
      ),
    },
    {
      header: "Context",
      cell: (item: AuditEvent) => (
        <div className="flex flex-col">
          {item.agent_id && (
            <span className="text-zinc-400 text-xs truncate max-w-[120px]" title={item.agent_id}>
              A: {item.agent_id}
            </span>
          )}
          {item.tool_id && (
            <span className="text-zinc-500 text-xs truncate max-w-[120px]" title={item.tool_id}>
              T: {item.tool_id}
            </span>
          )}
        </div>
      ),
    },
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
          <span className="text-zinc-600 text-xs">—</span>
        ),
    },
    {
      header: "Decision",
      cell: (item: AuditEvent) => (
        <StatusBadge status={item.final_decision || "UNKNOWN"} />
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-white">Audit Explorer</h1>
          <p className="mt-1 text-sm text-zinc-400">
            Immutable log of all security evaluations and system events.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-zinc-500" />
          <select
            className="glass-input text-sm py-1 pl-2 pr-8 border-white/10 bg-black"
            value={filterDecision}
            onChange={(e) => setFilterDecision(e.target.value)}
          >
            <option value="">All Decisions</option>
            <option value="ALLOW">ALLOW</option>
            <option value="BLOCK">BLOCK</option>
            <option value="REVIEW">REVIEW</option>
          </select>
        </div>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load audit events" />
      ) : (
        <DataTable
          data={events}
          columns={columns}
          keyExtractor={(item) => item.event_id}
          loading={loading}
        />
      )}
    </div>
  );
}
