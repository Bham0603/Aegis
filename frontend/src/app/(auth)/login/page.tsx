"use client";

import React, { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { KeyRound, Loader2, AlertCircle, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(apiKey);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid API key");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="text-center">
        <h1 className="headline text-3xl">Welcome to Aegis</h1>
        <p className="mt-3 text-sm text-muted">
          Enter your API key to access the Security Console.
        </p>
      </div>

      <div className="panel-elevated mt-8 rounded-xl p-7 sm:p-8">
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="api-key"
              className="block text-sm font-medium text-foreground"
            >
              API Key
            </label>
            <div className="relative mt-2">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <KeyRound className="h-4 w-4 text-foreground-muted" aria-hidden="true" />
              </div>
              <input
                id="api-key"
                name="api-key"
                type="password"
                required
                autoComplete="off"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="glass-input block w-full py-2 pl-10 pr-3 text-sm placeholder:text-foreground-muted/50"
                placeholder="aegis-…"
                aria-describedby={error ? "login-error" : "api-key-help"}
              />
            </div>
            <p id="api-key-help" className="mt-2 text-xs text-foreground-muted">
              Keys are validated against your Aegis backend — never stored in
              plaintext.
            </p>
          </div>

          {error && (
            <div
              id="login-error"
              role="alert"
              className="rounded-lg border border-block/30 bg-block/10 p-3.5"
            >
              <div className="flex">
                <AlertCircle className="h-5 w-5 shrink-0 text-block" aria-hidden="true" />
                <div className="ml-3">
                  <h2 className="text-sm font-semibold text-block">
                    Authentication failed
                  </h2>
                  <p className="mt-1 text-xs text-foreground-muted">{error}</p>
                </div>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !apiKey}
            className="btn-primary w-full justify-center disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <>
                Sign In
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 border-t border-border-base pt-5">
          <p className="text-xs leading-relaxed text-foreground-muted">
            No API key yet? Generate one from your backend with{" "}
            <code className="rounded bg-card px-1.5 py-0.5 font-mono text-[11px] text-foreground">
              python -m app.cli bootstrap-admin
            </code>{" "}
            or{" "}
            <Link href="/signup" className="text-accent hover:underline">
              request access
            </Link>
            .
          </p>
        </div>
      </div>
    </div>
  );
}
