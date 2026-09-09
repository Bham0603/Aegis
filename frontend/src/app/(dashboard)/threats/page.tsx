"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import Link from "next/link";
import { format } from "date-fns";

interface AuditEvent {
  id: string;
  action_id: string;
  agent_id: string;
  event_type: string;
  timestamp: string;
  details?: {
    severity?: string;
    threat_type?: string;
    description?: string;
    is_ai_detected?: boolean;
    [key: string]: unknown;
  };
}

export default function ThreatsPage() {
  const [threats, setThreats] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        const events = await api.get<AuditEvent[]>("/api/v1/audit/events?event_type=THREAT_DETECTED&limit=100");
        setThreats(events);
      } catch (error) {
        console.error("Failed to load threats", error);
      } finally {
        setLoading(false);
      }
    };

    fetchThreats();
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
      header: "Threat Type",
      cell: (item: AuditEvent) => (
        <div className="flex flex-col">
          <span className="text-zinc-200">{item.details?.threat_type || "Unknown"}</span>
          {item.details?.is_ai_detected && (
            <span className="text-[10px] text-purple-400 font-semibold uppercase tracking-wider mt-0.5">
              AI Detected
            </span>
          )}
        </div>
      )
    },
    {
      header: "Severity",
      cell: (item: AuditEvent) => {
        const sev = (item.details?.severity || "MEDIUM").toUpperCase();
        let colorClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";
        if (sev === "CRITICAL") colorClass = "bg-red-500/10 text-red-400 border-red-500/20";
        if (sev === "HIGH") colorClass = "bg-orange-500/10 text-orange-400 border-orange-500/20";
        if (sev === "LOW") colorClass = "bg-blue-500/10 text-blue-400 border-blue-500/20";

        return (
          <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${colorClass}`}>
            {sev}
          </span>
        );
      },
    },
    {
      header: "Description",
      cell: (item: AuditEvent) => (
        <span className="text-zinc-400 text-sm max-w-xs truncate block">
          {item.details?.description || "No description provided"}
        </span>
      ),
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Center</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Monitor detected threats, including semantic AI attacks and deterministic violations.
        </p>
      </div>

      <DataTable 
        data={threats} 
        columns={columns} 
        keyExtractor={(item) => item.id} 
        loading={loading} 
      />
    </div>
  );
}
