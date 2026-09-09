import * as vscode from 'vscode';
import { AegisClient } from '../api/client';
import { Config } from '../config';

export class ThreatNotifier {
    private static notifiedThreats: Set<string> = new Set();
    private static timer: NodeJS.Timeout | undefined;

    static start(refreshAll: () => void) {
        if (this.timer) {
            clearInterval(this.timer);
        }

        const interval = Config.autoRefreshInterval;
        if (interval > 0) {
            this.timer = setInterval(async () => {
                await this.check(refreshAll);
            }, interval * 1000);
        }
    }

    static stop() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }

    static async check(refreshAll: () => void) {
        const level = Config.notificationLevel;
        if (level === 'NONE') {
            return;
        }

        try {
            const threats = await AegisClient.getThreats();
            let newThreats = false;

            for (const t of threats) {
                if (!this.notifiedThreats.has(t.id)) {
                    this.notifiedThreats.add(t.id);
                    newThreats = true;

                    if (level === 'ALL' || t.severity === 'HIGH' || t.severity === 'CRITICAL') {
                        vscode.window.showWarningMessage(`Aegis Threat Detected: ${t.threat_type} (${t.severity})`, 'Inspect').then(choice => {
                            if (choice === 'Inspect') {
                                vscode.commands.executeCommand('aegis.inspectAction', { data: t });
                            }
                        });
                    }
                }
            }
            if (newThreats) {
                refreshAll();
            }
        } catch (e) {
            // Silently ignore connection errors during background poll
        }
    }
}
