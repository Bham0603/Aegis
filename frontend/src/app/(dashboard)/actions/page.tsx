"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import Link from "next/link";
import { format } from "date-fns";

interface AuditEvent {
  id: string;
  action_id: string;
  agent_id: string;
  tool_id: string;
  operation: string;
  event_type: string;
  decision: string;
  timestamp: string;
}

export default function ActionsPage() {
  const [actions, setActions] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActions = async () => {
      try {
        // Fetch ACTION_RECEIVED or EVALUATION_COMPLETED to list unique actions.
        // We'll fetch EVALUATION_COMPLETED because it contains the final decision.
        const events = await api.get<AuditEvent[]>("/api/v1/audit/events?event_type=EVALUATION_COMPLETED&limit=100");
        setActions(events);
      } catch (error) {
        console.error("Failed to load actions", error);
      } finally {
        setLoading(false);
      }
    };

    fetchActions();
  }, []);

  const columns = [
    {
      header: "Action ID",
      cell: (item: AuditEvent) => (
        <Link 
          href={`/actions/${item.action_id}`}
          className="text-blue-400 hover:text-blue-300 font-mono text-xs"
        >
          {item.action_id.substring(0, 8)}...
        </Link>
      ),
    },
    {
      header: "Timestamp",
      cell: (item: AuditEvent) => format(new Date(item.timestamp), "MMM d, HH:mm:ss"),
    },
    {
      header: "Agent / Tool",
      cell: (item: AuditEvent) => (
        <div className="flex flex-col">
          <span className="text-zinc-300">{item.agent_id}</span>
          <span className="text-xs text-zinc-500">{item.tool_id}</span>
        </div>
      ),
    },
    {
      header: "Operation",
      accessorKey: "operation" as keyof AuditEvent,
    },
    {
      header: "Decision",
      cell: (item: AuditEvent) => <StatusBadge status={item.decision || "UNKNOWN"} />,
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Action Explorer</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Trace security evaluations and decisions for every agent action.
        </p>
      </div>

      <DataTable 
        data={actions} 
        columns={columns} 
        keyExtractor={(item) => item.id} 
        loading={loading} 
      />
    </div>
  );
}
