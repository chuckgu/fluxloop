import * as vscode from 'vscode';
import * as which from 'which';
import { spawnSync } from 'child_process';
import { ProjectContext } from '../project/projectContext';

export class StatusProvider implements vscode.TreeDataProvider<StatusItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<StatusItem | undefined | null | void> = new vscode.EventEmitter<StatusItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<StatusItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private lastEnvironment: string | undefined;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    refreshForEnvironment(environment: string | undefined): void {
        this.lastEnvironment = environment;
        this.refresh();
    }

    getTreeItem(element: StatusItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: StatusItem): Promise<StatusItem[]> {
        const items: StatusItem[] = [];

        // Check CLI installation
        try {
            const cliPath = await which.default('fluxloop');
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
        const sdkStatus = this.checkSdkInstallation();
        items.push(new StatusItem(
            'SDK',
            sdkStatus.description,
            sdkStatus.status,
            sdkStatus.detail
        ));

        // Check collector connection
        const config = vscode.workspace.getConfiguration('fluxloop');
        const collectorUrl = config.get<string>('collectorUrl');
        items.push(new StatusItem(
            'Collector',
            collectorUrl || 'Not configured',
            'info'
        ));

        // Check configuration
        const workspacePath = ProjectContext.getActiveWorkspacePath();
        if (workspacePath) {
            const configUri = vscode.Uri.joinPath(vscode.Uri.file(workspacePath), 'setting.yaml');
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
        } else {
            items.push(new StatusItem(
                'Config',
                'No project selected',
                'info',
                'Select a project from the FluxLoop panel'
            ));
        }

        return items;
    }

    private checkSdkInstallation(): SdkStatusResult {
        if (this.lastEnvironment === 'Docker') {
            return {
                description: 'Verify inside Docker environment',
                status: 'info',
                detail: 'Run fluxloop-sdk install/check inside the selected Docker runtime'
            };
        }

        if (this.lastEnvironment === 'Dev Container') {
            return {
                description: 'Assuming Dev Container runtime',
                status: 'info',
                detail: 'FluxLoop SDK should be available in the Dev Container environment'
            };
        }

        const commands: Array<{ command: string; args: string[]; display: string }> = [
            { command: 'python', args: ['-c', 'import fluxloop'], display: 'python' },
            { command: 'python3', args: ['-c', 'import fluxloop'], display: 'python3' },
            { command: 'py', args: ['-c', 'import fluxloop'], display: 'py' }
        ];

        let attempted = false;

        for (const entry of commands) {
            const result = spawnSync(entry.command, entry.args, { stdio: 'pipe' });

            if (result.error && 'code' in result.error && result.error.code === 'ENOENT') {
                continue;
            }

            attempted = true;

            if (result.status === 0) {
                return {
                    description: 'Installed',
                    status: 'success',
                    detail: `Detected via ${entry.display}`
                };
            }
        }

        if (!attempted) {
            return {
                description: 'Python interpreter not found',
                status: 'warning',
                detail: 'Install Python or set a Python interpreter to verify FluxLoop SDK'
            };
        }

        return {
            description: 'Not installed',
            status: 'warning',
            detail: 'Install FluxLoop SDK: pip install fluxloop-sdk'
        };
    }
}

type StatusLevel = 'success' | 'error' | 'warning' | 'info';

class StatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly status: StatusLevel,
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

interface SdkStatusResult {
    description: string;
    status: StatusLevel;
    detail?: string;
}
