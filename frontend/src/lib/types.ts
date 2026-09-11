/**
 * Aegis shared frontend types.
 * Aligned with backend schemas in app/schemas/ and app/domain/.
 * Demo/mock data is isolated in src/lib/demo-data.ts and must never
 * be scattered inside components.
 */

// ---- Auth ----
export interface User {
  id: string;
  name: string;
  role: string;
}

// ---- Audit (app/domain/audit.py AuditEvent) ----
export type AuditEventType =
  | "ACTION_RECEIVED"
  | "ACTION_EVALUATED"
  | "APPROVAL_REQUESTED"
  | "APPROVAL_APPROVED"
  | "APPROVAL_DENIED"
  | "APPROVAL_EXPIRED"
  | "SECURITY_EVALUATION_FAILED"
  | "AI_SECURITY_ANALYSIS_STARTED"
  | "AI_SECURITY_ANALYSIS_COMPLETED"
  | "AI_SECURITY_ANALYSIS_FAILED"
  | "AI_SECURITY_ANALYSIS_UNAVAILABLE";

export interface AuditEvent {
  event_id: string;
  event_version?: string;
  event_type: AuditEventType | string;
  timestamp: string;
  correlation_id: string;
  action_id: string | null;
  user_id: string | null;
  agent_id: string | null;
  session_id: string | null;
  tool_id: string | null;
  operation: string | null;
  resource: string | null;
  environment: string | null;
  permission_result: string | null;
  trust_result: string | null;
  policy_result: string | null;
  risk_score: number | null;
  risk_level: string | null;
  threat_severity: string | null;
  approval_result: string | null;
  final_decision: string | null;
  decision_reasons: string[];
  ai_provider: string | null;
  ai_model: string | null;
  ai_threat_type: string | null;
  ai_severity: string | null;
  ai_confidence: number | null;
  ai_status: string | null;
  redacted_parameters: Record<string, unknown> | null;
  metadata?: Record<string, unknown>;
}

// ---- Agents (app/schemas/registry.py AgentResponse) ----
export interface Agent {
  id: string;
  name: string;
  description: string | null;
  trust_classification: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

// ---- Tools (app/schemas/registry.py ToolResponse) ----
export interface ToolOperation {
  id: string;
  tool_id: string;
  name: string;
  description: string | null;
}

export interface Tool {
  id: string;
  canonical_name: string;
  description: string | null;
  provider: string | null;
  trust_classification: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  operations: ToolOperation[];
}

// ---- Policies (app/schemas/policy.py PolicyResponse) ----
export interface PolicyRule {
  effect: "ALLOW" | "REVIEW" | "BLOCK" | string;
  condition: Record<string, Record<string, unknown>>;
}

export interface Policy {
  id: string;
  name: string;
  description: string | null;
  version: string;
  status: string;
  priority: number;
  rules: PolicyRule[];
  created_at: string;
  updated_at: string;
}

// ---- Approvals (app/api/v1/endpoints/approvals.py) ----
export interface ApprovalRequest {
  approval_request_id: string;
  action_id: string;
  agent_id: string;
  tool_id: string;
  operation: string | null;
  resource: string | null;
  environment: string;
  status: string;
  risk_score: number | null;
  risk_level: string | null;
  reasons: string[];
  created_at: string;
  expires_at: string;
  resolved_at: string | null;
  approver_id: string | null;
}

// ---- Attack Lab ----
export interface AttackScenario {
  scenario_id: string;
  version: string;
  category: string;
  name: string;
  description: string;
  severity: string;
  expected_security_behavior: string;
  limitations?: string;
}

export interface AttackRunResult {
  run_id: string;
  scenario_id: string;
  actual_outcome: string;
  explanation: string;
  status: string;
}

// ---- Risk ----
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface RiskScore {
  score: number;
  level: RiskLevel;
}

// ---- Sensitive data findings (derived from audit redacted_parameters) ----
export type SensitiveDataCategory =
  | "API Key"
  | "Credential"
  | "Token"
  | "Personal Information"
  | "Confidential File";

export interface SensitiveDataFinding {
  id: string;
  category: SensitiveDataCategory;
  parameterKey: string;
  redactedValue: string;
  actionId: string;
  agentId: string | null;
  timestamp: string;
  environment: string | null;
  severity: RiskLevel | "NONE";
  status: string;
}

// ---- Copilot ----
export interface CopilotMessage {
  id: string;
  role: "user" | "aegis";
  content: string;
  timestamp: string;
  structured?: {
    risk?: number;
    level?: string;
    policy?: string;
    agent?: string;
    actionId?: string;
  };
}

export interface CopilotConversation {
  id: string;
  title: string;
  messages: CopilotMessage[];
  updatedAt: string;
}
