import React from "react";
import { cn } from "@/lib/utils";

export type BadgeVariant = "default" | "allow" | "review" | "block" | "critical" | "info";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
    allow: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    review: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    block: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    critical: "bg-red-500/10 text-red-400 border-red-500/20",
    info: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}

export function StatusBadge({ status, className }: { status?: string | null; className?: string }) {
  let variant: BadgeVariant = "default";
  
  if (!status || typeof status !== 'string') {
    return <Badge variant="default" className={className}>UNKNOWN</Badge>;
  }

  const s = status.toUpperCase();
  
  if (s === "ALLOW" || s === "APPROVED" || s === "ACTIVE" || s === "SAFE" || s === "PASS") variant = "allow";
  if (s === "REVIEW" || s === "PENDING" || s === "WARN") variant = "review";
  if (s === "BLOCK" || s === "DENIED" || s === "INACTIVE" || s === "MALICIOUS" || s === "FAIL" || s === "ERROR") variant = "block";
  if (s === "CRITICAL") variant = "critical";

  return <Badge variant={variant} className={className}>{status}</Badge>;
}
