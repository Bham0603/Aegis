"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { Activity, ShieldCheck, ShieldAlert, CheckSquare } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

interface AuditEvent {
  id: string;
  action_id: string;
  agent_id: string;
  event_type: string;
  decision: string;
  timestamp: string;
}

interface Approval {
  id: string;
  action_id: string;
  status: string;
  created_at: string;
}

export default function OverviewPage() {
  const [recentEvents, setRecentEvents] = useState<AuditEvent[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);

  // Quick stats computed from recent fetch
  const [stats, setStats] = useState({
    totalActions: 0,
    blockedActions: 0,
    threatsDetected: 0,
    pendingApprovals: 0,
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch recent actions (limit 50)
        const events = await api.get<AuditEvent[]>("/api/v1/audit/events?limit=50");
        setRecentEvents(events.slice(0, 10)); // keep top 10 for list
        
        // Fetch pending approvals
        const approvals = await api.get<Approval[]>("/api/v1/approvals/");
        const pending = approvals.filter(a => a.status === "PENDING");
        setPendingApprovals(pending.slice(0, 5));

        // Compute basic stats from the first page of audit log
        const total = events.length;
        const blocked = events.filter(e => e.decision === "BLOCK").length;
        const threats = events.filter(e => e.event_type === "THREAT_DETECTED").length;

        setStats({
          totalActions: total,
          blockedActions: blocked,
          threatsDetected: threats,
          pendingApprovals: pending.length,
        });

      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
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
                  <dt className="truncate text-sm font-medium text-zinc-400">Active Threats</dt>
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
            <Link href="/audit" className="text-sm font-medium text-blue-400 hover:text-blue-300">
              View all
            </Link>
          </GlassCardHeader>
          <GlassCardContent className="flex-1 overflow-auto">
            {loading ? (
              <div className="flex justify-center p-4"><div className="animate-pulse bg-white/10 h-8 w-full rounded"></div></div>
            ) : recentEvents.length === 0 ? (
              <div className="text-center text-zinc-500 py-8">No events found.</div>
            ) : (
              <ul className="divide-y divide-white/10">
                {recentEvents.map((event) => (
                  <li key={event.id} className="py-3 flex justify-between items-center">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-white truncate max-w-[200px] sm:max-w-xs">
                        {event.event_type.replace(/_/g, " ")}
                      </span>
                      <span className="text-xs text-zinc-400">
                        {format(new Date(event.timestamp), "MMM d, HH:mm:ss")} • Agent: {event.agent_id.substring(0, 8)}...
                      </span>
                    </div>
                    <div>
                      <StatusBadge status={event.decision || "UNKNOWN"} />
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
            <Link href="/approvals" className="text-sm font-medium text-blue-400 hover:text-blue-300">
              Go to queue
            </Link>
          </GlassCardHeader>
          <GlassCardContent className="flex-1 overflow-auto">
            {loading ? (
              <div className="flex justify-center p-4"><div className="animate-pulse bg-white/10 h-8 w-full rounded"></div></div>
            ) : pendingApprovals.length === 0 ? (
              <div className="text-center text-zinc-500 py-8">No pending approvals.</div>
            ) : (
              <ul className="divide-y divide-white/10">
                {pendingApprovals.map((approval) => (
                  <li key={approval.id} className="py-3 flex justify-between items-center">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-white">
                        Action ID: {approval.action_id.substring(0, 8)}...
                      </span>
                      <span className="text-xs text-zinc-400">
                        Requested {format(new Date(approval.created_at), "MMM d, HH:mm:ss")}
                      </span>
                    </div>
                    <div>
                      <Link 
                        href={`/approvals/${approval.id}`}
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
