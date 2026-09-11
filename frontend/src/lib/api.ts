/**
 * Centralized API client for Aegis frontend.
 * Handles base URL configuration, common headers, and error states.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  public status: number;
  public data: unknown;

  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = "ApiError";
  }
}

// Simple event emitter for auth failures to allow the auth context to handle redirects
export const authEvents = new EventTarget();

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  // Get the token from sessionStorage (browser-only)
  if (typeof window !== "undefined") {
    const token = sessionStorage.getItem("aegis_api_key");
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);

  if (response.status === 401) {
    // Dispatch an event so the AuthProvider can clear state and redirect
    if (typeof window !== "undefined") {
      authEvents.dispatchEvent(new Event("unauthorized"));
    }
    throw new ApiError(401, "Unauthorized — session expired or invalid key");
  }

  if (!response.ok) {
    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = null;
    }
    const detail =
      errorData &&
      typeof errorData === "object" &&
      "detail" in errorData
        ? String((errorData as { detail: unknown }).detail)
        : `HTTP ${response.status}`;
    throw new ApiError(response.status, detail, errorData);
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "GET" }),

  post: <T>(endpoint: string, data: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    }),

  patch: <T>(endpoint: string, data: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "DELETE",
    }),
};

/**
 * Centralized API endpoint paths — single source of truth.
 * Update here when backend routes change.
 */
export const ENDPOINTS = {
  // Audit
  auditEvents: (params?: { limit?: number; offset?: number; event_type?: string; agent_id?: string; decision?: string }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    if (params?.event_type) q.set("event_type", params.event_type);
    if (params?.agent_id) q.set("agent_id", params.agent_id);
    if (params?.decision) q.set("decision", params.decision);
    const qs = q.toString();
    return `/api/v1/audit/events${qs ? `?${qs}` : ""}`;
  },
  auditEvent: (id: string) => `/api/v1/audit/events/${id}`,
  actionHistory: (actionId: string) => `/api/v1/audit/actions/${actionId}`,

  // Agents
  agents: (params?: { skip?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.skip) q.set("skip", String(params.skip));
    if (params?.limit) q.set("limit", String(params.limit));
    const qs = q.toString();
    return `/api/v1/agents/${qs ? `?${qs}` : ""}`;
  },
  agent: (id: string) => `/api/v1/agents/${id}`,

  // Tools
  tools: (params?: { skip?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.skip) q.set("skip", String(params.skip));
    if (params?.limit) q.set("limit", String(params.limit));
    const qs = q.toString();
    return `/api/v1/tools/${qs ? `?${qs}` : ""}`;
  },
  tool: (id: string) => `/api/v1/tools/${id}`,

  // Policies
  policies: () => `/api/v1/policies/`,
  policy: (id: string) => `/api/v1/policies/${id}`,

  // Approvals
  approvals: (params?: { skip?: number; limit?: number; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip) q.set("skip", String(params.skip));
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.status) q.set("status", params.status);
    const qs = q.toString();
    return `/api/v1/approvals/${qs ? `?${qs}` : ""}`;
  },
  approval: (id: string) => `/api/v1/approvals/${id}`,
  approveApproval: (id: string) => `/api/v1/approvals/${id}/approve`,
  denyApproval: (id: string) => `/api/v1/approvals/${id}/deny`,

  // Attack Lab
  attackLabScenarios: () => `/api/v1/attack-lab/scenarios`,
  attackLabScenario: (id: string) => `/api/v1/attack-lab/scenarios/${id}`,
  attackLabRuns: () => `/api/v1/attack-lab/runs`,
  attackLabRun: (id: string) => `/api/v1/attack-lab/runs/${id}`,

  // System
  health: () => `/health`,
  version: () => `/version`,
} as const;
