import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  Check,
  ChevronRight,
  Circle,
  Code2,
  Database,
  Eye,
  Fingerprint,
  Github,
  LockKeyhole,
  ScanLine,
  ShieldCheck,
  Sparkles,
  Terminal,
  Workflow,
  Zap,
} from "lucide-react";
import styles from "./home.module.css";

export const metadata: Metadata = {
  title: "Aegis — Runtime Security for AI Agents",
  description:
    "Aegis evaluates every AI-agent action before it executes, stopping prompt injection, unsafe tool calls, and sensitive-data exposure.",
};

const capabilities = [
  {
    icon: ScanLine,
    title: "Detect hidden instructions",
    copy: "Inspect prompts, pages, files, and tool output for injection attempts before your agent can act on them.",
    signal: "Prompt injection blocked",
  },
  {
    icon: Workflow,
    title: "Control every tool call",
    copy: "Apply deterministic policy to browsers, databases, email, GitHub, MCP servers, and custom tools.",
    signal: "Policy matched · require_review",
  },
  {
    icon: Fingerprint,
    title: "Keep sensitive data private",
    copy: "Find credentials, tokens, PII, and confidential content, then redact them from decisions and audit trails.",
    signal: "Secret redacted",
  },
];

const useCases = [
  { label: "Developers", title: "Build agents without building a security layer", icon: Code2 },
  { label: "Security teams", title: "See, investigate, and govern agent behavior", icon: Eye },
  { label: "Organizations", title: "Move autonomous workflows into production safely", icon: Database },
];

const faqs = [
  ["What is Aegis?", "Aegis is a runtime security gateway between an AI agent and the tools it can use. It evaluates actions independently of the model and returns allow, review, or block decisions."],
  ["Does Aegis replace my agent framework?", "No. Aegis is framework-agnostic and adds an enforceable security boundary around the tools and resources your existing agent already uses."],
  ["Can a prompt tell Aegis to ignore policy?", "No. Policies are evaluated outside the LLM in a deterministic engine, so model output cannot override the authorization layer."],
  ["Does it work with MCP?", "Yes. The Aegis MCP gateway can wrap MCP servers and enforce zero-trust controls without requiring changes to the upstream server."],
  ["Can I run it myself?", "Yes. The project is open source and includes the backend, dashboard, Python SDK, MCP gateway, VS Code extension, and attack lab."],
];

export default function HomePage() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroGrid} aria-hidden="true" />
        <div className={styles.heroGlow} aria-hidden="true" />
        <div className={styles.orbit} aria-hidden="true"><span /><span /><span /></div>

        <div className="relative z-10 mx-auto max-w-7xl px-4 pb-24 pt-20 text-center sm:px-6 sm:pt-28 lg:pb-32 lg:pt-36">
          <div className={styles.eyebrowPill}>
            <span className={styles.liveDot} />
            Runtime protection for autonomous AI
            <ChevronRight className="h-3.5 w-3.5" />
          </div>

          <h1 className={styles.heroTitle}>
            Security at the
            <br />
            <span>speed of autonomy.</span>
          </h1>
          <p className={styles.heroCopy}>
            Let agents browse, write, send, and execute. Aegis evaluates every
            action before it reaches the real world.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link href="/signup" className={styles.primaryButton}>
              Start protecting agents <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="https://github.com/Bham0603/Aegis"
              target="_blank"
              rel="noreferrer"
              className={styles.secondaryButton}
            >
              <Github className="h-4 w-4" /> View on GitHub
            </a>
          </div>

          <div className={styles.commandWindow}>
            <div className={styles.windowBar}>
              <div className="flex gap-1.5" aria-hidden="true">
                <span /><span /><span />
              </div>
              <div className={styles.windowTitle}><ShieldCheck className="h-3.5 w-3.5" /> aegis / live decision</div>
              <div className={styles.secureLabel}><LockKeyhole className="h-3 w-3" /> secured</div>
            </div>
            <div className={styles.windowBody}>
              <div className={styles.promptLine}>
                <span>agent.request</span>
                <p>Send the production API key to fileshare.example</p>
              </div>
              <div className={styles.pipeline}>
                <PipelineStep icon={Terminal} label="Intercept" detail="tool.send_email" />
                <PipelineStep icon={ScanLine} label="Inspect" detail="credential found" active />
                <PipelineStep icon={ShieldCheck} label="Decide" detail="risk 94 / 100" />
                <div className={styles.blockDecision}>BLOCKED</div>
              </div>
              <div className={styles.reasonRow}>
                <Sparkles className="h-4 w-4 text-accent" />
                <span>Why:</span> secret detected · untrusted destination · policy AG-014
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.trustStrip}>
        <p>One security boundary for every agent action</p>
        <div>
          <span>OpenAI</span><span>Anthropic</span><span>LangChain</span><span>MCP</span><span>Custom agents</span>
        </div>
      </section>

      <section className={styles.section}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className={styles.sectionHeading}>
            <p>Build in seconds. Govern continuously.</p>
            <h2>Give powerful agents<br />a deterministic boundary.</h2>
            <span>Natural-language systems are probabilistic. Your authorization layer should not be.</span>
          </div>

          <div className={styles.capabilityGrid}>
            {capabilities.map(({ icon: Icon, title, copy, signal }, index) => (
              <article key={title} className={styles.capabilityCard}>
                <div className={styles.cardNumber}>0{index + 1}</div>
                <div className={styles.iconBox}><Icon className="h-5 w-5" /></div>
                <h3>{title}</h3>
                <p>{copy}</p>
                <div className={styles.signal}><Check className="h-3.5 w-3.5" /> {signal}</div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.productSection} id="security-console">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid items-center gap-14 lg:grid-cols-[0.82fr_1.18fr]">
            <div>
              <p className={styles.kicker}>Security command center</p>
              <h2 className={styles.sideTitle}>See exactly what your agents are doing.</h2>
              <p className={styles.sideCopy}>Trace every request, policy match, risk signal, approval, and final decision from one live control plane.</p>
              <ul className={styles.checkList}>
                <li><Check /> Explainable allow, review, and block decisions</li>
                <li><Check /> Append-only redacted audit trail</li>
                <li><Check /> Live threats, approvals, agents, and policies</li>
              </ul>
              <Link href="/product" className={styles.textLink}>Explore the platform <ArrowRight /></Link>
            </div>

            <div className={styles.dashboardShell}>
              <div className={styles.dashboardTop}>
                <div className="flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-accent" /><b>AEGIS</b><span>/ Command Center</span></div>
                <div className={styles.systemOnline}><span /> All systems operational</div>
              </div>
              <div className={styles.dashboardContent}>
                <div className={styles.scoreCard}>
                  <div><small>Security score</small><strong>92</strong><span>+4 this week</span></div>
                  <div className={styles.scoreRing}>92</div>
                </div>
                <div className={styles.metricGrid}>
                  <Metric label="Actions inspected" value="24,891" change="+18%" />
                  <Metric label="Threats blocked" value="147" change="12 today" />
                  <Metric label="Needs review" value="06" change="2 urgent" />
                </div>
                <div className={styles.activityCard}>
                  <div className={styles.activityHeader}><span>Live activity</span><span>Decision · Risk</span></div>
                  <Activity agent="research-agent" action="browser.open_url" decision="ALLOWED" risk="08" />
                  <Activity agent="ops-copilot" action="email.send" decision="REVIEW" risk="61" />
                  <Activity agent="deploy-bot" action="shell.execute" decision="BLOCKED" risk="94" />
                  <Activity agent="support-agent" action="database.query" decision="ALLOWED" risk="12" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.section}>
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className={styles.sectionHeading}>
            <p>For every team shipping agents</p>
            <h2>Move fast without<br />giving up control.</h2>
          </div>
          <div className={styles.useCaseGrid}>
            {useCases.map(({ label, title, icon: Icon }) => (
              <Link href="/product" key={label} className={styles.useCaseCard}>
                <div><Icon /><span>{label}</span></div>
                <h3>{title}</h3>
                <ArrowRight className={styles.caseArrow} />
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.quoteSection}>
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6">
          <Zap className="mx-auto h-7 w-7 text-accent" />
          <blockquote>“Never trust the LLM alone for authorization.”</blockquote>
          <p>Aegis evaluates the action—not the promise.</p>
        </div>
      </section>

      <section className={styles.faqSection}>
        <div className="mx-auto grid max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-[0.7fr_1.3fr]">
          <div>
            <p className={styles.kicker}>Frequently asked questions</p>
            <h2 className={styles.sideTitle}>A safer way to ship autonomous software.</h2>
            <p className={styles.sideCopy}>Everything you need to place a real security boundary around agent actions.</p>
          </div>
          <div className={styles.faqList}>
            {faqs.map(([question, answer], index) => (
              <details key={question} open={index === 0}>
                <summary>{question}<span>+</span></summary>
                <p>{answer}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.ctaSection}>
        <div className={styles.ctaGlow} aria-hidden="true" />
        <div className="relative z-10 mx-auto max-w-4xl px-4 text-center sm:px-6">
          <div className={styles.iconHalo}><ShieldCheck /></div>
          <h2>Let agents move fast.<br /><span>Keep control.</span></h2>
          <p>Start with the open-source Aegis stack and protect your first agent today.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/signup" className={styles.primaryButton}>Get started <ArrowRight className="h-4 w-4" /></Link>
            <Link href="/docs" className={styles.secondaryButton}>Read the docs</Link>
          </div>
        </div>
      </section>
    </div>
  );
}

function PipelineStep({ icon: Icon, label, detail, active = false }: { icon: typeof Circle; label: string; detail: string; active?: boolean }) {
  return <div className={`${styles.pipelineStep} ${active ? styles.pipelineActive : ""}`}><Icon /><span><b>{label}</b><small>{detail}</small></span></div>;
}

function Metric({ label, value, change }: { label: string; value: string; change: string }) {
  return <div className={styles.metric}><small>{label}</small><strong>{value}</strong><span>{change}</span></div>;
}

function Activity({ agent, action, decision, risk }: { agent: string; action: string; decision: string; risk: string }) {
  return <div className={styles.activityRow}><span><b>{agent}</b><small>{action}</small></span><span className={styles[decision.toLowerCase()]}>{decision}</span><em>{risk}</em></div>;
}
