"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Activity,
  ShieldAlert,
  CheckSquare,
  Users,
  Wrench,
  FileText,
  History,
  FlaskConical,
  Shield,
  Lock,
  BarChart3,
  Sparkles,
  Puzzle,
  Settings,
  UserCircle,
  Menu,
  X,
} from "lucide-react";

const SECTIONS = [
  {
    label: "Monitor",
    items: [
      { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
      { name: "Live Activity", href: "/dashboard/audit", icon: Activity },
      { name: "Threats", href: "/dashboard/threats", icon: ShieldAlert },
      { name: "Approvals", href: "/dashboard/approvals", icon: CheckSquare },
    ],
  },
  {
    label: "Manage",
    items: [
      { name: "Agents", href: "/dashboard/agents", icon: Users },
      { name: "Tools", href: "/dashboard/tools", icon: Wrench },
      { name: "Policies", href: "/dashboard/policies", icon: FileText },
      { name: "Action Explorer", href: "/dashboard/actions", icon: History },
    ],
  },
  {
    label: "Investigate",
    items: [
      { name: "Sensitive Data", href: "/dashboard/sensitive-data", icon: Lock },
      { name: "Reports", href: "/dashboard/reports", icon: BarChart3 },
      { name: "Copilot", href: "/dashboard/copilot", icon: Sparkles },
    ],
  },
  {
    label: "Extensions",
    items: [
      { name: "Extension", href: "/dashboard/extension", icon: Puzzle },
      { name: "Attack Lab", href: "/dashboard/attack-lab", icon: FlaskConical },
    ],
  },
];

const FOOTER_ITEMS = [
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
  { name: "Account", href: "/dashboard/account", icon: UserCircle },
];

export function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const nav = (
    <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-5" aria-label="Dashboard navigation">
      {SECTIONS.map((section) => (
        <div key={section.label}>
          <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-foreground-muted/70">
            {section.label}
          </p>
          <ul className="space-y-0.5">
            {section.items.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname?.startsWith(`${item.href}/`));
              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    aria-current={isActive ? "page" : undefined}
                    className={cn(
                      "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-card-elevated text-foreground border border-border-strong"
                        : "text-foreground-muted hover:bg-card hover:text-foreground"
                    )}
                  >
                    <item.icon
                      className={cn(
                        "mr-3 h-4 w-4 shrink-0 transition-colors",
                        isActive ? "text-accent" : "text-foreground-muted group-hover:text-foreground"
                      )}
                      aria-hidden="true"
                    />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );

  const footer = (
    <div className="border-t border-border-base p-3">
      <ul className="space-y-0.5">
        {FOOTER_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <li key={item.name}>
              <Link
                href={item.href}
                onClick={() => setMobileOpen(false)}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-card-elevated text-foreground"
                    : "text-foreground-muted hover:bg-card hover:text-foreground"
                )}
              >
                <item.icon className="mr-3 h-4 w-4 shrink-0" aria-hidden="true" />
                {item.name}
              </Link>
            </li>
          );
        })}
      </ul>
      <div className="panel mt-3 p-3 text-center">
        <p className="font-mono text-[10px] leading-relaxed text-foreground-muted">
          AEGIS SECURITY ENGINE
          <br />
          <span className="text-allow">SYSTEM ACTIVE</span>
        </p>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile top bar with hamburger */}
      <div className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-border-base bg-background/95 px-4 backdrop-blur-sm lg:hidden">
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation"
          className="rounded-md p-2 text-foreground-muted hover:text-foreground"
        >
          <Menu className="h-5 w-5" />
        </button>
        <span className="inline-flex items-center gap-2 text-base font-bold tracking-tight">
          <Shield className="h-4 w-4 text-accent" aria-hidden="true" />
          AEGIS
        </span>
        <span className="w-9" aria-hidden="true" />
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/70"
            aria-hidden="true"
            onClick={() => setMobileOpen(false)}
          />
          <aside
            role="dialog"
            aria-label="Dashboard navigation"
            className="absolute inset-y-0 left-0 flex w-72 flex-col border-r border-border-base bg-card"
          >
            <div className="flex h-14 shrink-0 items-center justify-between border-b border-border-base px-4">
              <span className="inline-flex items-center gap-2 text-base font-bold tracking-tight">
                <Shield className="h-4 w-4 text-accent" aria-hidden="true" />
                AEGIS
              </span>
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                aria-label="Close navigation"
                className="rounded-md p-2 text-foreground-muted hover:text-foreground"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            {nav}
            {footer}
          </aside>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 hidden w-64 flex-col border-r border-border-base bg-card lg:flex">
        <div className="flex h-16 shrink-0 items-center border-b border-border-base px-6">
          <Shield className="h-6 w-6 text-accent mr-2.5" aria-hidden="true" />
          <span className="text-lg font-bold tracking-tight text-foreground">AEGIS</span>
        </div>
        {nav}
        {footer}
      </aside>
    </>
  );
}
