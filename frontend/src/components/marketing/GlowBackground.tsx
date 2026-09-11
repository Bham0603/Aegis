import { cn } from "@/lib/utils";

/** Subtle atmospheric backdrop: top accent glow + faint technical grid. */
export function GlowBackground({ className }: { className?: string }) {
  return (
    <div aria-hidden="true" className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      <div className="absolute inset-0 glow-top" />
      <div className="absolute inset-0 grid-lines [mask-image:radial-gradient(ellipse_70%_60%_at_50%_0%,black_40%,transparent_100%)]" />
    </div>
  );
}
