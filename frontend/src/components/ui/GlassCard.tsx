import React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function GlassCard({ className, children, ...props }: GlassCardProps) {
  return (
    <div
      className={cn("glass-card overflow-hidden", className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function GlassCardHeader({ className, children, ...props }: GlassCardProps) {
  return (
    <div
      className={cn("px-6 py-4 border-b border-white/5", className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function GlassCardTitle({ className, children, ...props }: GlassCardProps) {
  return (
    <h3
      className={cn("text-lg font-semibold leading-6 text-white", className)}
      {...props}
    >
      {children}
    </h3>
  );
}

export function GlassCardContent({ className, children, ...props }: GlassCardProps) {
  return (
    <div
      className={cn("p-6", className)}
      {...props}
    >
      {children}
    </div>
  );
}
