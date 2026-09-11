import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { StatusBadge } from "./Badge";

describe("StatusBadge", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders valid status (ALLOW)", () => {
    render(<StatusBadge status="ALLOW" />);
    const badge = screen.getByText("ALLOW");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-emerald-500/10");
  });

  it("handles undefined status gracefully", () => {
    render(<StatusBadge status={undefined} />);
    expect(screen.getByText("UNKNOWN")).toBeInTheDocument();
  });

  it("handles null status gracefully", () => {
    render(<StatusBadge status={null} />);
    expect(screen.getByText("UNKNOWN")).toBeInTheDocument();
  });

  it("handles unknown status string", () => {
    render(<StatusBadge status="RANDOM_STATUS" />);
    const badge = screen.getByText("RANDOM_STATUS");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-zinc-500/10");
  });

  it("handles lowercase status", () => {
    render(<StatusBadge status="review" />);
    const badge = screen.getByText("review");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-amber-500/10");
  });

  it("handles unexpected backend enum", () => {
    render(<StatusBadge status="UNKNOWN_ENUM_VALUE" />);
    const badge = screen.getByText("UNKNOWN_ENUM_VALUE");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-zinc-500/10");
  });

  it("handles empty string gracefully", () => {
    render(<StatusBadge status="" />);
    expect(screen.getByText("UNKNOWN")).toBeInTheDocument();
  });
});
