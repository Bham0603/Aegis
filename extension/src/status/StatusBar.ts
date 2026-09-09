import * as vscode from 'vscode';
import { AegisClient, AegisAPIError } from '../api/client';

export class StatusBar {
    private static item: vscode.StatusBarItem;
    private static timer: NodeJS.Timeout | undefined;

    static init(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.item.command = 'aegis.openDashboard';
        context.subscriptions.push(this.item);
        this.item.show();
        this.update('Offline');
    }

    static update(state: 'Protected' | 'Offline' | 'Review Required' | 'Threat' | 'Authentication Required') {
        let text = '🛡 Aegis';
        let tooltip = 'Aegis Security Console';
        let color: vscode.ThemeColor | undefined;

        switch (state) {
            case 'Protected':
                text = '$(shield) Aegis: Protected';
                tooltip = 'Connected and Protected';
                break;
            case 'Offline':
                text = '$(circle-slash) Aegis: Offline';
                tooltip = 'Cannot connect to backend';
                break;
            case 'Authentication Required':
                text = '$(key) Aegis: Auth Required';
                tooltip = 'Click to set API Key';
                this.item.command = 'aegis.configure';
                break;
            case 'Review Required':
                text = '$(warning) Aegis: Review Required';
                tooltip = 'Pending Approvals';
                color = new vscode.ThemeColor('statusBarItem.warningBackground');
                this.item.command = 'aegis.refresh'; // open approvals view essentially
                break;
            case 'Threat':
                text = '$(error) Aegis: Threat';
                tooltip = 'Active Threats Detected';
                color = new vscode.ThemeColor('statusBarItem.errorBackground');
                this.item.command = 'aegis.refresh';
                break;
        }

        this.item.text = text;
        this.item.tooltip = tooltip;
        this.item.backgroundColor = color;
    }

    static async refreshStatus() {
        try {
            await AegisClient.ping();
            
            // If ping succeeds, check threats and approvals
            const threats = await AegisClient.getThreats();
            if (threats.length > 0) {
                this.update('Threat');
                return;
            }

            const approvals = await AegisClient.getPendingApprovals();
            if (approvals.length > 0) {
                this.update('Review Required');
                return;
            }

            this.update('Protected');
            this.item.command = 'aegis.openDashboard';

        } catch (e: any) {
            if (e.status === 401 || e.status === 403) {
                this.update('Authentication Required');
            } else {
                this.update('Offline');
            }
        }
    }
}
