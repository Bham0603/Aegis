import * as vscode from 'vscode';
import { AegisClient } from '../api/client';

class AegisTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly data?: any,
        public readonly description?: string,
        public readonly iconPath?: vscode.ThemeIcon
    ) {
        super(label, collapsibleState);
        this.contextValue = data && data.id ? 'actionableItem' : 'item';
    }
}

export class SecurityOverviewProvider implements vscode.TreeDataProvider<AegisTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<AegisTreeItem | undefined | void> = new vscode.EventEmitter<AegisTreeItem | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<AegisTreeItem | undefined | void> = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: AegisTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: AegisTreeItem): Promise<AegisTreeItem[]> {
        if (!element) {
            // Root
            return [
                new AegisTreeItem('Active Threats', vscode.TreeItemCollapsibleState.Expanded, { type: 'threats' }, undefined, new vscode.ThemeIcon('error')),
                new AegisTreeItem('Recent Actions', vscode.TreeItemCollapsibleState.Expanded, { type: 'actions' }, undefined, new vscode.ThemeIcon('history'))
            ];
        }

        try {
            if (element.data.type === 'threats') {
                const threats = await AegisClient.getThreats();
                if (!threats.length) {
                    return [new AegisTreeItem('No active threats', vscode.TreeItemCollapsibleState.None)];
                }
                return threats.map(t => {
                    const label = `${t.threat_type || 'Threat'} (${t.severity})`;
                    const description = t.detector_id ? `Detector: ${t.detector_id}` : t.action_id;
                    const item = new AegisTreeItem(label, vscode.TreeItemCollapsibleState.None, t, description, new vscode.ThemeIcon('warning'));
                    item.command = { command: 'aegis.inspectAction', title: 'Inspect', arguments: [item] };
                    return item;
                });
            } else if (element.data.type === 'actions') {
                const actions = await AegisClient.getRecentActions();
                if (!actions.length) {
                    return [new AegisTreeItem('No recent actions', vscode.TreeItemCollapsibleState.None)];
                }
                return actions.map(a => {
                    const label = `${a.agent_name || 'Agent'} -> ${a.tool_name || 'Tool'}`;
                    const item = new AegisTreeItem(label, vscode.TreeItemCollapsibleState.None, a, a.decision, new vscode.ThemeIcon('output'));
                    item.command = { command: 'aegis.inspectAction', title: 'Inspect', arguments: [item] };
                    return item;
                });
            }
        } catch (e) {
            return [new AegisTreeItem('Error loading data', vscode.TreeItemCollapsibleState.None)];
        }
        return [];
    }
}

export class ApprovalsProvider implements vscode.TreeDataProvider<AegisTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<AegisTreeItem | undefined | void> = new vscode.EventEmitter<AegisTreeItem | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<AegisTreeItem | undefined | void> = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: AegisTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: AegisTreeItem): Promise<AegisTreeItem[]> {
        if (!element) {
            try {
                const approvals = await AegisClient.getPendingApprovals();
                if (!approvals.length) {
                    return [new AegisTreeItem('No pending approvals', vscode.TreeItemCollapsibleState.None, undefined, undefined, new vscode.ThemeIcon('check'))];
                }
                return approvals.map(a => {
                    const item = new AegisTreeItem(a.id, vscode.TreeItemCollapsibleState.None, a, 'PENDING', new vscode.ThemeIcon('question'));
                    item.contextValue = 'approval'; // Exposes context menu commands
                    item.command = { command: 'aegis.inspectAction', title: 'Inspect', arguments: [item] };
                    return item;
                });
            } catch (e) {
                return [new AegisTreeItem('Error loading approvals', vscode.TreeItemCollapsibleState.None)];
            }
        }
        return [];
    }
}

export class AuditProvider implements vscode.TreeDataProvider<AegisTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<AegisTreeItem | undefined | void> = new vscode.EventEmitter<AegisTreeItem | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<AegisTreeItem | undefined | void> = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: AegisTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: AegisTreeItem): Promise<AegisTreeItem[]> {
        if (!element) {
            try {
                const events = await AegisClient.getRecentActions();
                if (!events.length) {
                    return [new AegisTreeItem('No events', vscode.TreeItemCollapsibleState.None)];
                }
                return events.map(a => {
                    const item = new AegisTreeItem(a.id, vscode.TreeItemCollapsibleState.None, a, a.timestamp, new vscode.ThemeIcon('book'));
                    item.contextValue = 'auditEvent';
                    item.command = { command: 'aegis.inspectAction', title: 'Inspect', arguments: [item] };
                    return item;
                });
            } catch (e) {
                return [new AegisTreeItem('Error loading audit events', vscode.TreeItemCollapsibleState.None)];
            }
        }
        return [];
    }
}
