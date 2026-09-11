import type { Metadata } from "next";
import { ExtensionPreview } from "@/components/marketing/ExtensionPreview";
import { CheckCircle2, Terminal } from "lucide-react";

export const metadata: Metadata = {
  title: "Extension",
  description:
    "The Aegis VS Code extension: manage approvals, monitor agent status and run attack scenarios without leaving your editor.",
};

const FEATURES = [
  "Approve or deny human-in-the-loop requests directly from the IDE",
  "Live status for agents, approvals and blocked actions",
  "Credentials stored via VS Code secret storage — never in plaintext",
  "Run any Attack Lab scenario from the command palette",
  "One-click opening of the web Security Console",
];

export default function ExtensionPage() {
  return (
    <>
      <section className="border-b border-border-base/60">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
          <p className="eyebrow">Extension</p>
          <h1 className="headline mt-4 max-w-2xl text-4xl sm:text-5xl">
            Security follows your agent.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
            The Aegis VS Code extension brings the security console into
            your editor — monitor agent status, handle approvals and run
            attack scenarios without leaving your code.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="grid gap-14 lg:grid-cols-2 lg:items-center">
            <ExtensionPreview />
            <div>
              <ul className="space-y-4">
                {FEATURES.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm text-foreground">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-allow" aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <h2 className="headline text-2xl sm:text-3xl">Install</h2>
          <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted">
            The extension ships as a packaged <code className="font-mono text-foreground">.vsix</code> in
            the repository. Install it from the command line or via the
            Extensions view.
          </p>
          <div className="panel mt-6 max-w-xl rounded-lg p-4">
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-widest text-foreground-muted">
              From the repository root
            </p>
            <pre className="overflow-x-auto font-mono text-xs leading-relaxed text-foreground"><code>{`cd extension
npm install
npm run compile
code --install-extension aegis-security-console-1.0.0.vsix`}</code></pre>
          </div>
          <p className="mt-4 inline-flex items-center gap-2 font-mono text-xs text-foreground-muted">
            <Terminal className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
            VS Code 1.89+ · not yet published to the Marketplace
          </p>
        </div>
      </section>
    </>
  );
}
