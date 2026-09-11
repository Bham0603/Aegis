import { cn } from "@/lib/utils";

type Tone = "safe" | "review" | "block" | "neutral";

const toneClasses: Record<Tone, string> = {
  safe: "bg-allow",
  review: "bg-review",
  block: "bg-block",
  neutral: "bg-zinc-500",
};

const pulseClasses: Record<Tone, string> = {
  safe: "shadow-[0_0_0_0_rgba(216,255,62,0.4)]",
  review: "shadow-[0_0_0_0_rgba(245,185,66,0.4)]",
  block: "shadow-[0_0_0_0_rgba(255,90,95,0.4)]",
  neutral: "",
};

/**
 * Semantic status indicator. Color is paired with ARIA text so status is
 * never communicated by color alone.
 */
export function StatusDot({
  tone = "safe",
  pulse = false,
  className,
}: {
  tone?: Tone;
  pulse?: boolean;
  className?: string;
}) {
  return (
    <span
      role="img"
      aria-label={`${tone} status`}
      className={cn(
        "inline-block h-2 w-2 rounded-full shrink-0",
        toneClasses[tone],
        pulse && "pulse-dot",
        pulse && pulseClasses[tone],
        className
      )}
    />
  );
}
