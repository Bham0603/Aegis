import type { Metadata } from "next";
import { ShieldCheck, Lock, FileLock2, KeyRound, ScrollText, ServerCog } from "lucide-react";

export const metadata: Metadata = {
  title: "Security",
  description:
    "Aegis security principles: fail-closed evaluation, append-only redacted audit trails, hashed API keys, and the principle of never trusting the LLM alone for authorization.",
};

const PRINCIPLES = [
  {
    icon: ShieldCheck,
    title: "Never trust the LLM alone",
    description:
      "The LLM is untrusted for authorization. Security evaluation happens in a deterministic environment the model cannot talk its way out of — a malicious prompt cannot override policy.",
  },
  {
    icon: Lock,
    title: "Fail closed",
    description:
      "If evaluation fails — engine error, malformed action, unavailable dependency — the action is blocked, not allowed. Ambiguity never becomes access.",
  },
  {
    icon: FileLock2,
    title: "Redaction before recording",
    description:
      "Sensitive parameters (keys, tokens, credentials) are redacted before any log write. The audit trail records what happened, never your secrets.",
  },
  {
    icon: KeyRound,
    title: "Hashed credentials",
    description:
      "API keys are stored only as hashes. Bootstrap prints an admin key exactly once and refuses to generate a second one while an admin exists.",
  },
  {
    icon: ScrollText,
    title: "Append-only audit",
    description:
      "The audit API is read-only by design. There are intentionally no update or delete endpoints for audit records — provenance cannot be rewritten.",
  },
  {
    icon: ServerCog,
    title: "Hardened surface",
    description:
      "Security headers, request-size limits, rate limiting, error sanitization and strict production CORS defaults protect the gateway itself.",
  },
];

export default function SecurityPage() {
  return (
    <>
      <section className="border-b border-border-base/60">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <p className="eyebrow">Security</p>
          <h1 className="headline mt-4 max-w-2xl text-4xl sm:text-5xl">
            A security product must be secure by construction.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
            Aegis applies the same rigor to itself that it demands from
            agents. These are implemented properties of the codebase, not
            aspirations.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {PRINCIPLES.map((principle) => (
              <article key={principle.title} className="panel rounded-xl p-6">
                <principle.icon className="h-6 w-6 text-accent" aria-hidden="true" />
                <h2 className="mt-4 text-base font-semibold text-foreground">
                  {principle.title}
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {principle.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="mx-auto max-w-3xl">
            <h2 className="headline text-2xl sm:text-3xl">
              Honest about today&apos;s coverage
            </h2>
            <p className="mt-4 text-sm leading-relaxed text-muted">
              Aegis is a V1.0 release candidate. Deterministic detectors
              cover dangerous operation patterns, suspicious payloads and
              malformed actions, enforced on every evaluated action. Prompt
              injection detection is available through the AI Security
              Intelligence layer (off by default; needs a configured
              provider) — and the Attack Lab ships with limitations noted
              per scenario so you can verify exactly what is and isn&apos;t
              blocked in your environment.
            </p>
            <p className="mt-4 text-sm leading-relaxed text-muted">
              We do not claim guarantees the code does not make. Run the
              Attack Lab and see the decisions for yourself.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
