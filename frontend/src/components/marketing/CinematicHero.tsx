"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { AegisPrompt } from "./AegisPrompt";

/**
 * Cinematic centered hero — Fused-inspired composition:
 * eyebrow → headline → supporting copy → interactive prompt,
 * floating above a huge black curved horizon with atmospheric
 * green light at the intersection.
 */
export function CinematicHero() {
  const reduceMotion = useReducedMotion();

  const fadeUp = (delay: number) => ({
    initial: reduceMotion ? false : ({ opacity: 0, y: 18 } as const),
    animate: { opacity: 1, y: 0 } as const,
    transition: { duration: 0.7, delay, ease: [0.21, 0.6, 0.35, 1] as const },
  });

  return (
    <section className="relative min-h-[calc(100svh-6rem)] overflow-x-clip">
      {/* Atmospheric layers (all decorative) */}
      <div aria-hidden="true" className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 hero-glow-broad" />
        <div className="absolute inset-0 hero-glow-core" />
        <div className="absolute inset-0 hero-grid" />
        <div className="absolute inset-0 hero-vignette" />
      </div>

      {/* Huge black curved horizon — the security boundary.
          Clipped by an overflow-hidden wrapper so the oversized dome
          never bleeds into the next section or creates page overflow. */}
      <div aria-hidden="true" className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="hero-horizon" />
      </div>

      {/* Content */}
      <div className="relative mx-auto flex min-h-[100svh] max-w-5xl flex-col items-center justify-center px-4 pb-[26svh] pt-24 text-center sm:px-6">
        <motion.p {...fadeUp(0.05)} className="eyebrow tracking-[0.28em]">
          The Security Layer for AI Agents
        </motion.p>

        <motion.h1
          {...fadeUp(0.15)}
          className="headline mt-8 text-[clamp(2.75rem,7vw,5.25rem)] text-foreground"
        >
          Let your agents act.
          <br />
          {"Aegis keeps them "}
          <span className="text-accent">safe.</span>
        </motion.h1>

        <motion.p
          {...fadeUp(0.25)}
          className="mt-8 max-w-2xl text-base leading-relaxed text-secondary sm:text-lg"
        >
          Aegis is an intelligent security layer for autonomous AI agents —
          detecting prompt injection, unsafe actions, sensitive-data exposure
          and suspicious behavior before they become incidents.
        </motion.p>

        <motion.div {...fadeUp(0.35)} className="mt-12 w-full">
          <AegisPrompt />
        </motion.div>

        <motion.div
          {...fadeUp(0.45)}
          className="mt-10 flex flex-wrap items-center justify-center gap-3"
        >
          <a href="/signup" className="btn-primary">
            Get Started
            <svg
              className="h-4 w-4"
              viewBox="0 0 16 16"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M3 8h9m0 0L8.5 4.5M12 8l-3.5 3.5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </a>
          <a href="#security-console" className="btn-secondary">
            View Security Console
          </a>
        </motion.div>
      </div>
    </section>
  );
}
