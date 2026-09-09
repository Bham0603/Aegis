"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import Link from "next/link";
import { format } from "date-fns";

interface Approval {
  id: string;
  action_id: string;
  status: string;
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        const data = await api.get<Approval[]>("/api/v1/approvals/");
        // Sort pending first, then by created_at desc
        data.sort((a, b) => {
          if (a.status === "PENDING" && b.status !== "PENDING") return -1;
          if (a.status !== "PENDING" && b.status === "PENDING") return 1;
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        });
        setApprovals(data);
      } catch (error) {
        console.error("Failed to load approvals", error);
      } finally {
        setLoading(false);
      }
    };

    fetchApprovals();
  }, []);

  const columns = [
    {
      header: "Approval ID",
      cell: (item: Approval) => (
        <Link 
          href={`/approvals/${item.id}`}
          className="text-blue-400 hover:text-blue-300 font-mono text-xs"
        >
          {item.id.substring(0, 8)}...
        </Link>
      ),
    },
    {
      header: "Action ID",
      cell: (item: Approval) => (
        <Link 
          href={`/actions/${item.action_id}`}
          className="text-zinc-400 hover:text-white font-mono text-xs transition-colors"
        >
          {item.action_id.substring(0, 8)}...
        </Link>
      ),
    },
    {
      header: "Status",
      cell: (item: Approval) => <StatusBadge status={item.status} />,
    },
    {
      header: "Created At",
      cell: (item: Approval) => format(new Date(item.created_at), "MMM d, HH:mm:ss"),
    },
    {
      header: "Action",
      cell: (item: Approval) => (
        item.status === "PENDING" ? (
          <Link 
            href={`/approvals/${item.id}`}
            className="text-xs glass-button px-3 py-1.5 text-blue-400 inline-block"
          >
            Review
          </Link>
        ) : (
          <span className="text-xs text-zinc-500">Resolved</span>
        )
      ),
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Approval Center</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage human-in-the-loop (HITL) approval requests for sensitive agent actions.
        </p>
      </div>

      <DataTable 
        data={approvals} 
        columns={columns} 
        keyExtractor={(item) => item.id} 
        loading={loading} 
      />
    </div>
  );
}
