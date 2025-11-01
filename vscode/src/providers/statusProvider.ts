import * as vscode from 'vscode';
import * as which from 'which';
import { spawnSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { parse as parseYaml } from 'yaml';
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
            const configStatus = this.evaluateConfigStatus(workspacePath);
            items.push(new StatusItem(
                'Config',
                configStatus.message,
                configStatus.status,
                configStatus.detail
            ));

            const recordStatus = this.evaluateRecordStatus(workspacePath);
            items.push(new StatusItem(
                'Record Mode',
                recordStatus.message,
                recordStatus.status,
                recordStatus.detail
            ));
        } else {
            items.push(new StatusItem(
                'Config',
                'No project selected',
                'info',
                'Select a project from the FluxLoop panel'
            ));
            items.push(new StatusItem(
                'Record Mode',
                'No project selected',
                'info'
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

    private evaluateConfigStatus(projectPath: string): { status: StatusLevel; message: string; detail?: string } {
        const configDir = path.join(projectPath, 'configs');
        const requiredFiles = ['project.yaml', 'input.yaml', 'simulation.yaml'];
        const optionalFiles = ['evaluation.yaml'];

        if (fs.existsSync(configDir) && fs.statSync(configDir).isDirectory()) {
            const missing = requiredFiles.filter(file => !fs.existsSync(path.join(configDir, file)));
            const detailLines = requiredFiles.map(file => `${missing.includes(file) ? '✗' : '✓'} ${file}`);

            for (const optional of optionalFiles) {
                detailLines.push(`${fs.existsSync(path.join(configDir, optional)) ? '✓' : '○'} ${optional} (optional)`);
            }

            if (missing.length === 0) {
                return {
                    status: 'success',
                    message: 'configs/ structure ready',
                    detail: detailLines.join('\n')
                };
            }

            return {
                status: 'warning',
                message: 'configs/ incomplete',
                detail: `Missing: ${missing.join(', ')}`
            };
        }

        return {
            status: 'warning',
            message: 'No configuration found',
            detail: 'Run FluxLoop: Create Project to scaffold configs/'
        };
    }

    private evaluateRecordStatus(projectPath: string): { status: StatusLevel; message: string; detail?: string } {
        const envValues = this.readEnvFile(path.join(projectPath, '.env'));
        const envRecord = envValues?.FLUXLOOP_RECORD_ARGS?.toLowerCase() === 'true';
        const envRecordingFile = envValues?.FLUXLOOP_RECORDING_FILE;

        const simulationPath = path.join(projectPath, 'configs', 'simulation.yaml');
        const simulationConfig = this.readSimulationConfig(simulationPath);
        const configRecord = Boolean(simulationConfig?.replay_args?.enabled);
        const configRecordingFile = simulationConfig?.replay_args?.recording_file;

        const enabled = envRecord ?? configRecord;
        const recordingFile = envRecordingFile || configRecordingFile || 'recordings/args_recording.jsonl';

        if (enabled) {
            return {
                status: 'info',
                message: 'Enabled',
                detail: `Recording to ${recordingFile}`
            };
        }

        return {
            status: 'success',
            message: 'Disabled',
            detail: 'Enable via CLI (fluxloop record enable) when needed'
        };
    }

    private readEnvFile(envPath: string): Record<string, string> | undefined {
        if (!fs.existsSync(envPath)) {
            return undefined;
        }

        const result: Record<string, string> = {};
        try {
            const raw = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
            for (const line of raw) {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) {
                    continue;
                }
                const [key, value] = trimmed.split('=', 2);
                result[key.trim()] = value.trim();
            }
            return result;
        } catch (error) {
            console.warn('Failed to parse .env file', error);
            return undefined;
        }
    }

    private readSimulationConfig(simulationPath: string): any {
        if (!fs.existsSync(simulationPath)) {
            return undefined;
        }

        try {
            const raw = fs.readFileSync(simulationPath, 'utf8');
            return parseYaml(raw) ?? {};
        } catch (error) {
            console.warn('Failed to read simulation config for status provider', error);
            return undefined;
        }
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
