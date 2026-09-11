"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS, ApiError } from "@/lib/api";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { Activity, ShieldAlert, CheckSquare } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

// ---- Backend-aligned types ----
interface AuditEvent {
  event_id: string;
  action_id: string | null;
  agent_id: string | null;
  event_type: string;
  final_decision: string | null;
  timestamp: string;
}

interface ApprovalRequest {
  approval_request_id: string;
  action_id: string;
  status: string;
  created_at: string;
}

export default function OverviewPage() {
  const [recentEvents, setRecentEvents] = useState<AuditEvent[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [approvalsError, setApprovalsError] = useState<string | null>(null);

  const [stats, setStats] = useState({
    totalActions: 0,
    blockedActions: 0,
    threatsDetected: 0,
    pendingApprovals: 0,
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      // Fetch events and approvals independently so one failure doesn't break both
      const eventsResult = await api.get<AuditEvent[]>(ENDPOINTS.auditEvents({ limit: 50 }))
        .then((events) => {
          setRecentEvents(events.slice(0, 10));
          return events;
        })
        .catch((err: unknown) => {
          const msg = err instanceof ApiError ? `${err.status}: ${err.message}` : "Failed to load events";
          setEventsError(msg);
          return [] as AuditEvent[];
        });

      const approvalsResult = await api.get<ApprovalRequest[]>(ENDPOINTS.approvals({ limit: 100 }))
        .then((approvals) => {
          const pending = approvals.filter((a) => a.status === "PENDING");
          setPendingApprovals(pending.slice(0, 5));
          return approvals;
        })
        .catch((err: unknown) => {
          const msg = err instanceof ApiError ? `${err.status}: ${err.message}` : "Failed to load approvals";
          setApprovalsError(msg);
          return [] as ApprovalRequest[];
        });

      const total = eventsResult.length;
      const blocked = eventsResult.filter((e) => e.final_decision === "BLOCK").length;
      const threats = eventsResult.filter(
        (e) =>
          e.event_type === "AI_SECURITY_ANALYSIS_COMPLETED" ||
          e.event_type === "SECURITY_EVALUATION_FAILED"
      ).length;
      const pending = approvalsResult.filter((a) => a.status === "PENDING").length;

      setStats({
        totalActions: total,
        blockedActions: blocked,
        threatsDetected: threats,
        pendingApprovals: pending,
      });

      setLoading(false);
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">System Overview</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Real-time view of Aegis runtime security decisions.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <GlassCard>
          <GlassCardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500/10 p-3 rounded-lg border border-blue-500/20">
                <Activity className="h-6 w-6 text-blue-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-zinc-400">Recent Actions (50)</dt>
                  <dd className="text-2xl font-semibold text-white">{loading ? "-" : stats.totalActions}</dd>
                </dl>
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-rose-500/10 p-3 rounded-lg border border-rose-500/20">
                <ShieldAlert className="h-6 w-6 text-rose-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-zinc-400">Blocked Actions</dt>
                  <dd className="text-2xl font-semibold text-white">{loading ? "-" : stats.blockedActions}</dd>
                </dl>
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-amber-500/10 p-3 rounded-lg border border-amber-500/20">
                <ShieldAlert className="h-6 w-6 text-amber-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-zinc-400">Security Events</dt>
                  <dd className="text-2xl font-semibold text-white">{loading ? "-" : stats.threatsDetected}</dd>
                </dl>
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">
                <CheckSquare className="h-6 w-6 text-emerald-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-zinc-400">Pending Approvals</dt>
                  <dd className="text-2xl font-semibold text-white">{loading ? "-" : stats.pendingApprovals}</dd>
                </dl>
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

        {/* Recent Events */}
        <GlassCard className="flex flex-col">
          <GlassCardHeader className="flex flex-row items-center justify-between">
            <GlassCardTitle>Recent Security Events</GlassCardTitle>
            <Link href="/dashboard/audit" className="text-sm font-medium text-blue-400 hover:text-blue-300">
              View all
            </Link>
          </GlassCardHeader>
          <GlassCardContent className="flex-1 overflow-auto">
            {loading ? (
              <div className="flex justify-center p-4"><div className="animate-pulse bg-white/10 h-8 w-full rounded"></div></div>
            ) : eventsError ? (
              <div className="text-center text-red-400 py-8 text-sm font-mono">{eventsError}</div>
            ) : recentEvents.length === 0 ? (
              <div className="text-center text-zinc-500 py-8">No events found.</div>
            ) : (
              <ul className="divide-y divide-white/10">
                {recentEvents.map((event) => (
                  <li key={event.event_id} className="py-3 flex justify-between items-center">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-white truncate max-w-[200px] sm:max-w-xs">
                        {event.event_type.replace(/_/g, " ")}
                      </span>
                      <span className="text-xs text-zinc-400">
                        {format(new Date(event.timestamp), "MMM d, HH:mm:ss")} â€¢{" "}
                        {event.agent_id ? `Agent: ${event.agent_id.substring(0, 8)}...` : "No agent"}
                      </span>
                    </div>
                    <div>
                      <StatusBadge status={event.final_decision || "UNKNOWN"} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </GlassCardContent>
        </GlassCard>

        {/* Pending Approvals */}
        <GlassCard className="flex flex-col">
          <GlassCardHeader className="flex flex-row items-center justify-between">
            <GlassCardTitle>Requires Approval</GlassCardTitle>
            <Link href="/dashboard/approvals" className="text-sm font-medium text-blue-400 hover:text-blue-300">
              Go to queue
            </Link>
          </GlassCardHeader>
          <GlassCardContent className="flex-1 overflow-auto">
            {loading ? (
              <div className="flex justify-center p-4"><div className="animate-pulse bg-white/10 h-8 w-full rounded"></div></div>
            ) : approvalsError ? (
              <div className="text-center text-red-400 py-8 text-sm font-mono">{approvalsError}</div>
            ) : pendingApprovals.length === 0 ? (
              <div className="text-center text-zinc-500 py-8">No pending approvals.</div>
            ) : (
              <ul className="divide-y divide-white/10">
                {pendingApprovals.map((approval) => (
                  <li key={approval.approval_request_id} className="py-3 flex justify-between items-center">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-white">
                        Action: {approval.action_id.substring(0, 8)}...
                      </span>
                      <span className="text-xs text-zinc-400">
                        Requested {format(new Date(approval.created_at), "MMM d, HH:mm:ss")}
                      </span>
                    </div>
                    <div>
                      <Link
                        href={`/dashboard/approvals/${approval.approval_request_id}`}
                        className="text-xs glass-button px-3 py-1 text-blue-400"
                      >
                        Review
                      </Link>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </GlassCardContent>
        </GlassCard>
      </div>
    </div>
  );
}
