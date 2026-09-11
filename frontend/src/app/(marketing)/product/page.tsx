import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { SectionHeading } from "@/components/marketing/SectionHeading";
import { DecisionPipeline } from "@/components/marketing/DecisionPipeline";
import {
  FeatureCard,
  InjectionViz,
  ToolCallViz,
  SensitiveDataViz,
  UnauthorizedActionViz,
} from "@/components/marketing/FeatureCard";

export const metadata: Metadata = {
  title: "Product",
  description:
    "Aegis is a runtime security gateway for AI agents: action interception, deterministic policies, risk assessment, human approvals and full audit.",
};

const ARCHITECTURE_POINTS = [
  {
    title: "Intercept",
    description:
      "Agents call Aegis before executing any tool action — via the Python SDK, REST API or the MCP Security Gateway.",
  },
  {
    title: "Evaluate",
    description:
      "Permission, trust, policy, risk and threat engines run independently of the LLM, with strict precedence and fail-closed behavior.",
  },
  {
    title: "Enforce",
    description:
      "ALLOW executes, BLOCK stops the action, REVIEW pauses it for a human decision — every outcome lands in the audit trail.",
  },
];

export default function ProductPage() {
  return (
    <>
      <section className="relative overflow-hidden border-b border-border-base/60">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <p className="eyebrow">Product</p>
          <h1 className="headline mt-4 max-w-2xl text-4xl sm:text-5xl">
            A runtime security gateway for AI agents.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
            Aegis sits between autonomous agents and the tools they use.
            Every action is evaluated before it executes — so prompt
            injections, rogue agents and malicious tool responses cannot
            cause unauthorized harm.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="grid gap-6 md:grid-cols-3">
            {ARCHITECTURE_POINTS.map((point, i) => (
              <div key={point.title} className="panel rounded-xl p-6">
                <span className="font-mono text-xs text-foreground-muted/60">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h2 className="mt-3 text-lg font-semibold text-foreground">
                  {point.title}
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-muted">
                  {point.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="eyebrow">The pipeline</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                Independent. Deterministic. Explainable.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                Security evaluation is decoupled from the LLM entirely.
                Decisions are reproducible, reasons are recorded, and
                failures fail closed.
              </p>
              <Link href="/how-it-works" className="btn-secondary mt-6">
                See how it works
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>
            <div className="panel rounded-xl p-7 sm:p-9">
              <DecisionPipeline />
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <SectionHeading
            eyebrow="Defenses"
            title="Four defenses on every action."
          />
          <div className="mt-14 grid gap-6 md:grid-cols-2">
            <FeatureCard
              index="01"
              title="Prompt Injection Defense"
              description="Deterministic detectors and optional AI security intelligence analyze untrusted content and tool outputs for instruction-override attempts."
            >
              <InjectionViz />
            </FeatureCard>
            <FeatureCard
              index="02"
              title="Tool Call Protection"
              description="Dangerous operations, unauthorized tools and broad-scope targets are stopped before execution."
            >
              <ToolCallViz />
            </FeatureCard>
            <FeatureCard
              index="03"
              title="Sensitive Data Protection"
              description="Sensitive parameters are redacted before logging — keys, tokens and credentials never enter the audit trail in plaintext."
            >
              <SensitiveDataViz />
            </FeatureCard>
            <FeatureCard
              index="04"
              title="Unauthorized Action Detection"
              description="Agent identity, permissions, trust classification and user delegation are verified on every single call."
            >
              <UnauthorizedActionViz />
            </FeatureCard>
          </div>
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <SectionHeading
            eyebrow="Components"
            title="One platform, five surfaces."
          />
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <ComponentCard
              title="Python SDK"
              description="aegis_sdk — drop-in client for Python agents with typed errors for BLOCK and REVIEW outcomes."
            />
            <ComponentCard
              title="MCP Security Gateway"
              description="Zero-trust interception for any Model Context Protocol server — no server-side changes required."
            />
            <ComponentCard
              title="VS Code Extension"
              description="Approvals, agent status and attack scenarios from inside the IDE."
            />
            <ComponentCard
              title="Web Command Center"
              description="Approvals, audit exploration, policies and threat monitoring in one console."
            />
            <ComponentCard
              title="Attack Lab"
              description="Built-in adversarial scenarios to validate controls against prompt injection, exfiltration and destructive actions."
            />
            <ComponentCard
              title="Docker deployment"
              description="Production-ready docker-compose with PostgreSQL and Redis."
            />
          </div>
        </div>
      </section>
    </>
  );
}

function ComponentCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="panel panel-interactive rounded-xl p-6">
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{description}</p>
    </div>
  );
}
