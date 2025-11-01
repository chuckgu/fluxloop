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
            return Promise.resolve(this.getExperimentDetails(element));
        }

        return Promise.resolve(this.getRootItems());
    }

    private getRootItems(): ExperimentItem[] {
        const items: ExperimentItem[] = [];
        const workspacePath = ProjectContext.getActiveWorkspacePath();

        if (!workspacePath) {
            items.push(new ExperimentItem(
                'Select a project to view experiments',
                '',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return items;
        }

        const configInfo = this.resolveSimulationConfig(workspacePath);
        if (configInfo) {
            items.push(new ExperimentItem(
                'Current Experiment',
                configInfo.label,
                vscode.TreeItemCollapsibleState.Collapsed,
                'experiment',
                configInfo.path
            ));
        } else {
            items.push(new ExperimentItem(
                'No simulation configuration found',
                'Create configs/simulation.yaml to configure experiments',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
        }

        items.push(new ExperimentItem(
            'Recording Mode',
            'Enable, disable, or check recording status',
            vscode.TreeItemCollapsibleState.Collapsed,
            'recordingGroup'
        ));

        items.push(...this.getExperimentResults(workspacePath));
        items.push(...this.getRecordingItems(workspacePath));

        return items;
    }

    private getExperimentDetails(element: ExperimentItem): ExperimentItem[] {
        const details: ExperimentItem[] = [];

        if (element.type === 'recordingGroup') {
            return [
                new ExperimentItem(
                    'Enable Recording Mode',
                    'fluxloop record enable',
                    vscode.TreeItemCollapsibleState.None,
                    'command',
                    undefined,
                    'fluxloop.enableRecording'
                ),
                new ExperimentItem(
                    'Disable Recording Mode',
                    'fluxloop record disable',
                    vscode.TreeItemCollapsibleState.None,
                    'command',
                    undefined,
                    'fluxloop.disableRecording'
                ),
                new ExperimentItem(
                    'Show Recording Status',
                    'fluxloop record status',
                    vscode.TreeItemCollapsibleState.None,
                    'command',
                    undefined,
                    'fluxloop.showRecordingStatus'
                )
            ];
        }

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

                const recordings = this.getRecordingItems(element.resourcePath);
                details.push(...recordings);
        }

        return details;
    }

    private getExperimentResults(projectPath: string): ExperimentItem[] {
        const experiments: ExperimentItem[] = [];
        const experimentsDir = path.join(projectPath, 'experiments');
        if (!fs.existsSync(experimentsDir)) {
            experiments.push(new ExperimentItem(
                'No experiments found',
                'Run "FluxLoop: Run Experiment" to get started',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return experiments;
        }

        const dirs = fs.readdirSync(experimentsDir)
            .filter(file => fs.statSync(path.join(experimentsDir, file)).isDirectory())
            .sort((a, b) => b.localeCompare(a))
            .slice(0, 10);

        for (const dir of dirs) {
            const experimentPath = path.join(experimentsDir, dir);
            const summaryPath = path.join(experimentPath, 'summary.json');
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
                experimentPath
            ));
        }

        if (experiments.length === 0) {
            experiments.push(new ExperimentItem(
                'No experiments found',
                'Run "FluxLoop: Run Experiment" to get started',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
        }

        return experiments;
    }

    private getRecordingItems(basePath: string): ExperimentItem[] {
        const recordings: ExperimentItem[] = [];

        const recordingsDir = path.join(basePath, 'recordings');
        if (!fs.existsSync(recordingsDir)) {
            // Try project-level recordings directory
            if (basePath === ProjectContext.getActiveWorkspacePath()) {
                const projectLevelDir = path.join(basePath, 'recordings');
                if (!fs.existsSync(projectLevelDir)) {
                    recordings.push(new ExperimentItem(
                        'No recordings found',
                        'Enable Record Mode to capture inputs',
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    ));
                    return recordings;
                }
            } else {
                return recordings;
            }
        }

        const dir = fs.existsSync(recordingsDir) ? recordingsDir : path.join(basePath, 'recordings');
        if (!fs.existsSync(dir)) {
            recordings.push(new ExperimentItem(
                'No recordings found',
                'Enable Record Mode to capture inputs',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return recordings;
        }

        const files = fs.readdirSync(dir)
            .filter(file => fs.statSync(path.join(dir, file)).isFile())
            .sort((a, b) => b.localeCompare(a))
            .slice(0, 10);

        if (files.length === 0) {
            recordings.push(new ExperimentItem(
                'No recordings found',
                'Enable Record Mode to capture inputs',
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return recordings;
        }

        if (basePath === ProjectContext.getActiveWorkspacePath()) {
            recordings.push(new ExperimentItem(
                'Recordings',
                dir,
                vscode.TreeItemCollapsibleState.Collapsed,
                'recordings',
                dir
            ));
        } else {
            for (const file of files) {
                const filePath = path.join(dir, file);
                recordings.push(new ExperimentItem(
                    file,
                    '',
                    vscode.TreeItemCollapsibleState.None,
                    'file',
                    filePath,
                    filePath
                ));
            }
        }

        return recordings;
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
        public readonly type: 'experiment' | 'result' | 'file' | 'run' | 'info' | 'command' | 'recordings' | 'recordingGroup',
        public readonly resourcePath?: string,
        private readonly commandId?: string
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
                this.iconPath = new vscode.ThemeIcon('debug-start');
                this.command = {
                    command: 'fluxloop.runExperiment',
                    title: 'Run Experiment'
                };
                break;
            case 'command':
                this.iconPath = new vscode.ThemeIcon('debug-start');
                if (commandId) {
                    this.command = {
                        command: commandId,
                        title: label
                    };
                }
                break;
            case 'recordings':
                this.iconPath = new vscode.ThemeIcon('record');
                break;
            case 'recordingGroup':
                this.iconPath = new vscode.ThemeIcon('record');
                break;
            case 'info':
                this.iconPath = new vscode.ThemeIcon('info');
                break;
        }
    }
}
