import { useSyncExternalStore } from "react";

/**
 * Hydration-safe prefers-reduced-motion.
 *
 * Returns false during SSR and the first client render (matching the
 * server snapshot), then synchronizes to the real media query state
 * immediately after hydration. No setState-in-effect: the media
 * query is an external store subscribed via useSyncExternalStore.
 * Also updates live when the user toggles the OS setting.
 */

const QUERY = "(prefers-reduced-motion: reduce)";

function subscribe(callback: () => void) {
  const mediaQueryList = window.matchMedia(QUERY);
  mediaQueryList.addEventListener("change", callback);
  return () => mediaQueryList.removeEventListener("change", callback);
}

function getSnapshot() {
  return window.matchMedia(QUERY).matches;
}

function getServerSnapshot() {
  return false;
}

export function useSafeReducedMotion() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
