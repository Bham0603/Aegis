/**
 * DEMO DATA — MARKETING ONLY.
 *
 * This data backs cinematic visualizations on the public website.
 * It is illustrative and clearly isolated here; it must never be
 * presented as real security telemetry and must never be used in
 * the authenticated dashboard (which reads only from the live API).
 */

export interface ConsoleAction {
  action: string;
  target: string;
  decision: "ALLOWED" | "REVIEW" | "BLOCKED";
}

export const heroConsoleActions: ConsoleAction[] = [
  { action: "Web navigation", target: "docs.aegis.dev", decision: "ALLOWED" },
  { action: "Read webpage", target: "api reference", decision: "ALLOWED" },
  { action: "Prompt injection", target: "untrusted page content", decision: "BLOCKED" },
  { action: "External API call", target: "api.anthropic.com", decision: "REVIEW" },
  { action: "Credential access", target: ".env/production", decision: "BLOCKED" },
  { action: "Database query", target: "users table", decision: "ALLOWED" },
];

export const securityScore = 98;

export const heroConsoleStats = {
  securityScore: 98,
  actionsAnalyzed: "12,842",
  threatsBlocked: 37,
};

export const dashboardPreviewMetrics = [
  { label: "Security Score", value: "94", suffix: "/100" },
  { label: "Threats Blocked", value: "37", suffix: "" },
  { label: "Actions Analyzed", value: "12,842", suffix: "" },
  { label: "Active Agents", value: "4", suffix: "" },
];

export const dashboardPreviewActivity: ConsoleAction[] = [
  { action: "Navigate", target: "example.com", decision: "ALLOWED" },
  { action: "Prompt interpretation", target: "example.com", decision: "BLOCKED" },
  { action: "File read", target: "config.yaml", decision: "ALLOWED" },
  { action: "External POST", target: "api.evil.com", decision: "BLOCKED" },
  { action: "Database query", target: "customers", decision: "REVIEW" },
];

export const threatBreakdown = [
  { label: "Prompt Injection", count: 14, share: 38 },
  { label: "Dangerous Operations", count: 9, share: 24 },
  { label: "Suspicious Payloads", count: 8, share: 22 },
  { label: "Malformed Actions", count: 6, share: 16 },
];

export const demoTimeline = [
  { time: "09:41", label: "Agent started", tone: "neutral" },
  { time: "09:42", label: "Page accessed", tone: "neutral" },
  { time: "09:42", label: "Untrusted instruction detected", tone: "warn" },
  { time: "09:42", label: "Action blocked", tone: "block" },
  { time: "09:43", label: "User reviewed event", tone: "neutral" },
  { time: "09:44", label: "Policy updated", tone: "safe" },
] as const;

export const demoPolicies = [
  { capability: "Browser Access", effect: "ALLOW" as const },
  { capability: "Document Access", effect: "ALLOW" as const },
  { capability: "External APIs", effect: "REVIEW" as const },
  { capability: "Credential Files", effect: "BLOCK" as const },
  { capability: "Shell Execution", effect: "BLOCK" as const },
  { capability: "Data Export", effect: "REVIEW" as const },
];

export const copilotPreviewConversation = [
  {
    role: "user" as const,
    content: "Why was the browser action blocked?",
  },
  {
    role: "aegis" as const,
    content:
      "The action was blocked because untrusted page content attempted to override the agent's trusted instructions.",
    structured: {
      risk: 91,
      policy: "Prompt Injection Protection",
    },
  },
];

export const pricing = {
  note: "Placeholder pricing — final plans and limits are being finalized.",
  tiers: [
    {
      name: "Free",
      price: "$0",
      cadence: "forever",
      description: "For developers protecting a single agent locally.",
      features: [
        "1 agent",
        "Core policy engine",
        "Basic audit trail",
        "Community support",
      ],
      cta: "Start Free",
      highlight: false,
    },
    {
      name: "Pro",
      price: "$TBD",
      cadence: "per month",
      description: "For teams running agents against real tools.",
      features: [
        "Up to 10 agents",
        "Human-in-the-loop approvals",
        "AI threat intelligence",
        "Full audit history",
        "Priority support",
      ],
      cta: "Get Started",
      highlight: true,
    },
    {
      name: "Team / Enterprise",
      price: "Contact us",
      cadence: "",
      description: "For organizations deploying autonomous AI at scale.",
      features: [
        "Unlimited agents",
        "SSO & role-based access",
        "Custom policies & retention",
        "Deployment support",
        "Security review assistance",
      ],
      cta: "Contact Sales",
      highlight: false,
    },
  ],
};
