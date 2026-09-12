"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { AegisMark } from "./AnnouncementBar";

const NAV_LINKS = [
  { name: "Product", href: "/product" },
  { name: "How it Works", href: "/how-it-works" },
  { name: "Security", href: "/security" },
  { name: "Extension", href: "/extension" },
  { name: "Pricing", href: "/pricing" },
  { name: "Docs", href: "/docs" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const closeMenu = () => setMenuOpen(false);

  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b transition-colors duration-200",
        scrolled
          ? "border-border-base/70 bg-background/80 backdrop-blur-md"
          : "border-transparent bg-background/0 backdrop-blur-[2px]"
      )}
    >
      <nav
        aria-label="Main navigation"
        className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6"
      >
        <Link href="/" aria-label="Aegis home" className="shrink-0">
          <AegisMark />
        </Link>

        {/* Desktop nav */}
        <ul className="hidden items-center gap-1 lg:flex">
          {NAV_LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    active
                      ? "text-foreground"
                      : "text-foreground-muted hover:text-foreground"
                  )}
                >
                  {link.name}
                </Link>
              </li>
            );
          })}
        </ul>

        <div className="hidden items-center gap-3 lg:flex">
          <Link
            href="/login"
            className="rounded-md px-3 py-2 text-sm font-medium text-foreground-muted transition-colors hover:text-foreground"
          >
            Log In
          </Link>
          <Link href="/signup" className="btn-primary">
            Get Started
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          type="button"
          onClick={() => setMenuOpen((v) => !v)}
          aria-expanded={menuOpen}
          aria-controls="mobile-nav"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          className="rounded-md p-2 text-foreground-muted hover:text-foreground lg:hidden"
        >
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      {/* Mobile menu */}
      {menuOpen && (
        <div
          id="mobile-nav"
          className="border-t border-border-base bg-background lg:hidden"
        >
          <ul className="mx-auto max-w-7xl space-y-1 px-4 py-4 sm:px-6">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={closeMenu}
                  className="block rounded-md px-3 py-2.5 text-sm font-medium text-foreground-muted hover:bg-card hover:text-foreground"
                >
                  {link.name}
                </Link>
              </li>
            ))}
            <li className="flex items-center gap-3 pt-3">
              <Link href="/login" onClick={closeMenu} className="btn-secondary flex-1 justify-center">
                Log In
              </Link>
              <Link href="/signup" onClick={closeMenu} className="btn-primary flex-1 justify-center">
                Get Started
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
