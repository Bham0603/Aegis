"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { ErrorState } from "@/components/ui/ErrorState";
import Link from "next/link";
import { format } from "date-fns";

// ---- Backend-aligned type (app/schemas/registry.py AgentResponse) ----
interface Agent {
  id: string;
  name: string;
  description: string | null;
  trust_classification: string | null;
  status: string; // AgentStatus enum value
  created_at: string;
  updated_at: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await api.get<Agent[]>(ENDPOINTS.agents({ limit: 100 }));
        setAgents(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  const columns = [
    {
      header: "Agent Name",
      cell: (item: Agent) => (
        <div className="flex flex-col">
          <span className="text-white font-medium">{item.name}</span>
          <span className="text-zinc-500 text-xs font-mono">{item.id.substring(0, 8)}...</span>
        </div>
      ),
    },
    {
      header: "Description",
      cell: (item: Agent) => (
        <span className="text-zinc-400 text-sm">{item.description || "—"}</span>
      ),
    },
    {
      header: "Classification",
      cell: (item: Agent) => (
        <span className="text-zinc-400 text-sm">{item.trust_classification || "—"}</span>
      ),
    },
    {
      header: "Status",
      cell: (item: Agent) => <StatusBadge status={item.status} />,
    },
    {
      header: "Created At",
      cell: (item: Agent) => format(new Date(item.created_at), "MMM d, yyyy"),
    },
    {
      header: "",
      cell: (item: Agent) => (
        <Link
          href={`/dashboard/agents/${item.id}`}
          className="glass-button px-3 py-1.5 text-accent text-xs inline-block"
        >
          View
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Agent Registry</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage registered AI agents and their security classifications.
        </p>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load agents" />
      ) : (
        <DataTable
          data={agents}
          columns={columns}
          keyExtractor={(item) => item.id}
          loading={loading}
        />
      )}
    </div>
  );
}
