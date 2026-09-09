import * as vscode from 'vscode';

export class Config {
    static get serverUrl(): string {
        return vscode.workspace.getConfiguration('aegis').get<string>('serverUrl') || 'http://127.0.0.1:8000';
    }

    static get dashboardUrl(): string {
        return vscode.workspace.getConfiguration('aegis').get<string>('dashboardUrl') || 'http://localhost:3000';
    }

    static get notificationLevel(): string {
        return vscode.workspace.getConfiguration('aegis').get<string>('notificationLevel') || 'IMPORTANT';
    }

    static get autoRefreshInterval(): number {
        return vscode.workspace.getConfiguration('aegis').get<number>('autoRefreshInterval') || 30;
    }
}
