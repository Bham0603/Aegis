"use client";

import React from "react";
import { useAuth } from "@/lib/auth-context";
import { usePathname } from "next/navigation";
import { LogOut, ShieldCheck, Server } from "lucide-react";

export function Topbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  
  if (pathname === "/login") return null;

  return (
    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-white/10 glass-panel px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6 justify-between items-center">
        
        {/* Left Section - Environment / Status */}
        <div className="flex items-center gap-x-4">
          <div className="flex items-center gap-x-2 text-sm text-zinc-400 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
            <Server className="h-4 w-4" />
            <span className="font-mono text-xs uppercase tracking-wider">production</span>
          </div>
          <div className="flex items-center gap-x-2 text-sm text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
            <ShieldCheck className="h-4 w-4" />
            <span className="font-medium text-xs uppercase tracking-wider">Protected</span>
          </div>
        </div>

        {/* Right Section - User */}
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          <div className="hidden sm:flex sm:flex-col sm:items-end">
            <span className="text-sm font-semibold leading-6 text-white" aria-hidden="true">
              {user?.name || "Admin"}
            </span>
            <span className="text-xs leading-5 text-zinc-400" aria-hidden="true">
              {user?.role || "Operator"}
            </span>
          </div>
          
          <div className="h-8 w-px bg-white/10" aria-hidden="true" />
          
          <button
            onClick={logout}
            className="flex items-center gap-x-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors"
          >
            <LogOut className="h-5 w-5" />
            <span className="hidden sm:block">Sign out</span>
          </button>
        </div>
      </div>
    </header>
  );
}
