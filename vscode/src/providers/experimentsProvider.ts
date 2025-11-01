import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { parse as parseYaml } from 'yaml';
import { ProjectContext } from '../project/projectContext';

export class ExperimentsProvider implements vscode.TreeDataProvider<ExperimentItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ExperimentItem | undefined | null | void> = new vscode.EventEmitter<ExperimentItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ExperimentItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private workspaceState: vscode.Memento) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ExperimentItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ExperimentItem): Thenable<ExperimentItem[]> {
        if (element) {
            // Show experiment details
            return Promise.resolve(this.getExperimentDetails(element));
        } else {
            // Show list of experiments
            return Promise.resolve(this.getExperiments());
        }
    }

    private getExperiments(): ExperimentItem[] {
        const experiments: ExperimentItem[] = [];
        const workspacePath = ProjectContext.getActiveWorkspacePath();

        if (!workspacePath) {
            experiments.push(new ExperimentItem(
                'Select a project to view experiments',
                '',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return experiments;
        }

        const configInfo = this.resolveSimulationConfig(workspacePath);
        if (configInfo) {
            experiments.push(new ExperimentItem(
                'Current Experiment',
                configInfo.label,
                vscode.TreeItemCollapsibleState.Collapsed,
                'experiment',
                configInfo.path
            ));
        } else {
            experiments.push(new ExperimentItem(
                'No simulation configuration found',
                'Create configs/simulation.yaml to configure experiments',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
        }

        // Check experiments directory
        const experimentsDir = path.join(workspacePath, 'experiments');
        if (fs.existsSync(experimentsDir)) {
            const dirs = fs.readdirSync(experimentsDir)
                .filter(file => fs.statSync(path.join(experimentsDir, file)).isDirectory())
                .sort((a, b) => b.localeCompare(a)) // Sort by date (newest first)
                .slice(0, 10); // Show last 10

            for (const dir of dirs) {
                const summaryPath = path.join(experimentsDir, dir, 'summary.json');
                let label = dir;
                let description = '';

                if (fs.existsSync(summaryPath)) {
                    try {
                        const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
                        label = summary.name || dir;
                        description = `${summary.results?.success_rate ? (summary.results.success_rate * 100).toFixed(1) : 0}% success`;
                    } catch {
                        // Ignore parse errors
                    }
                }

                experiments.push(new ExperimentItem(
                    label,
                    description,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'result',
                    path.join(experimentsDir, dir)
                ));
            }
        }

        if (experiments.length === 0) {
            experiments.push(new ExperimentItem(
                'No experiments found',
                'Run "FluxLoop: Initialize Project" to get started',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
        }

        return experiments;
    }

    private getExperimentDetails(element: ExperimentItem): ExperimentItem[] {
        const details: ExperimentItem[] = [];

        if (element.type === 'experiment') {
            // Show config details
            if (element.resourcePath) {
                const workspacePath = ProjectContext.getActiveWorkspacePath();
                const configLabel = workspacePath
                    ? path.relative(workspacePath, element.resourcePath)
                    : path.basename(element.resourcePath);

                details.push(new ExperimentItem(
                    'Open configuration',
                    configLabel,
                    vscode.TreeItemCollapsibleState.None,
                    'file',
                    element.resourcePath,
                    element.resourcePath
                ));

                const configData = this.readSimulationConfig(element.resourcePath);
                if (configData) {
                    if (configData.runner?.module_path) {
                        details.push(new ExperimentItem(
                            `Runner: ${configData.runner.module_path}`,
                            configData.runner.function_name ? `Function: ${configData.runner.function_name}` : '',
                            vscode.TreeItemCollapsibleState.None,
                            'info'
                        ));
                    }

                    if (typeof configData.iterations === 'number') {
                        details.push(new ExperimentItem(
                            `Iterations: ${configData.iterations}`,
                            '',
                            vscode.TreeItemCollapsibleState.None,
                            'info'
                        ));
                    }

                    const recordStatus = this.getRecordModeStatus(element.resourcePath, configData);
                    details.push(new ExperimentItem(
                        recordStatus.label,
                        recordStatus.description,
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    ));
                }
            }
            details.push(new ExperimentItem(
                'Run Experiment',
                '',
                vscode.TreeItemCollapsibleState.None,
                'run'
            ));
        } else if (element.type === 'result' && element.resourcePath) {
            // Show result files
            const files = ['summary.json', 'traces.jsonl', 'errors.json'];
            for (const file of files) {
                const filePath = path.join(element.resourcePath, file);
                if (fs.existsSync(filePath)) {
                    details.push(new ExperimentItem(
                        file,
                        '',
                        vscode.TreeItemCollapsibleState.None,
                        'file',
                        filePath,
                        filePath
                    ));
                }
            }
        }

        return details;
    }

    private resolveSimulationConfig(projectPath: string): { path: string; label: string } | undefined {
        const modernPath = path.join(projectPath, 'configs', 'simulation.yaml');
        if (fs.existsSync(modernPath)) {
            return { path: modernPath, label: 'configs/simulation.yaml' };
        }

        return undefined;
    }

    private readSimulationConfig(configPath: string): any {
        try {
            const raw = fs.readFileSync(configPath, 'utf8');
            return parseYaml(raw) ?? {};
        } catch (error) {
            console.warn(`Failed to read simulation config: ${configPath}`, error);
            return undefined;
        }
    }

    private getRecordModeStatus(configPath: string, config: any): { label: string; description: string } {
        const projectPath = this.resolveProjectPathFromConfig(configPath);
        const envRecord = this.readEnvRecordFlag(path.join(projectPath, '.env'));
        const configRecord = Boolean(config?.replay_args?.enabled);
        const recordingFile = config?.replay_args?.recording_file || 'recordings/args_recording.jsonl';

        const enabled = envRecord ?? configRecord;
        if (enabled) {
            return {
                label: 'Record Mode: Enabled',
                description: `Recording to ${recordingFile}`
            };
        }

        return {
            label: 'Record Mode: Disabled',
            description: 'Toggle via CLI (fluxloop record enable) or VSCode command when available'
        };
    }

    private resolveProjectPathFromConfig(configPath: string): string {
        const normalized = path.resolve(configPath);
        const configsSegment = `${path.sep}configs${path.sep}`;
        const index = normalized.lastIndexOf(configsSegment);
        if (index !== -1) {
            return normalized.substring(0, index);
        }
        return path.dirname(normalized);
    }

    private readEnvRecordFlag(envPath: string): boolean | undefined {
        if (!fs.existsSync(envPath)) {
            return undefined;
        }

        try {
            const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) {
                    continue;
                }

                const [key, value] = trimmed.split('=', 2);
                if (key === 'FLUXLOOP_RECORD_ARGS') {
                    return value.toLowerCase() === 'true';
                }
            }
        } catch (error) {
            console.warn('Failed to read .env for record mode status', error);
        }

        return undefined;
    }
}

class ExperimentItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'experiment' | 'result' | 'file' | 'run' | 'info',
        public readonly resourcePath?: string,
        private readonly openPath?: string
    ) {
        super(label, collapsibleState);

        this.tooltip = this.label;
        this.description = description;

        // Set icon based on type
        switch (type) {
            case 'experiment':
                this.iconPath = new vscode.ThemeIcon('beaker');
                break;
            case 'result':
                this.iconPath = new vscode.ThemeIcon('graph');
                break;
            case 'file':
                this.iconPath = new vscode.ThemeIcon('file');
                if (resourcePath) {
                    this.command = {
                        command: 'vscode.open',
                        title: 'Open File',
                        arguments: [vscode.Uri.file(resourcePath)]
                    };
                }
                break;
            case 'run':
                this.iconPath = new vscode.ThemeIcon('run');
                this.command = {
                    command: 'fluxloop.runExperiment',
                    title: 'Run Experiment'
                };
                break;
            case 'info':
                this.iconPath = new vscode.ThemeIcon('info');
                break;
        }
    }
}
