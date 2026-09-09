"use client";

import React, { useEffect, useState, use } from "react";
import { api } from "@/lib/api";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { format } from "date-fns";
import { useRouter } from "next/navigation";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

interface Approval {
  id: string;
  action_id: string;
  status: string;
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
  reason?: string;
}

export default function ApprovalDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [approval, setApproval] = useState<Approval | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionReason, setActionReason] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchApproval = async () => {
      try {
        const data = await api.get<Approval>(`/api/v1/approvals/${id}`);
        setApproval(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load approval");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchApproval();
    }
  }, [id]);

  const handleDecision = async (decision: "APPROVED" | "DENIED") => {
    setSubmitting(true);
    setError(null);
    try {
      if (decision === "APPROVED") {
        await api.post(`/api/v1/approvals/${id}/approve`, {
          approver_id: "current-user", // Backend will use current auth token for approver context ideally, but we pass what's required by schema
          reason: actionReason || "Approved via Dashboard",
        });
      } else {
        await api.post(`/api/v1/approvals/${id}/deny`, {
          approver_id: "current-user",
          reason: actionReason || "Denied via Dashboard",
        });
      }
      
      // Refresh
      const data = await api.get<Approval>(`/api/v1/approvals/${id}`);
      setApproval(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process decision");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-12">
        <div className="animate-pulse bg-white/10 h-32 w-full max-w-2xl rounded-xl"></div>
      </div>
    );
  }

  if (error || !approval) {
    return (
      <GlassCard className="max-w-2xl mx-auto mt-12">
        <GlassCardContent className="text-center py-12 text-zinc-400">
          {error || "Approval request not found."}
        </GlassCardContent>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Review Approval Request</h1>
        <p className="mt-1 text-sm text-zinc-400 font-mono">
          Approval ID: {id}
        </p>
      </div>

      <GlassCard>
        <GlassCardHeader>
          <div className="flex justify-between items-center">
            <GlassCardTitle>Request Details</GlassCardTitle>
            <StatusBadge status={approval.status} />
          </div>
        </GlassCardHeader>
        <GlassCardContent>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-sm">
            <div>
              <dt className="text-zinc-500 font-medium">Action ID</dt>
              <dd className="text-blue-400 font-mono mt-1 hover:underline cursor-pointer" onClick={() => router.push(`/actions/${approval.action_id}`)}>
                {approval.action_id}
              </dd>
            </div>
            <div>
              <dt className="text-zinc-500 font-medium">Requested At</dt>
              <dd className="text-zinc-200 mt-1">{format(new Date(approval.created_at), "PPpp")}</dd>
            </div>
            
            {approval.status !== "PENDING" && (
              <>
                <div>
                  <dt className="text-zinc-500 font-medium">Resolved At</dt>
                  <dd className="text-zinc-200 mt-1">
                    {approval.resolved_at ? format(new Date(approval.resolved_at), "PPpp") : "N/A"}
                  </dd>
                </div>
                <div>
                  <dt className="text-zinc-500 font-medium">Resolved By</dt>
                  <dd className="text-zinc-200 mt-1 font-mono">{approval.resolved_by}</dd>
                </div>
                {approval.reason && (
                  <div className="sm:col-span-2">
                    <dt className="text-zinc-500 font-medium">Reason</dt>
                    <dd className="text-zinc-200 mt-1">{approval.reason}</dd>
                  </div>
                )}
              </>
            )}
          </dl>
        </GlassCardContent>
      </GlassCard>

      {approval.status === "PENDING" && (
        <GlassCard className="border-blue-500/30 bg-blue-900/10">
          <GlassCardHeader>
            <GlassCardTitle>Provide Decision</GlassCardTitle>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="space-y-4">
              <div>
                <label htmlFor="reason" className="block text-sm font-medium leading-6 text-zinc-300">
                  Reason for Decision (Optional)
                </label>
                <div className="mt-2">
                  <textarea
                    id="reason"
                    rows={3}
                    className="block w-full rounded-md border-0 py-1.5 glass-input ring-1 ring-inset ring-white/10 placeholder:text-zinc-500 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6 px-3"
                    placeholder="Provide justification for approval or denial..."
                    value={actionReason}
                    onChange={(e) => setActionReason(e.target.value)}
                  />
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => handleDecision("APPROVED")}
                  disabled={submitting}
                  className="flex flex-1 justify-center items-center gap-2 rounded-md bg-emerald-600/20 px-3 py-2 text-sm font-semibold text-emerald-400 border border-emerald-500/30 shadow-sm hover:bg-emerald-600/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600 disabled:opacity-50 transition-all"
                >
                  {submitting ? <Loader2 className="h-5 w-5 animate-spin" /> : <CheckCircle2 className="h-5 w-5" />}
                  Approve Action
                </button>
                <button
                  onClick={() => handleDecision("DENIED")}
                  disabled={submitting}
                  className="flex flex-1 justify-center items-center gap-2 rounded-md bg-rose-600/20 px-3 py-2 text-sm font-semibold text-rose-400 border border-rose-500/30 shadow-sm hover:bg-rose-600/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-rose-600 disabled:opacity-50 transition-all"
                >
                  {submitting ? <Loader2 className="h-5 w-5 animate-spin" /> : <XCircle className="h-5 w-5" />}
                  Deny Action
                </button>
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>
      )}
    </div>
  );
}
