"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ENDPOINTS } from "@/lib/api";
import { LogOut, Server } from "lucide-react";
import { StatusDot } from "@/components/marketing/StatusDot";

type ApiStatus = "checking" | "online" | "offline";

/**
 * Dashboard topbar. The ● Protected indicator is driven by a real
 * health check against the configured backend, not a static badge.
 */
export function Topbar() {
  const { user, logout } = useAuth();
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        await api.get<{ status: string }>(ENDPOINTS.health());
        if (!cancelled) setApiStatus("online");
      } catch {
        if (!cancelled) setApiStatus("offline");
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-border-base bg-background/90 px-4 shadow-sm backdrop-blur-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <div className="flex flex-1 items-center justify-between gap-x-4 self-stretch lg:gap-x-6">
        {/* Left: environment + protection status */}
        <div className="flex items-center gap-x-3">
          <div className="hidden items-center gap-x-2 rounded-full border border-border-base bg-card px-3 py-1.5 text-foreground-muted sm:flex">
            <Server className="h-3.5 w-3.5" aria-hidden="true" />
            <span className="font-mono text-[10px] uppercase tracking-wider">
              {process.env.NEXT_PUBLIC_API_URL
                ? new URL(process.env.NEXT_PUBLIC_API_URL).host
                : "localhost:8000"}
            </span>
          </div>
          <div
            className="flex items-center gap-x-2 rounded-full border border-allow/30 bg-allow/10 px-3 py-1.5"
            role="status"
            aria-label={
              apiStatus === "online"
                ? "Backend online, environment protected"
                : apiStatus === "offline"
                  ? "Backend unreachable"
                  : "Checking backend connection"
            }
          >
            <StatusDot
              tone={apiStatus === "offline" ? "block" : "safe"}
              pulse={apiStatus !== "offline"}
            />
            <span className="text-[10px] font-semibold uppercase tracking-wider text-allow">
              {apiStatus === "online"
                ? "Protected"
                : apiStatus === "offline"
                  ? "API Offline"
                  : "Checking"}
            </span>
          </div>
        </div>

        {/* Right: user */}
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          <div className="hidden flex-col items-end sm:flex">
            <span className="text-sm font-semibold leading-5 text-foreground">
              {user?.name || "Admin"}
            </span>
            <span className="font-mono text-[10px] uppercase leading-4 tracking-wider text-foreground-muted">
              {user?.role || "Operator"}
            </span>
          </div>

          <div className="h-8 w-px bg-border-base" aria-hidden="true" />

          <button
            onClick={logout}
            className="flex items-center gap-x-2 text-sm font-medium text-foreground-muted transition-colors hover:text-foreground"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:block">Sign out</span>
          </button>
        </div>
      </div>
    </header>
  );
}
