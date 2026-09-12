"use client";

import { useSafeReducedMotion } from "@/lib/use-safe-reduced-motion";

import React, { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";

/** Counts up to a target when scrolled into view. */
export function CountUp({
  to,
  duration = 1200,
  className,
}: {
  to: number;
  duration?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const [value, setValue] = useState(0);
  const reduceMotion = useSafeReducedMotion();

  useEffect(() => {
    if (!inView || reduceMotion) return;
    const start = performance.now();
    let frame: number;
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * to));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, to, duration, reduceMotion]);

  const display = reduceMotion || !inView ? to : value;

  return (
    <span ref={ref} className={className}>
      {display.toLocaleString()}
    </span>
  );
}