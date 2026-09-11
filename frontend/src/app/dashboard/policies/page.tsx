"use client";

import React, { useEffect, useState } from "react";
import { api, ENDPOINTS } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { ErrorState } from "@/components/ui/ErrorState";
import Link from "next/link";

// ---- Backend-aligned type (app/schemas/policy.py PolicyResponse) ----
  interface PolicyRule {
    effect: string;
    condition: Record<string, Record<string, unknown>>;
  }

interface Policy {
  id: string;
  name: string;
  description: string | null;
  version: string;
  status: string; // PolicyStatus enum value: ACTIVE, INACTIVE, DRAFT
  priority: number;
  rules: PolicyRule[];
  created_at: string;
  updated_at: string;
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchPolicies = async () => {
      try {
        const data = await api.get<Policy[]>(ENDPOINTS.policies());
        data.sort((a, b) => b.priority - a.priority); // High priority first
        setPolicies(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPolicies();
  }, []);

  const columns = [
    {
      header: "Policy Name",
      cell: (item: Policy) => (
        <div className="flex flex-col">
          <span className="text-white font-medium">{item.name}</span>
          <span className="text-zinc-500 text-xs font-mono">{item.id.substring(0, 8)}...</span>
        </div>
      ),
    },
    {
      header: "Description",
      cell: (item: Policy) => (
        <span className="text-zinc-400 text-sm">{item.description || "—"}</span>
      ),
    },
    {
      header: "Rules",
      cell: (item: Policy) => (
        <div className="flex flex-wrap gap-1">
          {item.rules.length === 0 ? (
            <span className="text-zinc-500 text-sm">No rules</span>
          ) : (
            item.rules.map((rule, idx) => {
              let colorClass = "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
              if (rule.effect === "ALLOW") colorClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
              if (rule.effect === "DENY") colorClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
              if (rule.effect === "REVIEW") colorClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";
              return (
                <span
                  key={idx}
                  className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${colorClass}`}
                >
                  {rule.effect}
                </span>
              );
            })
          )}
        </div>
      ),
    },
    {
      header: "Priority",
      accessorKey: "priority" as keyof Policy,
    },
    {
      header: "Version",
      cell: (item: Policy) => (
        <span className="text-zinc-400 text-sm font-mono">{item.version}</span>
      ),
    },
    {
      header: "Status",
      cell: (item: Policy) => {
        let colorClass = "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
        if (item.status === "ACTIVE") colorClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
        if (item.status === "INACTIVE") colorClass = "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
        if (item.status === "DRAFT") colorClass = "bg-blue-500/10 text-blue-400 border-blue-500/20";
        return (
          <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${colorClass}`}>
            {item.status}
          </span>
        );
      },
    },
    {
      header: "",
      cell: (item: Policy) => (
        <Link
          href={`/dashboard/policies/${item.id}`}
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
        <h1 className="text-2xl font-bold text-white">Policy Center</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage deterministic security rules governing agent behavior.
        </p>
      </div>

      {error ? (
        <ErrorState error={error} title="Failed to load policies" />
      ) : (
        <DataTable
          data={policies}
          columns={columns}
          keyExtractor={(item) => item.id}
          loading={loading}
        />
      )}
    </div>
  );
}
