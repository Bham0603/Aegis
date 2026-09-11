import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { DecisionPipeline } from "@/components/marketing/DecisionPipeline";

export const metadata: Metadata = {
  title: "How it Works",
  description:
    "How Aegis evaluates every AI agent action: interception, permission and trust verification, deterministic policies, risk scoring, threat detection and human approvals.",
};

const STEPS = [
  {
    title: "The agent acts",
    description:
      "An autonomous agent decides to call a tool — a database, a browser, a shell, an external API. It cannot execute yet.",
  },
  {
    title: "Aegis intercepts",
    description:
      "Through the Python SDK, REST gateway or MCP Security Gateway, the action is submitted to Aegis before execution.",
  },
  {
    title: "Identity is verified",
    description:
      "The Permission Engine checks the agent's registration, tool bindings and user delegation. The Trust Engine scores the agent and session trust class.",
  },
  {
    title: "Policies decide",
    description:
      "The deterministic Policy Engine evaluates active rules with strict precedence. No matching policy means deny — the default is closed.",
  },
  {
    title: "Risk and threats are scored",
    description:
      "An explainable Risk Engine produces a 0–100 score from operation sensitivity, environment and trust. Threat detectors scan payloads for injection and dangerous patterns.",
  },
  {
    title: "The decision is enforced",
    description:
      "ALLOW, BLOCK or REVIEW — with every reason recorded. REVIEW creates a human approval request that pauses the action until a person decides.",
  },
  {
    title: "Everything is audited",
    description:
      "Every evaluation lands in an append-only audit trail with redacted parameters, full provenance and correlation IDs for end-to-end reconstruction.",
  },
];

export default function HowItWorksPage() {
  return (
    <>
      <section className="border-b border-border-base/60">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <p className="eyebrow">How it works</p>
          <h1 className="headline mt-4 max-w-2xl text-4xl sm:text-5xl">
            Observe. Detect. Understand. Decide. Enforce.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
            Aegis becomes the control layer between your agents and the real
            world. Here is exactly what happens on every action.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <ol className="relative mx-auto max-w-3xl space-y-0 border-l border-border-strong pl-8">
            {STEPS.map((step, i) => (
              <li key={step.title} className="relative pb-10 last:pb-0">
                <span
                  aria-hidden="true"
                  className="absolute -left-[37px] top-1 flex h-6 w-6 items-center justify-center rounded-full border border-border-strong bg-card font-mono text-[10px] font-bold text-accent"
                >
                  {i + 1}
                </span>
                <h2 className="text-lg font-semibold text-foreground">
                  {step.title}
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {step.description}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <div>
              <h2 className="headline text-3xl sm:text-4xl">
                The evaluation pipeline, in code order.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                This is the real sequence implemented in the Aegis
                evaluator: permission and trust run first and can short-
                circuit to BLOCK; policy sets the base decision; risk and
                threat thresholds can escalate it; human approvals resolve
                REVIEW outcomes.
              </p>
              <Link href="/docs" className="btn-secondary mt-6">
                Read the docs
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>
            <div className="panel rounded-xl p-7 sm:p-9">
              <DecisionPipeline />
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
