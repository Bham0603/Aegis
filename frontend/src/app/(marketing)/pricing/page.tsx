import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { pricing } from "@/lib/demo-data";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Aegis pricing: Free, Pro and Team/Enterprise plans. Placeholder pricing while final plans are being finalized.",
};

export default function PricingPage() {
  return (
    <>
      <section className="border-b border-border-base/60">
        <div className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6 lg:py-24">
          <p className="eyebrow">Pricing</p>
          <h1 className="headline mt-4 text-4xl sm:text-5xl">
            Protect your agents at any scale.
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted sm:text-lg">
            Start free with the open-source release. Scale to teams and
            enterprises when your agents touch production.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {pricing.tiers.map((tier) => (
              <article
                key={tier.name}
                className={cn(
                  "relative flex flex-col rounded-xl p-7",
                  tier.highlight
                    ? "panel-elevated border-accent-border shadow-2xl shadow-accent/5"
                    : "panel"
                )}
              >
                {tier.highlight && (
                  <span className="absolute -top-3 left-6 rounded-full border border-accent-border bg-accent px-3 py-0.5 text-[10px] font-bold tracking-widest text-background">
                    RECOMMENDED
                  </span>
                )}
                <h2 className="text-lg font-semibold text-foreground">{tier.name}</h2>
                <p className="mt-4">
                  <span className="font-mono text-3xl font-bold text-foreground">
                    {tier.price}
                  </span>
                  {tier.cadence && (
                    <span className="ml-2 text-xs text-foreground-muted">{tier.cadence}</span>
                  )}
                </p>
                <p className="mt-3 text-sm text-muted">{tier.description}</p>
                <ul className="mt-6 flex-1 space-y-2.5">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2.5 text-sm text-foreground">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-allow" aria-hidden="true" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href={tier.name === "Team / Enterprise" ? "/signup" : "/signup"}
                  className={cn("mt-7 justify-center", tier.highlight ? "btn-primary" : "btn-secondary")}
                >
                  {tier.cta}
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              </article>
            ))}
          </div>

          <p className="mt-8 text-center text-xs text-foreground-muted">
            {pricing.note}
          </p>
        </div>
      </section>

      <section className="border-t border-border-base/60 bg-background-secondary">
        <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
          <h2 className="text-lg font-semibold text-foreground">
            Is Aegis open source?
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-muted">
            Yes — the full platform (gateway, dashboard, SDK, MCP gateway and
            extension) is available on GitHub at Bham0603/Aegis. Self-hosting
            with Docker is free regardless of scale.
          </p>
        </div>
      </section>
    </>
  );
}
