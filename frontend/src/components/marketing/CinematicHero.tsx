"use client";

import React from "react";
import { AegisPrompt } from "./AegisPrompt";

/**
 * Cinematic centered hero — Fused-inspired composition:
 * eyebrow → headline → supporting copy → interactive prompt,
 * floating above a huge black curved horizon with atmospheric
 * green light at the intersection.
 *
 * The initial page-load reveal is pure CSS (see the
 * `aegis-*` keyframes in globals.css): the section starts at
 * 0.35 opacity and each layer rises on a slightly staggered
 * delay, so the whole composition "powers on" in ~1s with no
 * hydration flash, no JS animation loop, and an immediate
 * final state under prefers-reduced-motion.
 */
export function CinematicHero() {
  return (
    <section className="aegis-power-on relative min-h-[calc(100svh-6rem)] overflow-x-clip">
      {/* Atmospheric layers (all decorative) — the green light is
          part of the reveal: it fades in just before the text. */}
      <div
        aria-hidden="true"
        className="aegis-rise-atmosphere absolute inset-0 overflow-hidden pointer-events-none"
      >
        <div className="absolute inset-0 hero-glow-broad" />
        <div className="absolute inset-0 hero-glow-core" />
        <div className="absolute inset-0 hero-grid" />
        <div className="absolute inset-0 hero-vignette" />
      </div>

      {/* Huge black curved horizon — the security boundary.
          Clipped by an overflow-hidden wrapper so the oversized dome
          never bleeds into the next section or creates page overflow.
          It is the last layer to appear in the power-on sequence. */}
      <div
        aria-hidden="true"
        className="aegis-rise-horizon absolute inset-0 overflow-hidden pointer-events-none"
      >
        <div className="hero-horizon" />
      </div>

      {/* Content */}
      <div className="relative mx-auto flex min-h-[100svh] max-w-[800px] flex-col items-center justify-center px-4 pb-[26svh] pt-24 text-center sm:px-6">
        <p className="aegis-rise-eyebrow eyebrow tracking-[0.28em]">
          The Security Layer for AI Agents
        </p>

        <h1
          className="aegis-rise-headline headline headline-luminous mt-8 text-[clamp(2.6rem,6.2vw,56px)] tracking-[-1.12px]"
        >
          Let your agents act.
          <br />
          Aegis keeps them safe.
        </h1>

        <p className="aegis-rise-copy mt-8 max-w-[680px] text-[17px] leading-relaxed text-[#D6D9C5]">
          Aegis is an intelligent security layer for autonomous AI agents —
          detecting prompt injection, unsafe actions, sensitive-data exposure
          and suspicious behavior before they become incidents.
        </p>

        <div className="aegis-rise-prompt mt-12 w-full">
          <AegisPrompt />
        </div>

        <div className="aegis-rise-cta mt-10 flex flex-wrap items-center justify-center gap-3">
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
        </div>
      </div>
    </section>
  );
}
