import Link from "next/link";
import { Shield } from "lucide-react";

/**
 * Top announcement bar for the public site.
 * Content is intentionally non-product-launch-y and honest.
 */
export function AnnouncementBar() {
  return (
    <div className="announcement-bar relative z-50 border-b border-border-base bg-background/90 backdrop-blur-sm">
      <p className="mx-auto max-w-7xl px-4 py-2 text-center text-xs tracking-wide text-foreground-muted sm:px-6">
        Aegis is building security for the agentic era
        <span className="mx-2 text-border-strong" aria-hidden="true">·</span>
        <Link
          href="https://github.com/Bham0603/Aegis"
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent underline-offset-2 transition-colors hover:text-foreground hover:underline"
        >
          V1.0 Release Candidate → GitHub
        </Link>
      </p>
    </div>
  );
}

/** Compact Aegis wordmark used across marketing and auth surfaces. */
export function AegisMark({ withTag = false }: { withTag?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <Shield className="h-5 w-5 text-accent" aria-hidden="true" />
      <span className="text-lg font-bold tracking-tight text-foreground">
        AEGIS
      </span>
      {withTag && (
        <span className="hidden sm:inline-block border-l border-border-strong pl-2.5 text-xs font-medium uppercase tracking-widest text-foreground-muted">
          Security for AI agents
        </span>
      )}
    </span>
  );
}
