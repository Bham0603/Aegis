"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Activity,
  CheckSquare,
  Users,
  Wrench,
  FileText,
  History,
  FlaskConical
} from "lucide-react";

const navigation = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Action Explorer", href: "/actions", icon: Activity },
  { name: "Threat Center", href: "/threats", icon: ShieldAlert },
  { name: "Approvals", href: "/approvals", icon: CheckSquare },
  { name: "Agent Registry", href: "/agents", icon: Users },
  { name: "Tool Registry", href: "/tools", icon: Wrench },
  { name: "Policies", href: "/policies", icon: FileText },
  { name: "Audit Logs", href: "/audit", icon: History },
  { name: "Attack Lab", href: "/attack-lab", icon: FlaskConical },
];

export function Sidebar() {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  if (isLoginPage) return null;

  return (
    <aside className="fixed inset-y-0 left-0 w-64 glass-panel border-r border-white/10 z-50 flex flex-col">
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-white/10">
        <ShieldAlert className="h-8 w-8 text-blue-500 mr-3" />
        <span className="text-xl font-bold tracking-tight text-white">AEGIS</span>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto px-4 py-6">
        <nav className="flex-1 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                  isActive 
                    ? "bg-white/10 text-white shadow-sm border border-white/5" 
                    : "text-zinc-400 hover:bg-white/5 hover:text-white"
                )}
              >
                <item.icon
                  className={cn(
                    "mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-200",
                    isActive ? "text-blue-400" : "text-zinc-500 group-hover:text-zinc-300"
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
      
      <div className="p-4 border-t border-white/10">
        <div className="glass-card p-4 flex items-center justify-center">
           <div className="text-xs text-zinc-500 font-mono text-center">
             AEGIS SECURITY ENGINE<br />
             <span className="text-emerald-500">SYSTEM ACTIVE</span>
           </div>
        </div>
      </div>
    </aside>
  );
}
