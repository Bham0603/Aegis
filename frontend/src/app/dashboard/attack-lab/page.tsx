"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/Badge";
import { FlaskConical, Play, CheckCircle2, XCircle, Loader2 } from "lucide-react";

interface Scenario {
  scenario_id: string;
  version: string;
  description: string;
  expected_security_behavior: string;
  category: string;
}

interface RunResult {
  run_id: string;
  actual_outcome: string;
  explanation: string;
  status: string;
}

export default function AttackLabPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Track running state and results per scenario
  const [running, setRunning] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, RunResult>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const data = await api.get<Scenario[]>("/api/v1/attack-lab/scenarios");
        setScenarios(data);
      } catch (error) {
        console.error("Failed to load scenarios", error);
      } finally {
        setLoading(false);
      }
    };

    fetchScenarios();
  }, []);

  const runScenario = async (scenarioId: string) => {
    setRunning(prev => ({ ...prev, [scenarioId]: true }));
    setErrors(prev => ({ ...prev, [scenarioId]: "" }));
    
    try {
      const result = await api.post<RunResult>(`/api/v1/attack-lab/runs`, { scenario_id: scenarioId });
      setResults(prev => ({ ...prev, [scenarioId]: result }));
    } catch (err) {
      setErrors(prev => ({ 
        ...prev, 
        [scenarioId]: err instanceof Error ? err.message : "Run failed" 
      }));
    } finally {
      setRunning(prev => ({ ...prev, [scenarioId]: false }));
    }
  };

  const runAll = async () => {
    for (const scenario of scenarios) {
      await runScenario(scenario.scenario_id);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-12">
        <div className="animate-pulse bg-white/10 h-32 w-full rounded-xl"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FlaskConical className="h-6 w-6 text-purple-400" />
            Attack Lab
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            Simulate advanced attacks and verify Aegis defense mechanisms.
          </p>
        </div>
        <button
          onClick={runAll}
          disabled={scenarios.length === 0 || Object.values(running).some(Boolean)}
          className="flex items-center gap-2 rounded-md bg-purple-600/20 px-3 py-2 text-sm font-semibold text-purple-400 border border-purple-500/30 hover:bg-purple-600/30 transition-colors disabled:opacity-50"
        >
          <Play className="h-4 w-4" />
          Run All Scenarios
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {scenarios.map(scenario => {
          const isRunning = running[scenario.scenario_id];
          const result = results[scenario.scenario_id];
          const error = errors[scenario.scenario_id];
          
          const isPass = result?.actual_outcome === scenario.expected_security_behavior;

          return (
            <GlassCard key={scenario.scenario_id} className="flex flex-col">
              <GlassCardHeader className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                      {scenario.category}
                    </span>
                    <span className="text-xs text-zinc-500 font-mono">v{scenario.version}</span>
                  </div>
                  <GlassCardTitle>{scenario.scenario_id}</GlassCardTitle>
                </div>
                <button
                  onClick={() => runScenario(scenario.scenario_id)}
                  disabled={isRunning}
                  className="glass-button p-2 text-zinc-300 hover:text-white"
                  title="Run Scenario"
                >
                  {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                </button>
              </GlassCardHeader>
              
              <GlassCardContent className="flex-1 flex flex-col">
                <p className="text-sm text-zinc-400 mb-6 flex-1">
                  {scenario.description}
                </p>
                
                <div className="bg-black/40 rounded-lg p-4 border border-white/5 mt-auto">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-zinc-500 mb-1">Expected</div>
                      <StatusBadge status={scenario.expected_security_behavior} />
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500 mb-1">Actual</div>
                      {result ? (
                        <StatusBadge status={result.actual_outcome} />
                      ) : error ? (
                        <span className="text-xs text-red-400 font-semibold">{error}</span>
                      ) : (
                        <span className="text-xs text-zinc-600 font-medium tracking-wide">NOT RUN</span>
                      )}
                    </div>
                  </div>
                  
                  {result && (
                    <div className="pt-3 border-t border-white/5">
                      <div className="flex items-center gap-2 mb-2">
                        {isPass ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                        ) : (
                          <XCircle className="h-4 w-4 text-rose-400" />
                        )}
                        <span className={`text-xs font-semibold ${isPass ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isPass ? 'VERIFIED' : 'FAILED'}
                        </span>
                      </div>
                      
                      {result.explanation && (
                        <div className="mt-2 text-xs text-zinc-400">
                          {result.explanation}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </GlassCardContent>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
}
