# Aegis Security Console - VS Code Extension

The Aegis VS Code Extension brings the power of the Aegis Runtime Security & Governance platform directly into the developer's IDE. It provides immediate visibility into security policies, active threats, and pending approvals, allowing developers to manage agent security posture without context switching.

## Architecture & Security Model

- **Client Only:** The extension is purely a presentation client. It evaluates zero policies, holds no root trust, and makes zero security decisions independently.
- **Backend Authority:** All security logic, trust evaluations, risk calculations, and authorization decisions remain strictly on the Aegis backend.
- **Secure Secret Storage:** API keys are stored securely using VS Code's encrypted `SecretStorage` via the `aegis.setApiKey` command. Keys are never logged or stored in plain-text workspace settings.
- **Polling with Deduplication:** Threat notifications are fetched via background polling, deduplicated locally, and presented to the user via VS Code native `showWarningMessage`.

## Key Features

1. **Security Overview (Tree View):**
   - Displays real-time stats for active agents, policies, tools, and recent actions.
2. **Pending Approvals (Tree View):**
   - Lists all `PENDING` actions requiring human-in-the-loop (HITL) authorization.
   - Provides inline commands to immediately **Approve** or **Deny** actions.
3. **Audit Stream (Tree View):**
   - Displays recent agent actions, threats, and policy enforcements.
4. **Action Inspector (Webview):**
   - Securely inspects the JSON payload of specific actions or approvals in a read-only Webview Panel.
5. **Real-time Threat Alerts:**
   - Toast notifications for newly detected threats.

## Commands

- `aegis.setApiKey`: Sets the API key for authenticating with the Aegis backend.
- `aegis.refresh`: Refreshes all tree views and fetches the latest data.
- `aegis.approveAction`: Approves a pending action.
- `aegis.denyAction`: Denies a pending action.
- `aegis.inspectAction`: Opens the Action Inspector Webview.

## Build and Run

To package the extension:
```bash
npm run package
npx @vscode/vsce package
```

This generates a `.vsix` file that can be installed directly in VS Code.
