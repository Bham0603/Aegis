"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { ErrorState } from "@/components/ui/ErrorState";
import Link from "next/link";
import { format } from "date-fns";

// ---- Backend-aligned type (app/api/v1/endpoints/approvals.py ApprovalRequestResponse) ----
interface ApprovalRequest {
  approval_request_id: string;
  action_id: string;
  agent_id: string;
  tool_id: string;
  operation: string | null;
  resource: string | null;
  environment: string;
  status: string;
  risk_score: number | null;
  risk_level: string | null;
  reasons: string[];
  created_at: string;
  expires_at: string;
  resolved_at: string | null;
  approver_id: string | null;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchApprovals = async () => {
      try {
        const data = await api.get<ApprovalRequest[]>(ENDPOINTS.approvals({ limit: 100 }));
        // Sort pending first, then by created_at desc
        data.sort((a, b) => {
          if (a.status === "PENDING" && b.status !== "PENDING") return -1;
          if (a.status !== "PENDING" && b.status === "PENDING") return 1;
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        });
        setApprovals(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchApprovals();
  }, []);

  const columns = [
    {
      header: "Request ID",
      cell: (item: ApprovalRequest) => (
        <Link
          href={`/dashboard/approvals/${item.approval_request_id}`}
          className="text-blue-400 hover:text-blue-300 font-mono text-xs"
        >
          {item.approval_request_id.substring(0, 12)}...
        </Link>
      ),
    },
    {
      header: "Action ID",
      cell: (item: ApprovalRequest) => (
        <Link
          href={`/dashboard/actions/${item.action_id}`}
          className="text-zinc-400 hover:text-white font-mono text-xs transition-colors"
        >
          {item.action_id.substring(0, 8)}...
        </Link>
      ),
    },
    {
      header: "Operation",
      cell: (item: ApprovalRequest) => (
        <span className="text-zinc-300 text-sm">{item.operation || "—"}</span>
      ),
    },
    {
      header: "Risk",
      cell: (item: ApprovalRequest) => (
        <div className="flex flex-col">
          <span className="text-zinc-300 text-sm">{item.risk_level || "UNKNOWN"}</span>
          {item.risk_score !== null && (
            <span className="text-zinc-500 text-xs">Score: {item.risk_score}</span>
          )}
        </div>
      ),
    },
    {
      header: "Status",
      cell: (item: ApprovalRequest) => <StatusBadge status={item.status} />,
    },
    {
      header: "Created At",
      cell: (item: ApprovalRequest) => format(new Date(item.created_at), "MMM d, HH:mm:ss"),
    },
    {
      header: "Action",
      cell: (item: ApprovalRequest) =>
        item.status === "PENDING" ? (
          <Link
            href={`/dashboard/approvals/${item.approval_request_id}`}
            className="text-xs glass-button px-3 py-1.5 text-blue-400 inline-block"
          >
            Review
          </Link>
        ) : (
          <span className="text-xs text-zinc-500">Resolved</span>
        ),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Approval Center</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage human-in-the-loop (HITL) approval requests for sensitive agent actions.
        </p>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load approvals" />
      ) : (
        <DataTable
          data={approvals}
          columns={columns}
          keyExtractor={(item) => item.approval_request_id}
          loading={loading}
        />
      )}
    </div>
  );
}
