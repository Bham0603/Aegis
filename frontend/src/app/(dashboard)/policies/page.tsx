"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";

interface Policy {
  id: string;
  name: string;
  effect: string; // ALLOW, DENY, REVIEW
  description?: string;
  is_active: boolean;
  priority: number;
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicies = async () => {
      try {
        const data = await api.get<Policy[]>("/api/v1/policies/");
        data.sort((a, b) => b.priority - a.priority); // High priority first
        setPolicies(data);
      } catch (error) {
        console.error("Failed to load policies", error);
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
        <span className="text-zinc-400 text-sm">{item.description || "-"}</span>
      ),
    },
    {
      header: "Effect",
      cell: (item: Policy) => {
        let variant = "default";
        if (item.effect === "ALLOW") variant = "allow";
        if (item.effect === "DENY") variant = "block";
        if (item.effect === "REVIEW") variant = "review";
        
        // Custom styling for effects
        return (
          <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold
            ${variant === "allow" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : ""}
            ${variant === "block" ? "bg-rose-500/10 text-rose-400 border-rose-500/20" : ""}
            ${variant === "review" ? "bg-amber-500/10 text-amber-400 border-amber-500/20" : ""}
          `}>
            {item.effect}
          </span>
        );
      },
    },
    {
      header: "Priority",
      accessorKey: "priority" as keyof Policy,
    },
    {
      header: "Status",
      cell: (item: Policy) => <StatusBadge status={item.is_active ? "ACTIVE" : "INACTIVE"} />,
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Policy Center</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage deterministic security rules governing agent behavior.
        </p>
      </div>

      <DataTable 
        data={policies} 
        columns={columns} 
        keyExtractor={(item) => item.id} 
        loading={loading} 
      />
    </div>
  );
}
