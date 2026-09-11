"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { ErrorState } from "@/components/ui/ErrorState";
import { format } from "date-fns";

// ---- Backend-aligned type (app/schemas/registry.py ToolResponse) ----
interface ToolOperation {
  id: string;
  tool_id: string;
  name: string;
  description: string | null;
}

interface Tool {
  id: string;
  canonical_name: string;
  description: string | null;
  provider: string | null;
  trust_classification: string | null;
  status: string; // ToolStatus enum value
  created_at: string;
  updated_at: string;
  operations: ToolOperation[];
}

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const data = await api.get<Tool[]>(ENDPOINTS.tools({ limit: 100 }));
        setTools(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTools();
  }, []);

  const columns = [
    {
      header: "Tool Name",
      cell: (item: Tool) => (
        <div className="flex flex-col">
          <span className="text-white font-medium">{item.canonical_name}</span>
          <span className="text-zinc-500 text-xs font-mono">{item.id.substring(0, 8)}...</span>
        </div>
      ),
    },
    {
      header: "Provider",
      cell: (item: Tool) => (
        <span className="text-zinc-400 text-sm">{item.provider || "—"}</span>
      ),
    },
    {
      header: "Description",
      cell: (item: Tool) => (
        <span className="text-zinc-400 text-sm max-w-sm truncate block">
          {item.description || "—"}
        </span>
      ),
    },
    {
      header: "Operations",
      cell: (item: Tool) => (
        <span className="text-zinc-400 text-sm">
          {item.operations.length > 0
            ? item.operations.map((o) => o.name).join(", ")
            : "—"}
        </span>
      ),
    },
    {
      header: "Classification",
      cell: (item: Tool) => (
        <span className="text-zinc-400 text-sm">{item.trust_classification || "—"}</span>
      ),
    },
    {
      header: "Status",
      cell: (item: Tool) => <StatusBadge status={item.status} />,
    },
    {
      header: "Created At",
      cell: (item: Tool) => format(new Date(item.created_at), "MMM d, yyyy"),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Tool Registry</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage registered tools and their security classifications.
        </p>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load tools" />
      ) : (
        <DataTable
          data={tools}
          columns={columns}
          keyExtractor={(item) => item.id}
          loading={loading}
        />
      )}
    </div>
  );
}
