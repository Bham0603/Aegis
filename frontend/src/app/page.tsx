"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type HealthStatus = "Connected" | "Disconnected" | "Loading";

export default function Home() {
  const [status, setStatus] = useState<HealthStatus>("Loading");
  const [details, setDetails] = useState<string | null>(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await api.get<{ status: string }>("/health");
        if (response.status === "healthy") {
          setStatus("Connected");
        } else {
          setStatus("Disconnected");
          setDetails("Backend returned unexpected status.");
        }
      } catch (err: unknown) {
        setStatus("Disconnected");
        if (err instanceof Error) {
            setDetails(err.message || "Failed to connect to backend.");
        } else {
            setDetails("Failed to connect to backend.");
        }
      }
    }

    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-8 font-sans">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Logo / Title Area */}
        <div className="space-y-4">
          <h1 className="text-6xl font-black tracking-tight bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent drop-shadow-sm">
            AEGIS
          </h1>
          <p className="text-xl text-gray-400 font-light tracking-wide">
            Runtime Security & Governance for AI Agents
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl transition-all duration-300">
          <div className="flex flex-col items-center justify-center space-y-4">
            <h2 className="text-gray-400 uppercase tracking-widest text-sm font-semibold">
              Backend Status
            </h2>
            
            <div className="flex items-center space-x-3">
              {/* Status Indicator Dot */}
              <div
                className={`w-4 h-4 rounded-full shadow-lg ${
                  status === "Connected"
                    ? "bg-green-500 shadow-green-500/50"
                    : status === "Loading"
                    ? "bg-yellow-500 shadow-yellow-500/50 animate-pulse"
                    : "bg-red-500 shadow-red-500/50"
                }`}
              />
              
              <span className={`text-2xl font-bold tracking-wide ${
                status === "Connected" ? "text-green-400" :
                status === "Loading" ? "text-yellow-400" :
                "text-red-400"
              }`}>
                {status}
              </span>
            </div>

            {/* Error Details if disconnected */}
            {status === "Disconnected" && details && (
              <p className="text-sm text-gray-500 bg-gray-950 px-4 py-2 rounded-lg border border-gray-800">
                {details}
              </p>
            )}
          </div>
        </div>

        {/* Footer info */}
        <div className="pt-12 text-sm text-gray-600">
          <p>Phase 1 MVP Foundation</p>
          <p className="mt-1">© {new Date().getFullYear()} Experiential Labs</p>
        </div>
      </div>
    </div>
  );
}
