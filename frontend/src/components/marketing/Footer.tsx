import Link from "next/link";
import { Shield, Code2 } from "lucide-react";
import { AegisMark } from "./AnnouncementBar";

const PRODUCT_LINKS = [
  { name: "Product", href: "/product" },
  { name: "How it Works", href: "/how-it-works" },
  { name: "Security", href: "/security" },
  { name: "Extension", href: "/extension" },
];

const RESOURCES_LINKS = [
  { name: "Pricing", href: "/pricing" },
  { name: "Docs", href: "/docs" },
  { name: "GitHub", href: "https://github.com/Bham0603/Aegis" },
];

const ACCOUNT_LINKS = [
  { name: "Log In", href: "/login" },
  { name: "Get Started", href: "/signup" },
  { name: "Security Console", href: "/dashboard" },
];

export function Footer() {
  return (
    <footer className="border-t border-border-base bg-background-secondary">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <AegisMark />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
              The security layer for AI agents. Aegis evaluates every action
              your agents take — before it executes.
            </p>
            <a
              href="https://github.com/Bham0603/Aegis"
              className="mt-5 inline-flex items-center gap-2 text-sm text-foreground-muted transition-colors hover:text-foreground"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Code2 className="h-4 w-4" aria-hidden="true" />
              Bham0603/Aegis
            </a>
          </div>

          <FooterColumn title="Product" links={PRODUCT_LINKS} />
          <FooterColumn title="Resources" links={RESOURCES_LINKS} />
          <FooterColumn title="Account" links={ACCOUNT_LINKS} />
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-4 border-t border-border-base pt-8 sm:flex-row sm:items-center">
          <p className="text-xs text-foreground-muted">
            © {new Date().getFullYear()} Aegis. Never trust the LLM alone for
            authorization.
          </p>
          <p className="inline-flex items-center gap-2 text-xs text-foreground-muted">
            <Shield className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
            V1.0 Release Candidate
          </p>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: { name: string; href: string }[];
}) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      <ul className="mt-4 space-y-3">
        {links.map((link) => (
          <li key={link.name}>
            <Link
              href={link.href}
              className="text-sm text-foreground-muted transition-colors hover:text-foreground"
            >
              {link.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
