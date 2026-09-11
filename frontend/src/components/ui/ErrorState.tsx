import React from "react";
import { AlertCircle } from "lucide-react";
import { ApiError } from "@/lib/api";

interface ErrorStateProps {
  error: Error | ApiError | unknown;
  title?: string;
}

export function ErrorState({ error, title = "Failed to load data" }: ErrorStateProps) {
  let message = "An unexpected error occurred.";
  let status: number | undefined;

  if (error && typeof error === "object" && "status" in error) {
    const apiError = error as ApiError;
    status = apiError.status;
    message = apiError.message;
    if (apiError.data && typeof apiError.data === "object" && "detail" in apiError.data) {
      message = String((apiError.data as { detail?: unknown }).detail);
    }
  } else if (error instanceof Error) {
    message = error.message;
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center rounded-lg border border-red-500/20 bg-red-500/5">
      <AlertCircle className="h-8 w-8 text-red-500 mb-3 opacity-80" />
      <h3 className="text-lg font-medium text-zinc-200">{title}</h3>
      <p className="mt-2 text-sm text-zinc-400 max-w-md">
        {status ? (
          <span className="font-mono bg-red-500/10 text-red-400 px-1.5 py-0.5 rounded mr-2">
            {status}
          </span>
        ) : null}
        {message}
      </p>
    </div>
  );
}
