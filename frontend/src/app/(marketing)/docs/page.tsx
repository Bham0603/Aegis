import type { Metadata } from "next";
import { ArrowRight, BookOpen, Terminal, Shield, Workflow, FlaskConical, Plug, PanelsTopLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Docs",
  description:
    "Aegis documentation index: quickstart, architecture, policy model, SDK, MCP gateway, attack lab and the VS Code extension.",
};

const DOC_GROUPS = [
  {
    title: "Get started",
    docs: [
      {
        name: "Quickstart & Demo",
        href: "https://github.com/Bham0603/Aegis#quickstart--demo",
        description: "Run the end-to-end demo: ALLOW, BLOCK and REVIEW workflows.",
        icon: Terminal,
      },
      {
        name: "System Architecture",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/SYSTEM_ARCHITECTURE.md",
        description: "How the gateway, engines and audit trail fit together.",
        icon: Workflow,
      },
    ],
  },
  {
    title: "Core concepts",
    docs: [
      {
        name: "Policy Model",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/POLICY_MODEL.md",
        description: "Rules, conditions, effects (ALLOW/REVIEW/BLOCK) and precedence.",
        icon: Shield,
      },
      {
        name: "Threat Model",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/THREAT_MODEL.md",
        description: "What Aegis defends against — and what it deliberately does not.",
        icon: Shield,
      },
      {
        name: "API Contract",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/API_CONTRACT.md",
        description: "The REST surface: evaluate, registries, policies, approvals, audit.",
        icon: BookOpen,
      },
    ],
  },
  {
    title: "Integrations",
    docs: [
      {
        name: "Python SDK",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/SDK.md",
        description: "aegis_sdk: typed client with ActionBlockedError and ApprovalRequiredError.",
        icon: Terminal,
      },
      {
        name: "MCP Security Gateway",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/MCP_SECURITY.md",
        description: "Zero-trust wrapping for Model Context Protocol servers.",
        icon: Plug,
      },
      {
        name: "VS Code Extension",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/VSCODE_EXTENSION.md",
        description: "Approvals and monitoring from inside the IDE.",
        icon: PanelsTopLeft,
      },
      {
        name: "Attack Lab",
        href: "https://github.com/Bham0603/Aegis/blob/main/docs/ATTACK_LAB.md",
        description: "Validate controls against adversarial scenarios.",
        icon: FlaskConical,
      },
    ],
  },
];

export default function DocsPage() {
  return (
    <>
      <section className="border-b border-border-base/60">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-24">
          <p className="eyebrow">Docs</p>
          <h1 className="headline mt-4 text-4xl sm:text-5xl">Documentation</h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-muted sm:text-lg">
            Full documentation lives with the repository. Start here to get
            oriented.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl space-y-16 px-4 py-20 sm:px-6">
          {DOC_GROUPS.map((group) => (
            <div key={group.title}>
              <h2 className="text-sm font-semibold uppercase tracking-widest text-foreground-muted">
                {group.title}
              </h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {group.docs.map((doc) => (
                  <a
                    key={doc.name}
                    href={doc.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="panel panel-interactive group rounded-xl p-5"
                  >
                    <doc.icon className="h-5 w-5 text-accent" aria-hidden="true" />
                    <p className="mt-3 flex items-center gap-1.5 text-sm font-semibold text-foreground">
                      {doc.name}
                      <ArrowRight
                        className="h-3.5 w-3.5 text-foreground-muted transition-transform group-hover:translate-x-0.5"
                        aria-hidden="true"
                      />
                    </p>
                    <p className="mt-1.5 text-xs leading-relaxed text-muted">
                      {doc.description}
                    </p>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-3xl px-4 py-20 sm:px-6">
          <h2 className="headline text-2xl sm:text-3xl">Frequently asked</h2>
          <div className="mt-8 space-y-8">
            <Faq
              q="What is Aegis?"
              a="A runtime security gateway for AI agents. It sits between autonomous agents and their tools, evaluating every action before it executes through deterministic policies, risk scoring and threat detection — independent of the LLM."
            />
            <Faq
              q="How does Aegis protect AI agents?"
              a="By intercepting actions before execution and evaluating them through permission, trust, policy, risk and threat engines. The LLM is never the authority on authorization, evaluation fails closed, and every decision is audited."
            />
            <Faq
              q="Does Aegis work with browser-based agents?"
              a="Aegis protects any agent that routes its actions through the SDK, REST API or MCP gateway — including agents that browse the web. It does not ship a browser extension today; the shipped extension targets VS Code."
            />
            <Faq
              q="What happens when a threat is detected?"
              a="Depending on severity and policy: the action is allowed, paused for human approval (REVIEW), or blocked outright. Every outcome — including the reasons — is recorded in the audit trail, and REVIEW requests wait in the approval queue."
            />
            <Faq
              q="Can I create security policies?"
              a="Yes. Policies are rules with conditions and effects (ALLOW, REVIEW, BLOCK), evaluated with strict precedence via the API or the dashboard. The default is deny when nothing matches."
            />
            <Faq
              q="Does Aegis store prompts or browsing information?"
              a="Aegis records action metadata (agent, tool, operation, resource, environment) and redacted parameters. Sensitive values are replaced before logging. It does not record full prompts or browsing history."
            />
            <Faq
              q="Which environments are supported?"
              a="Any environment your agents run in — actions carry an environment field, and the risk engine applies stricter multipliers to production. Aegis itself runs via Docker (PostgreSQL + Redis) or locally with uvicorn."
            />
            <Faq
              q="Is Aegis open source?"
              a="Yes. The gateway, dashboard, SDK, MCP gateway and VS Code extension are all on GitHub at Bham0603/Aegis."
            />
          </div>
        </div>
      </section>
    </>
  );
}

function Faq({ q, a }: { q: string; a: string }) {
  return (
    <div>
      <h3 className="text-base font-semibold text-foreground">{q}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{a}</p>
    </div>
  );
}
