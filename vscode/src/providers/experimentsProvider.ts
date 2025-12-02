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
                undefined,
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return items;
        }

        const configInfo = this.resolveSimulationConfig(workspacePath);
        if (configInfo) {
            items.push(new ExperimentItem(
                'Configuration',
                undefined,
                vscode.TreeItemCollapsibleState.Collapsed,
                'experiment',
                configInfo.path
            ));
            items.push(new ExperimentItem(
                'Prepare Simulation',
                'Flux Agent context gathering (recommended)',
                vscode.TreeItemCollapsibleState.None,
                'command',
                undefined,
                'fluxloop.integration.runAgent',
                'debug-start',
                [{ useDefaultContext: true }]
            ));
            items.push(new ExperimentItem(
                'Simulation Guide',
                'Checklist before running experiments',
                vscode.TreeItemCollapsibleState.None,
                'command',
                undefined,
                'fluxloop.integration.showPlaygroundGuide',
                'book'
            ));
            items.push(new ExperimentItem(
                'Run Experiment',
                undefined,
                vscode.TreeItemCollapsibleState.None,
                'command',
                undefined,
                'fluxloop.runExperiment'
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
            'Experiments',
            undefined,
            vscode.TreeItemCollapsibleState.Collapsed,
            'experimentsGroup',
            workspacePath
        ));

        return items;
    }

    private getExperimentDetails(element: ExperimentItem): ExperimentItem[] {
        const details: ExperimentItem[] = [];

        if (element.type === 'experimentsGroup' && element.resourcePath) {
            return this.getExperimentResults(element.resourcePath);
        }

        if (element.type === 'recordings' && element.resourcePath) {
            const entries: ExperimentItem[] = [];

            try {
                const files = fs.readdirSync(element.resourcePath)
                    .filter(file => fs.statSync(path.join(element.resourcePath!, file)).isFile())
                    .sort((a, b) => b.localeCompare(a))
                    .slice(0, 20);

                if (files.length === 0) {
                    entries.push(new ExperimentItem(
                        'No recordings found',
                        'Enable Record Mode to capture inputs',
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    ));
                } else {
                    for (const file of files) {
                        const filePath = path.join(element.resourcePath, file);
                        entries.push(new ExperimentItem(
                            file,
                            '',
                            vscode.TreeItemCollapsibleState.None,
                            'file',
                            filePath,
                            filePath
                        ));
                    }
                }
            } catch (error) {
                console.warn('Failed to read recordings directory', error);
                entries.push(new ExperimentItem(
                    'Failed to load recordings',
                    'Check recordings directory permissions',
                    vscode.TreeItemCollapsibleState.None,
                    'info'
                ));
            }

            return entries;
        }

        if (element.type === 'experiment') {
            const workspacePath = ProjectContext.getActiveWorkspacePath();
            // Show config details
            if (element.resourcePath) {
                const configLabel = workspacePath
                    ? path.relative(workspacePath, element.resourcePath)
                    : path.basename(element.resourcePath);

                details.push(new ExperimentItem(
                    'Open configuration',
                    configLabel,
                    vscode.TreeItemCollapsibleState.None,
                    'file',
                    element.resourcePath,
                    undefined,
                    'settings-gear'
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

            if (workspacePath) {
                details.push(new ExperimentItem(
                    'Recording (Advanced)',
                    'Recording mode controls and files',
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'recordingAdvanced',
                    workspacePath
                ));
            }
        } else if (element.type === 'recordingAdvanced') {
            const workspacePath = element.resourcePath ?? ProjectContext.getActiveWorkspacePath();
            const recordingItems: ExperimentItem[] = [];

            recordingItems.push(
                new ExperimentItem(
                    'Enable Recording',
                    'fluxloop record enable',
                    vscode.TreeItemCollapsibleState.None,
                    'command',
                    undefined,
                    'fluxloop.enableRecording'
                ),
            );

            recordingItems.push(
                new ExperimentItem(
                    'Disable Recording',
                    'fluxloop record disable',
                    vscode.TreeItemCollapsibleState.None,
                    'command',
                    undefined,
                    'fluxloop.disableRecording'
                ),
            );

            if (workspacePath) {
                const filesItems = this.getRecordingItems(workspacePath, {
                    rootLabel: 'Recording files',
                    emptyLabel: 'No recordings found',
                    emptyDescription: 'Enable Record Mode to capture inputs'
                });
                recordingItems.push(...filesItems);
            } else {
                recordingItems.push(new ExperimentItem(
                    'Recording files unavailable',
                    'Open a FluxLoop project to view recordings',
                    vscode.TreeItemCollapsibleState.None,
                    'info'
                ));
            }

            return recordingItems;
        } else if (element.type === 'result' && element.resourcePath) {
            // Show result files
            const files = ['summary.json', 'trace_summary.jsonl', 'traces.jsonl', 'observations.jsonl', 'errors.json', 'logs.json'];
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
            const timestampLabel = this.extractTimestampFromExperimentName(dir);
            let description = '';

            if (fs.existsSync(summaryPath)) {
                try {
                    const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
                    label = summary.name || dir;
                    const successRate = summary.results?.success_rate;
                    const successLabel = typeof successRate === 'number'
                        ? `${this.formatPercentage(successRate)} success`
                        : '';
                    const descriptionParts = [];
                    if (timestampLabel) {
                        descriptionParts.push(timestampLabel);
                    }
                    if (successLabel) {
                        descriptionParts.push(successLabel);
                    }
                    description = descriptionParts.join(' • ');
                } catch {
                    // Ignore parse errors
                }
            }

            if (!description && timestampLabel) {
                description = timestampLabel;
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

    private getRecordingItems(
        basePath: string,
        options?: { rootLabel?: string; emptyLabel?: string; emptyDescription?: string }
    ): ExperimentItem[] {
        const recordings: ExperimentItem[] = [];
        const noRecordingsLabel = options?.emptyLabel ?? 'No recordings found';
        const noRecordingsDescription = options?.emptyDescription ?? 'Enable Record Mode to capture inputs';

        const recordingsDir = path.join(basePath, 'recordings');
        if (!fs.existsSync(recordingsDir)) {
            // Try project-level recordings directory
            if (basePath === ProjectContext.getActiveWorkspacePath()) {
                const projectLevelDir = path.join(basePath, 'recordings');
                if (!fs.existsSync(projectLevelDir)) {
                    recordings.push(new ExperimentItem(
                        noRecordingsLabel,
                        noRecordingsDescription,
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
                noRecordingsLabel,
                noRecordingsDescription,
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
                noRecordingsLabel,
                noRecordingsDescription,
                vscode.TreeItemCollapsibleState.None,
                'info'
            ));
            return recordings;
        }

        if (basePath === ProjectContext.getActiveWorkspacePath()) {
            recordings.push(new ExperimentItem(
                options?.rootLabel ?? 'Recordings',
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

    private extractTimestampFromExperimentName(name: string): string | undefined {
        const match = name.match(/_(\d{8})_(\d{6})$/);
        if (!match) {
            return undefined;
        }

        const [, datePart, timePart] = match;
        const year = datePart.substring(0, 4);
        const month = datePart.substring(4, 6);
        const day = datePart.substring(6, 8);
        const hours = timePart.substring(0, 2);
        const minutes = timePart.substring(2, 4);
        const seconds = timePart.substring(4, 6);

        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }

    private formatPercentage(value: number): string {
        const percentage = value * 100;
        const formatted = Number.isInteger(percentage) ? percentage.toFixed(0) : percentage.toFixed(1);
        return `${formatted}%`;
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
        public label: string,
        description: string | undefined,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'experiment' | 'experimentsGroup' | 'result' | 'file' | 'info' | 'command' | 'recordings' | 'recordingGroup' | 'recordingAdvanced',
        public readonly resourcePath?: string,
        private readonly commandId?: string,
        private readonly iconId?: string,
        private readonly commandArgs?: unknown[]
    ) {
        super(label, collapsibleState);

        this.tooltip = this.label;
        if (description !== undefined) {
        this.description = description;
        }

        // Set icon based on type
        switch (type) {
            case 'experiment':
                this.iconPath = new vscode.ThemeIcon('settings-gear');
                break;
            case 'experimentsGroup':
                this.iconPath = new vscode.ThemeIcon('folder');
                break;
            case 'recordingAdvanced':
                this.iconPath = new vscode.ThemeIcon('folder');
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
            case 'command':
                this.iconPath = new vscode.ThemeIcon('debug-start');
                if (commandId) {
                    this.command = {
                        command: commandId,
                        title: label,
                        arguments: commandArgs
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

        if (this.iconId) {
            this.iconPath = new vscode.ThemeIcon(this.iconId);
        }
    }
}
