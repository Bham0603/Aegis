import * as vscode from 'vscode';
import { SecretManager } from './auth/SecretManager';
import { StatusBar } from './status/StatusBar';
import { registerCommands } from './commands';
import { SecurityOverviewProvider, ApprovalsProvider, AuditProvider } from './providers';
import { ThreatNotifier } from './notifications/ThreatNotifier';

export async function activate(context: vscode.ExtensionContext) {
    SecretManager.init(context);
    StatusBar.init(context);

    const overviewProvider = new SecurityOverviewProvider();
    const approvalsProvider = new ApprovalsProvider();
    const auditProvider = new AuditProvider();

    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('aegisOverview', overviewProvider),
        vscode.window.registerTreeDataProvider('aegisApprovals', approvalsProvider),
        vscode.window.registerTreeDataProvider('aegisAudit', auditProvider)
    );

    const refreshAll = () => {
        overviewProvider.refresh();
        approvalsProvider.refresh();
        auditProvider.refresh();
        StatusBar.refreshStatus();
    };

    registerCommands(context, refreshAll);

    // Initial status check
    await StatusBar.refreshStatus();
    ThreatNotifier.start(refreshAll);

    // Handle configuration changes
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('aegis.autoRefreshInterval')) {
            ThreatNotifier.start(refreshAll);
        }
    }));
}

export function deactivate() {
    ThreatNotifier.stop();
}
