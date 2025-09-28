import * as vscode from 'vscode';
import * as which from 'which';

export class StatusProvider implements vscode.TreeDataProvider<StatusItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<StatusItem | undefined | null | void> = new vscode.EventEmitter<StatusItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<StatusItem | undefined | null | void> = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: StatusItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: StatusItem): Promise<StatusItem[]> {
        const items: StatusItem[] = [];

        // Check CLI installation
        try {
            const cliPath = await which('fluxloop');
            items.push(new StatusItem(
                'CLI',
                'Installed',
                'success',
                cliPath
            ));
        } catch {
            items.push(new StatusItem(
                'CLI',
                'Not installed',
                'error',
                'Run: pip install fluxloop-cli'
            ));
        }

        // Check SDK installation
        try {
            // This is a simplified check
            items.push(new StatusItem(
                'SDK',
                'Check in terminal',
                'warning',
                'Run: pip show fluxloop-sdk'
            ));
        } catch {
            items.push(new StatusItem(
                'SDK',
                'Unknown',
                'warning'
            ));
        }

        // Check collector connection
        const config = vscode.workspace.getConfiguration('fluxloop');
        const collectorUrl = config.get<string>('collectorUrl');
        items.push(new StatusItem(
            'Collector',
            collectorUrl || 'Not configured',
            'info'
        ));

        // Check configuration
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            const configUri = vscode.Uri.joinPath(workspaceFolder.uri, 'setting.yaml');
            try {
                await vscode.workspace.fs.stat(configUri);
                items.push(new StatusItem(
                    'Config',
                    'setting.yaml found',
                    'success'
                ));
            } catch {
                items.push(new StatusItem(
                    'Config',
                    'No setting.yaml',
                    'warning',
                    'Run: FluxLoop: Initialize Project'
                ));
            }
        }

        return items;
    }
}

class StatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly status: 'success' | 'error' | 'warning' | 'info',
        public readonly detail?: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        
        this.description = description;
        this.tooltip = detail || description;

        // Set icon based on status
        switch (status) {
            case 'success':
                this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
                break;
            case 'error':
                this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('testing.iconFailed'));
                break;
            case 'warning':
                this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('testing.iconQueued'));
                break;
            case 'info':
                this.iconPath = new vscode.ThemeIcon('info');
                break;
        }
    }
}
