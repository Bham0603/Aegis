/* eslint-disable @typescript-eslint/naming-convention */
// Disabled naming convention because the Aegis backend schema uses snake_case for fields
// like scenario_id, action_id, threat_type, etc., and we must match the API contract exactly.

import { Config } from '../config';
import { SecretManager } from '../auth/SecretManager';

export class AegisAPIError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'AegisAPIError';
    }
}

export class AegisClient {
    private static async request<T>(path: string, options: RequestInit = {}): Promise<T> {
        const apiKey = await SecretManager.getApiKey();
        const url = `${Config.serverUrl.replace(/\/$/, '')}${path}`;
        
        const headers = new Headers(options.headers || {});
        if (apiKey) {
            headers.set('Authorization', `Bearer ${apiKey}`);
        }
        headers.set('Content-Type', 'application/json');

        const fetchOptions: RequestInit = {
            ...options,
            headers,
        };

        let response: Response;
        try {
            response = await fetch(url, fetchOptions);
        } catch (error) {
            throw new AegisAPIError(0, `Network error: Cannot connect to Aegis (${(error as Error).message})`);
        }

        if (!response.ok) {
            let errorMsg = `HTTP Error ${response.status}`;
            try {
                const errorData: any = await response.json();
                errorMsg = errorData.detail || errorMsg;
            } catch (e) {
                errorMsg = await response.text() || errorMsg;
            }
            throw new AegisAPIError(response.status, errorMsg);
        }

        if (response.status === 204) {
            return {} as T;
        }

        try {
            return await response.json() as T;
        } catch (e) {
            throw new AegisAPIError(response.status, 'Invalid JSON response from Aegis backend');
        }
    }

    static async ping() {
        // Just checking if we get a 200/401/403 instead of network error
        return this.request<any>('/api/v1/audit/events?limit=1');
    }

    static async getPendingApprovals() {
        return this.request<any[]>('/api/v1/approvals/?status=PENDING');
    }

    static async getThreats() {
        // Threats are embedded in audit events with ACTION_EVALUATED type
        // Extract from recent security evaluation events
        const events = await this.request<any[]>('/api/v1/audit/events?limit=50&event_type=ACTION_EVALUATED');

        const threats: any[] = [];
        for (const event of events) {
            // Check if this event has threat severity indicating a threat was detected
            if (event.threat_severity && event.threat_severity !== 'NONE' && event.threat_severity !== null) {
                // Extract threat details from metadata if available
                const threatDetails = event.metadata?.threat_details || [];

                if (threatDetails.length > 0) {
                    // If we have detailed threat findings, use them
                    for (const detail of threatDetails) {
                        // eslint-disable-next-line @typescript-eslint/naming-convention
                        threats.push({
                            id: `${event.action_id}-${detail.detector_id || 'unknown'}`,
                            action_id: event.action_id,
                            event_id: event.event_id,
                            threat_type: detail.threat_type || 'UNKNOWN',
                            severity: detail.severity || event.threat_severity,
                            detector_id: detail.detector_id,
                            confidence: detail.confidence,
                            timestamp: event.timestamp,
                            correlation_id: event.correlation_id,
                            reason: detail.reason || 'Threat detected',
                            agent_id: event.agent_id,
                            tool_id: event.tool_id,
                            operation: event.operation,
                            resource: event.resource
                        });
                    }
                } else {
                    // Fallback: create a single threat entry from the event-level severity
                    // eslint-disable-next-line @typescript-eslint/naming-convention
                    threats.push({
                        id: `${event.action_id}-threat`,
                        action_id: event.action_id,
                        event_id: event.event_id,
                        threat_type: 'DETECTED',
                        severity: event.threat_severity,
                        timestamp: event.timestamp,
                        correlation_id: event.correlation_id,
                        reason: event.decision_reasons?.join('; ') || 'Threat detected during evaluation',
                        agent_id: event.agent_id,
                        tool_id: event.tool_id,
                        operation: event.operation,
                        resource: event.resource
                    });
                }
            }
        }
        return threats;
    }
    
    static async getRecentActions() {
        return this.request<any[]>('/api/v1/audit/events?limit=10');
    }

    static async getApproval(id: string) {
        return this.request<any>(`/api/v1/approvals/${id}`);
    }

    static async resolveApproval(id: string, decision: 'APPROVED' | 'DENIED', comment: string) {
        return this.request<any>(`/api/v1/approvals/${id}/approve`, {
            method: 'POST',
            body: JSON.stringify({ decision, comment })
        });
    }

    static async getAttackScenarios() {
        return this.request<any[]>('/api/v1/attack-lab/scenarios');
    }

    static async runAttackScenario(scenarioId: string) {
        return this.request<any>('/api/v1/attack-lab/runs', {
            method: 'POST',
            // eslint-disable-next-line @typescript-eslint/naming-convention
            body: JSON.stringify({ scenario_id: scenarioId })
        });
    }
}
