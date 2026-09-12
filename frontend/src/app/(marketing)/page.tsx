import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Terminal, Workflow, Eye, Lock, ChevronDown } from "lucide-react";
import { CinematicHero } from "@/components/marketing/CinematicHero";
import { GlowBackground } from "@/components/marketing/GlowBackground";
import { SectionHeading } from "@/components/marketing/SectionHeading";
import { SecurityConsole } from "@/components/marketing/SecurityConsole";
import { DecisionPipeline } from "@/components/marketing/DecisionPipeline";
import { AttackSimulation } from "@/components/marketing/AttackSimulation";
import { DashboardPreview } from "@/components/marketing/DashboardPreview";
import { CopilotPreview } from "@/components/marketing/CopilotPreview";
import { ExtensionPreview } from "@/components/marketing/ExtensionPreview";
import { PolicyEditorPreview } from "@/components/marketing/PolicyEditorPreview";
import { SecurityTimeline } from "@/components/marketing/SecurityTimeline";
import {
  FeatureCard,
  InjectionViz,
  ToolCallViz,
  SensitiveDataViz,
  UnauthorizedActionViz,
} from "@/components/marketing/FeatureCard";

export const metadata: Metadata = {
  title: "Aegis — The Security Layer for AI Agents",
  description:
    "Aegis is an intelligent security layer for autonomous AI agents — detecting prompt injection, unsafe actions, sensitive-data exposure and suspicious behavior before they become incidents.",
};

export default function HomePage() {
  return (
    <>
      {/* ============ 01–03 · HERO + AEGIS PROMPT + BLACK HORIZON ============ */}
      <CinematicHero />

      {/* ============ 04 · CORE CONCEPT ============ */}
      <section className="relative border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="eyebrow">Why agent security is different</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                AI agents don&apos;t just generate.
                <br />
                They act.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                Traditional security protects applications. Aegis protects
                the agent&apos;s decision and action layer — the point where
                an LLM&apos;s output becomes real-world behavior.
              </p>
              <p className="mt-4 text-base leading-relaxed text-muted">
                An LLM should never be the final authority on whether a
                sensitive action is allowed. Aegis sits between your agent
                and its tools, evaluating every action independently and
                deterministically. A malicious prompt cannot tell Aegis to
                &quot;ignore the security policy.&quot;
              </p>
            </div>

            {/* Control layer diagram */}
            <div className="panel mx-auto w-full max-w-md space-y-0 rounded-xl p-7">
              <FlowNode icon={<Terminal className="h-4 w-4" />} label="Prompt" sub="user or task" />
              <FlowArrow />
              <FlowNode icon={<Workflow className="h-4 w-4" />} label="Agent" sub="LLM decides to act" />
              <FlowArrow />
              <FlowNode
                icon={<Eye className="h-4 w-4" />}
                label="AEGIS"
                sub="observe · detect · decide · enforce"
                highlight
              />
              <FlowArrow />
              <div className="grid grid-cols-2 gap-2">
                <FlowNode icon={null} label="Tools" sub="browser · db" compact />
                <FlowNode icon={null} label="Data / APIs" sub="external calls" compact />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ 05 · SECURITY CONSOLE ============ */}
      <section id="security-console" className="relative overflow-x-clip">
        <GlowBackground />
        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <SectionHeading
            eyebrow="Security console"
            title="See what Aegis sees."
            description="Every action your agents take is intercepted, evaluated and decided — allowed, flagged for review, or blocked."
          />
          <div className="mx-auto mt-14 max-w-3xl">
            <SecurityConsole />
          </div>
        </div>
      </section>

      {/* ============ PROTECTION FEATURES ============ */}
      <section className="relative">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <SectionHeading
            eyebrow="Protection"
            title="Protect every action."
            description="Four deterministic defenses run on every action before it executes — independent of the LLM's own judgment."
          />

          <div className="mt-14 grid gap-6 md:grid-cols-2">
            <FeatureCard
              index="01"
              title="Prompt Injection Defense"
              description="Detect malicious or untrusted instructions hidden in webpages, documents, external content and tool outputs."
            >
              <InjectionViz />
            </FeatureCard>
            <FeatureCard
              index="02"
              title="Tool Call Protection"
              description="Evaluate dangerous or unexpected agent actions before execution — destructive operations, unauthorized tools, broad-scope targets."
            >
              <ToolCallViz />
            </FeatureCard>
            <FeatureCard
              index="03"
              title="Sensitive Data Protection"
              description="Detect API keys, credentials, tokens, personal information and confidential files — and redact them from every audit trail."
            >
              <SensitiveDataViz />
            </FeatureCard>
            <FeatureCard
              index="04"
              title="Unauthorized Action Detection"
              description="Identify behavior outside agent policies or expected workflows — permissions, trust classification and delegation verified on every call."
            >
              <UnauthorizedActionViz />
            </FeatureCard>
          </div>
        </div>
      </section>

      {/* ============ 06 · DECISION ENGINE ============ */}
      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="grid gap-14 lg:grid-cols-[1fr_1.2fr] lg:items-center">
            <div>
              <p className="eyebrow">Decision engine</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                Every action gets a decision.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                Aegis never trusts the LLM alone for authorization. Each
                action flows through an explainable, deterministic pipeline —
                with risk scores, matched policies and reasons recorded for
                every outcome.
              </p>

              <div className="panel mt-8 rounded-xl p-6">
                <p className="text-[11px] font-semibold uppercase tracking-widest text-foreground-muted">
                  Worked example
                </p>
                <p className="mt-3 text-sm text-foreground">
                  Agent wants to send an API credential to an external server.
                </p>
                <ul className="mt-3 space-y-1.5 font-mono text-xs text-foreground-muted">
                  <li>Sensitive credential — <span className="text-allow">detected</span></li>
                  <li>External destination — <span className="text-allow">detected</span></li>
                  <li>Unexpected behavior — <span className="text-allow">detected</span></li>
                </ul>
                <div className="mt-4 flex flex-wrap items-center gap-3 border-t border-border-base pt-4">
                  <span className="font-mono text-sm">
                    Risk <span className="font-bold text-block">94 / 100</span>
                  </span>
                  <span className="rounded-full border border-block/40 bg-block/10 px-3 py-1 font-mono text-xs font-bold tracking-widest text-block">
                    BLOCKED
                  </span>
                </div>
                <p className="mt-3 text-xs italic text-foreground-muted">
                  &quot;Untrusted destination + credential detected + abnormal agent behavior.&quot;
                </p>
              </div>
            </div>

            <div className="panel rounded-xl p-7 sm:p-9">
              <DecisionPipeline />
            </div>
          </div>
        </div>
      </section>

      {/* ============ 07 · ATTACK SIMULATION ============ */}
      <section className="relative overflow-x-clip">
        <GlowBackground />
        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <SectionHeading
            eyebrow="Live demo"
            title="See Aegis stop an attack."
            description="An interactive simulation of an indirect prompt injection hidden inside a webpage — the same scenario class shipped in the Aegis Attack Lab."
          />
          <div className="mx-auto mt-14 max-w-4xl">
            <AttackSimulation />
          </div>
        </div>
      </section>

      {/* ============ 08 · DASHBOARD PREVIEW ============ */}
      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <SectionHeading
            eyebrow="Command center"
            title="One place to understand everything your agents do."
            description="Live activity, threat breakdowns, agent risk and security trends — built from your real Aegis audit trail."
          />
          <div className="mx-auto mt-14 max-w-5xl">
            <DashboardPreview />
          </div>
        </div>
      </section>

      {/* ============ 09 · AEGIS COPILOT ============ */}
      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <div className="order-2 lg:order-1">
              <CopilotPreview />
            </div>
            <div className="order-1 lg:order-2">
              <p className="eyebrow">Aegis Copilot — AI security analyst</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                Ask your security data anything.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                Ask questions about security events, threats, agents, risk
                scores, policies and sensitive-data findings — in plain
                language, answered from your Aegis audit trail.
              </p>
              <ul className="mt-6 space-y-3 text-sm text-foreground">
                {[
                  "Why was this action blocked?",
                  "Show me the highest-risk event today.",
                  "Which agent has the highest risk?",
                  "What caused my security score to drop?",
                  "Explain this prompt injection.",
                  "Are any credentials exposed?",
                ].map((q) => (
                  <li key={q} className="flex items-start gap-2.5">
                    <ChevronDown className="mt-0.5 h-4 w-4 shrink-0 rotate-[-90deg] text-accent" aria-hidden="true" />
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* ============ 10 · VS CODE EXTENSION ============ */}
      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="eyebrow">Aegis for VS Code</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                Security follows your agent.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                The Aegis VS Code extension brings the security console into
                your IDE — monitor agent status, handle approvals and run
                attack scenarios without leaving your editor.
              </p>
              <ul className="mt-6 space-y-2.5 text-sm text-foreground">
                <li className="flex items-center gap-2.5">
                  <Lock className="h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
                  Credentials stored via VS Code secret storage — never in plaintext
                </li>
                <li className="flex items-center gap-2.5">
                  <Eye className="h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
                  Live approvals and blocked-action alerts
                </li>
              </ul>
              <div className="mt-8">
                <Link href="/extension" className="btn-primary">
                  Install Aegis Extension
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
                <p className="mt-4 font-mono text-xs text-foreground-muted">
                  VS Code · packaged as a .vsix
                </p>
              </div>
            </div>
            <ExtensionPreview />
          </div>
        </div>
      </section>

      {/* ============ 11 · POLICY ENGINE ============ */}
      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="eyebrow">Policy engine</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                You decide what agents are allowed to do.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                Express security as deterministic rules — evaluated with
                strict precedence on every action. Toggle a capability below
                to see how policies map to outcomes.
              </p>
            </div>
            <PolicyEditorPreview />
          </div>
        </div>
      </section>

      {/* ============ 12–13 · TIMELINE + AUDIENCES ============ */}
      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <div className="grid gap-14 lg:grid-cols-[1fr_1.4fr]">
            <div>
              <p className="eyebrow">Full traceability</p>
              <h2 className="headline mt-4 text-3xl sm:text-4xl">
                Trace what happened.
              </h2>
              <p className="mt-5 text-base leading-relaxed text-muted">
                Every decision is recorded in an append-only, redacted audit
                trail — so you can reconstruct exactly what happened, when,
                and why.
              </p>
              <div className="mt-10">
                <SecurityTimeline />
              </div>
            </div>

            <div>
              <p className="eyebrow">Who Aegis is for</p>
              <div className="mt-6 grid gap-5 sm:grid-cols-2">
                <AudienceCard
                  title="Developers"
                  description="Build and experiment with AI agents safely."
                />
                <AudienceCard
                  title="Security Teams"
                  description="Monitor, investigate and control agent behavior."
                />
                <AudienceCard
                  title="Organizations"
                  description="Deploy autonomous AI without giving up control."
                />
                <AudienceCard
                  title="AI Power Users"
                  description="Protect personal data and credentials."
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============ 14 · PRICING ============ */}
      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <SectionHeading
            eyebrow="Pricing"
            title="Protect your agents at any scale."
            description="Start free with the open-source release. Scale to teams and enterprises when your agents touch production."
          />
          <div className="mt-12 text-center">
            <Link href="/pricing" className="btn-secondary">
              View pricing
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>

      {/* ============ 15 · FINAL CTA ============ */}
      <section className="relative overflow-x-clip border-t border-border-base/60">
        <div
          aria-hidden="true"
          className="absolute inset-0 overflow-hidden pointer-events-none"
        >
          <div className="hero-glow-broad" />
          <div className="hero-glow-core" />
          <div className="cta-horizon" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 py-28 text-center sm:px-6 lg:py-36">
          <h2 className="headline mx-auto max-w-2xl text-4xl sm:text-5xl">
            Give your agents
            <br />
            a security layer.
          </h2>
          <p className="mx-auto mt-5 max-w-md text-base text-muted">
            Start protecting autonomous AI today.
          </p>
          <Link href="/signup" className="btn-primary mt-8">
            Get Started
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>
    </>
  );
}

function FlowNode({
  icon,
  label,
  sub,
  highlight,
  compact,
}: {
  icon: React.ReactNode | null;
  label: string;
  sub: string;
  highlight?: boolean;
  compact?: boolean;
}) {
  return (
    <div
      className={
        highlight
          ? "flex items-center gap-3 rounded-lg border border-accent-border bg-accent-dim px-4 py-3"
          : compact
            ? "flex flex-col items-center rounded-lg border border-border-base bg-background/60 px-3 py-3 text-center"
            : "flex items-center gap-3 rounded-lg border border-border-base bg-background/60 px-4 py-3"
      }
    >
      {icon && (
        <span
          className={
            highlight
              ? "text-accent"
              : "text-foreground-muted"
          }
          aria-hidden="true"
        >
          {icon}
        </span>
      )}
      <span className={highlight ? "text-sm font-bold tracking-widest text-accent" : compact ? "text-xs font-semibold text-foreground" : "text-sm font-semibold text-foreground"}>
        {label}
      </span>
      <span className="truncate font-mono text-[10px] text-foreground-muted">
        {sub}
      </span>
    </div>
  );
}

function FlowArrow() {
  return (
    <div aria-hidden="true" className="flex justify-center py-1.5">
      <svg width="12" height="16" viewBox="0 0 12 16" className="text-border-strong">
        <path d="M6 0 L6 12 M2 9 L6 13 L10 9" stroke="currentColor" strokeWidth="1.5" fill="none" />
      </svg>
    </div>
  );
}

function AudienceCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="panel panel-interactive rounded-xl p-6">
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{description}</p>
    </div>
  );
}
