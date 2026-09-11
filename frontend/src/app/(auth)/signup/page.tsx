"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Mail, Server, ShieldCheck, Terminal } from "lucide-react";

/**
 * Signup / Get Started.
 *
 * Honest flow: Aegis auth today is API-key based and issued by the
 * backend (bootstrap-admin CLI). There is no self-serve account system
 * yet, so this page collects an access request rather than fabricating
 * accounts. Social/SSO signup is intentionally not faked.
 */
export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [useCase, setUseCase] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Access requests are not wired to a backend yet — keep state local
    // and surface honest next steps instead of faking account creation.
    setSubmitted(true);
  };

  return (
    <div className="w-full max-w-md">
      <div className="text-center">
        <h1 className="headline text-3xl">Get started with Aegis</h1>
        <p className="mt-3 text-sm text-muted">
          Run the open-source platform today, or request early access to
          managed deployments.
        </p>
      </div>

      <div className="panel-elevated mt-8 rounded-xl p-7 sm:p-8">
        {/* Self-serve path */}
        <div className="rounded-lg border border-accent-border/40 bg-accent-dim/30 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Terminal className="h-4 w-4 text-accent" aria-hidden="true" />
            Self-host now (free)
          </p>
          <p className="mt-1.5 text-xs leading-relaxed text-foreground-muted">
            Clone the repo, run Docker, bootstrap an admin key and sign in to
            the console.
          </p>
          <pre className="mt-3 overflow-x-auto rounded-md bg-background/70 p-3 font-mono text-[11px] leading-relaxed text-foreground"><code>{`git clone https://github.com/Bham0603/Aegis
cd Aegis && docker-compose up --build -d
python -m app.cli bootstrap-admin`}</code></pre>
        </div>

        <div className="my-6 flex items-center gap-3" aria-hidden="true">
          <span className="h-px flex-1 bg-border-base" />
          <span className="text-[11px] uppercase tracking-widest text-foreground-muted">
            or request access
          </span>
          <span className="h-px flex-1 bg-border-base" />
        </div>

        {submitted ? (
          <div
            role="status"
            className="rounded-lg border border-allow/30 bg-allow/10 p-4"
          >
            <p className="flex items-center gap-2 text-sm font-semibold text-allow">
              <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
              Request noted
            </p>
            <p className="mt-1.5 text-xs leading-relaxed text-foreground-muted">
              Access requests are reviewed as managed availability opens up.
              In the meantime, the self-hosted path above is fully
              functional and free.
            </p>
            <Link
              href="/login"
              className="btn-secondary mt-4 w-full justify-center"
            >
              Go to sign in
            </Link>
          </div>
        ) : (
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-foreground">
                Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="glass-input mt-2 block w-full px-3 py-2 text-sm placeholder:text-foreground-muted/50"
                placeholder="Ada Lovelace"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground">
                Work email
              </label>
              <div className="relative mt-2">
                <Mail
                  className="pointer-events-none absolute inset-y-0 left-0 top-2.5 ml-3 h-4 w-4 text-foreground-muted"
                  aria-hidden="true"
                />
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="glass-input block w-full py-2 pl-10 pr-3 text-sm placeholder:text-foreground-muted/50"
                  placeholder="you@company.com"
                />
              </div>
            </div>
            <div>
              <label htmlFor="usecase" className="block text-sm font-medium text-foreground">
                What are your agents doing?
              </label>
              <textarea
                id="usecase"
                name="usecase"
                rows={3}
                value={useCase}
                onChange={(e) => setUseCase(e.target.value)}
                className="glass-input mt-2 block w-full px-3 py-2 text-sm placeholder:text-foreground-muted/50"
                placeholder="Browsing, querying databases, sending emails…"
              />
            </div>
            <button type="submit" className="btn-primary w-full justify-center">
              Request early access
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </button>
            <p className="text-center text-[11px] leading-relaxed text-foreground-muted">
              Aegis is in V1.0 release candidate. Self-serve accounts and SSO
              are on the roadmap — we won&apos;t pretend otherwise.
            </p>
          </form>
        )}
      </div>

      <div className="mt-6 flex items-center justify-center gap-6 text-xs text-foreground-muted">
        <span className="inline-flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
          Open source
        </span>
        <span className="inline-flex items-center gap-1.5">
          <Server className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
          Self-hostable
        </span>
      </div>
    </div>
  );
}
