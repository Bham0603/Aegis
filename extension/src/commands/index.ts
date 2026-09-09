import * as vscode from 'vscode';
import { SecretManager } from '../auth/SecretManager';
import { AegisClient } from '../api/client';
import { Config } from '../config';
import { StatusBar } from '../status/StatusBar';
import { ActionInspectorPanel } from '../panels/ActionInspectorPanel';

export function registerCommands(context: vscode.ExtensionContext, refreshAll: () => void) {
    context.subscriptions.push(
        vscode.commands.registerCommand('aegis.configure', async () => {
            const key = await vscode.window.showInputBox({
                prompt: 'Enter Aegis API Key',
                password: true,
                ignoreFocusOut: true
            });
            if (key) {
                await SecretManager.setApiKey(key);
                vscode.window.showInformationMessage('Aegis API Key saved to SecretStorage.');
                StatusBar.refreshStatus();
                refreshAll();
            }
        }),

        vscode.commands.registerCommand('aegis.clearCredentials', async () => {
            await SecretManager.deleteApiKey();
            vscode.window.showInformationMessage('Aegis credentials cleared.');
            StatusBar.refreshStatus();
            refreshAll();
        }),

        vscode.commands.registerCommand('aegis.openDashboard', () => {
            vscode.env.openExternal(vscode.Uri.parse(Config.dashboardUrl));
        }),

        vscode.commands.registerCommand('aegis.refresh', () => {
            StatusBar.refreshStatus();
            refreshAll();
        }),

        vscode.commands.registerCommand('aegis.inspectAction', async (item: any) => {
            if (!item || !item.data) {
                return;
            }
            ActionInspectorPanel.render(context.extensionUri, item.data);
        }),

        vscode.commands.registerCommand('aegis.approve', async (item: any) => {
            if (!item || !item.data) {
                return;
            }
            const comment = await vscode.window.showInputBox({ prompt: 'Approval comment (optional)' });
            try {
                await AegisClient.resolveApproval(item.data.id, 'APPROVED', comment || 'Approved via VS Code');
                vscode.window.showInformationMessage('Action approved.');
                refreshAll();
            } catch (e: any) {
                vscode.window.showErrorMessage(`Failed to approve: ${e.message}`);
            }
        }),

        vscode.commands.registerCommand('aegis.deny', async (item: any) => {
            if (!item || !item.data) {
                return;
            }
            const comment = await vscode.window.showInputBox({ prompt: 'Denial comment (optional)' });
            try {
                await AegisClient.resolveApproval(item.data.id, 'DENIED', comment || 'Denied via VS Code');
                vscode.window.showInformationMessage('Action denied.');
                refreshAll();
            } catch (e: any) {
                vscode.window.showErrorMessage(`Failed to deny: ${e.message}`);
            }
        }),

        vscode.commands.registerCommand('aegis.runAttackLab', async () => {
            try {
                const scenarios = await AegisClient.getAttackScenarios();
                const picks = scenarios.map(s => ({
                    label: s.name,
                    description: s.id,
                    detail: s.description,
                    scenario: s
                }));
                const selection = await vscode.window.showQuickPick(picks, { title: 'Select Attack Scenario' });
                if (selection) {
                    const result = await AegisClient.runAttackScenario(selection.scenario.id);
                    ActionInspectorPanel.render(context.extensionUri, result, 'Attack Lab Result');
                    refreshAll();
                }
            } catch (e: any) {
                vscode.window.showErrorMessage(`Attack Lab error: ${e.message}`);
            }
        })
    );
}
