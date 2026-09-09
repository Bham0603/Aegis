"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { format } from "date-fns";

interface Agent {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  is_active: boolean;
  created_at: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await api.get<Agent[]>("/api/v1/agents/");
        setAgents(data);
      } catch (error) {
        console.error("Failed to load agents", error);
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
        <span className="text-zinc-400 text-sm">{item.description || "-"}</span>
      ),
    },
    {
      header: "Status",
      cell: (item: Agent) => <StatusBadge status={item.is_active ? "ACTIVE" : "INACTIVE"} />,
    },
    {
      header: "Created At",
      cell: (item: Agent) => format(new Date(item.created_at), "MMM d, yyyy"),
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Agent Registry</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage registered AI agents and their status.
        </p>
      </div>

      <DataTable 
        data={agents} 
        columns={columns} 
        keyExtractor={(item) => item.id} 
        loading={loading} 
      />
    </div>
  );
}
