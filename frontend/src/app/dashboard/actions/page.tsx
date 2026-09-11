"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { ErrorState } from "@/components/ui/ErrorState";
import Link from "next/link";
import { format } from "date-fns";

// ---- Backend-aligned type (app/domain/audit.py AuditEvent) ----
interface AuditEvent {
  event_id: string;
  action_id: string | null;
  agent_id: string | null;
  tool_id: string | null;
  operation: string | null;
  event_type: string;
  final_decision: string | null;
  timestamp: string;
}

export default function ActionsPage() {
  const [actions, setActions] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchActions = async () => {
      try {
        // EVALUATION_COMPLETED events contain the final security decision per action
        const events = await api.get<AuditEvent[]>(
          ENDPOINTS.auditEvents({ event_type: "EVALUATION_COMPLETED", limit: 100 })
        );
        setActions(events);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchActions();
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
          <span className="text-zinc-600 text-xs font-mono">—</span>
        ),
    },
    {
      header: "Timestamp",
      cell: (item: AuditEvent) =>
        format(new Date(item.timestamp), "MMM d, HH:mm:ss"),
    },
    {
      header: "Agent / Tool",
      cell: (item: AuditEvent) => (
        <div className="flex flex-col">
          <span className="text-zinc-300">{item.agent_id || "—"}</span>
          <span className="text-xs text-zinc-500">{item.tool_id || "—"}</span>
        </div>
      ),
    },
    {
      header: "Operation",
      cell: (item: AuditEvent) => (
        <span className="text-zinc-300 text-sm">{item.operation || "—"}</span>
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
      <div>
        <h1 className="text-2xl font-bold text-white">Action Explorer</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Trace security evaluations and decisions for every agent action.
        </p>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load actions" />
      ) : (
        <DataTable
          data={actions}
          columns={columns}
          keyExtractor={(item) => item.event_id}
          loading={loading}
        />
      )}
    </div>
  );
}
