"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { format } from "date-fns";

interface Tool {
  id: string;
  name: string;
  description: string;
  is_sensitive: boolean;
  created_at: string;
}

export default function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const data = await api.get<Tool[]>("/api/v1/tools/");
        setTools(data);
      } catch (error) {
        console.error("Failed to load tools", error);
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
          <span className="text-white font-medium">{item.name}</span>
          <span className="text-zinc-500 text-xs font-mono">{item.id.substring(0, 8)}...</span>
        </div>
      ),
    },
    {
      header: "Description",
      cell: (item: Tool) => (
        <span className="text-zinc-400 text-sm max-w-sm truncate block">{item.description || "-"}</span>
      ),
    },
    {
      header: "Sensitivity",
      cell: (item: Tool) => (
        item.is_sensitive ? (
          <StatusBadge status="CRITICAL" />
        ) : (
          <StatusBadge status="SAFE" />
        )
      ),
    },
    {
      header: "Created At",
      cell: (item: Tool) => format(new Date(item.created_at), "MMM d, yyyy"),
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Tool Registry</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage tools and their sensitivity classifications.
        </p>
      </div>

      <DataTable 
        data={tools} 
        columns={columns} 
        keyExtractor={(item) => item.id} 
        loading={loading} 
      />
    </div>
  );
}
