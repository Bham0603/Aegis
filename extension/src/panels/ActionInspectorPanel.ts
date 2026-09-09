import * as vscode from 'vscode';

export class ActionInspectorPanel {
    public static currentPanel: ActionInspectorPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, data: any, title: string) {
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = this._getHtmlForWebview(this._panel.webview, data, title);
    }

    public static render(extensionUri: vscode.Uri, data: any, title = 'Action Inspector') {
        if (ActionInspectorPanel.currentPanel) {
            ActionInspectorPanel.currentPanel._panel.reveal(vscode.ViewColumn.One);
            ActionInspectorPanel.currentPanel._panel.webview.html = ActionInspectorPanel.currentPanel._getHtmlForWebview(ActionInspectorPanel.currentPanel._panel.webview, data, title);
        } else {
            const panel = vscode.window.createWebviewPanel(
                'aegisActionInspector',
                title,
                vscode.ViewColumn.One,
                { enableScripts: false } // strict CSP, no scripts
            );

            ActionInspectorPanel.currentPanel = new ActionInspectorPanel(panel, extensionUri, data, title);
        }
    }

    public dispose() {
        ActionInspectorPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview, data: any, title: string) {
        // Strict CSP
        const json = JSON.stringify(data, null, 2).replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource};">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>${title}</title>
                <style>
                    body { font-family: var(--vscode-editor-font-family); padding: 10px; color: var(--vscode-editor-foreground); background-color: var(--vscode-editor-background); }
                    pre { background-color: var(--vscode-textCodeBlock-background); padding: 10px; border-radius: 5px; overflow-x: auto; }
                    h2 { color: var(--vscode-editorInfo-foreground); }
                </style>
            </head>
            <body>
                <h2>${title}</h2>
                <pre><code>${json}</code></pre>
            </body>
            </html>`;
    }
}
