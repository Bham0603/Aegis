import * as vscode from 'vscode';

const SECRET_KEY = 'aegis_api_key';

export class SecretManager {
    private static secrets: vscode.SecretStorage;

    static init(context: vscode.ExtensionContext) {
        this.secrets = context.secrets;
    }

    static async getApiKey(): Promise<string | undefined> {
        return await this.secrets.get(SECRET_KEY);
    }

    static async setApiKey(key: string): Promise<void> {
        await this.secrets.store(SECRET_KEY, key);
    }

    static async deleteApiKey(): Promise<void> {
        await this.secrets.delete(SECRET_KEY);
    }
}
