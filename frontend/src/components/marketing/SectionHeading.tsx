interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
  className?: string;
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
  className,
}: SectionHeadingProps) {
  return (
    <div
      className={
        align === "center"
          ? `mx-auto max-w-2xl text-center ${className ?? ""}`
          : `max-w-2xl ${className ?? ""}`
      }
    >
      {eyebrow && (
        <p className="eyebrow mb-3">
          {eyebrow}
        </p>
      )}
      <h2 className="headline text-3xl sm:text-4xl text-foreground">{title}</h2>
      {description && (
        <p className="mt-4 text-base leading-relaxed text-muted">
          {description}
        </p>
      )}
    </div>
  );
}
