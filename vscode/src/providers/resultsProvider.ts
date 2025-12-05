import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { ProjectContext } from '../project/projectContext';

export class ResultsProvider implements vscode.TreeDataProvider<ResultItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ResultItem | undefined | null | void> = new vscode.EventEmitter<ResultItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ResultItem | undefined | null | void> = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ResultItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ResultItem): Thenable<ResultItem[]> {
        const projectPath = ProjectContext.getActiveWorkspacePath();

        if (!projectPath) {
            return Promise.resolve([new ResultItem(
                'No project selected',
                'Select a project to view results',
                vscode.TreeItemCollapsibleState.None,
                'info'
            )]);
        }

        if (!element) {
            const experimentsDir = path.join(projectPath, 'experiments');
            const configureItem = new ResultItem(
                'Configure Evaluation…',
                'Open configs/evaluation.yaml',
                vscode.TreeItemCollapsibleState.None,
                'command',
                undefined,
                {
                    command: 'fluxloop.openEvaluationConfig',
                    title: 'Configure Evaluation'
                }
            );

            if (!fs.existsSync(experimentsDir)) {
                return Promise.resolve([
                    configureItem,
                    new ResultItem(
                        'No experiment results yet',
                        'Run FluxLoop: Run Experiment to generate outputs',
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    )
                ]);
            }

            const directories = fs.readdirSync(experimentsDir)
                .map(name => ({ name, fullPath: path.join(experimentsDir, name) }))
                .filter(entry => {
                    try {
                        return fs.statSync(entry.fullPath).isDirectory();
                    } catch {
                        return false;
                    }
                })
                .sort((a, b) => b.name.localeCompare(a.name))
                .slice(0, 15);

            if (directories.length === 0) {
                return Promise.resolve([
                    configureItem,
                    new ResultItem(
                        'No experiment results yet',
                        'Run FluxLoop: Run Experiment to generate outputs',
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    )
                ]);
            }

            const items = directories.map(entry => {
                const summary = this.readSummary(path.join(entry.fullPath, 'summary.json'));
                const label = summary?.name || entry.name;
                const timestampLabel = this.extractTimestampFromExperimentName(entry.name);
                const description = this.buildResultDescription(summary, entry.fullPath, timestampLabel);
                return new ResultItem(
                    label,
                    description,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'folder',
                    entry.fullPath
                );
            });

            return Promise.resolve([configureItem, ...items]);
        }

        if (element.type === 'folder' && element.resourcePath) {
            const files = ['summary.json', 'trace_summary.jsonl', 'traces.jsonl', 'observations.jsonl', 'errors.json', 'logs.json'];
            const items: ResultItem[] = [];

            items.push(new ResultItem(
                'Parse Results',
                'fluxloop parse experiment',
                vscode.TreeItemCollapsibleState.None,
                'action',
                element.resourcePath,
                {
                    command: 'fluxloop.parseExperiment',
                    title: 'Parse Experiment Results',
                    arguments: [element.resourcePath]
                }
            ));

            items.push(new ResultItem(
                'Evaluate Results',
                'fluxloop evaluate experiment',
                vscode.TreeItemCollapsibleState.None,
                'action',
                element.resourcePath,
                {
                    command: 'fluxloop.evaluateExperiment',
                    title: 'Evaluate Experiment Results',
                    arguments: [element.resourcePath]
                }
            ));

            const analysisDir = path.join(element.resourcePath, 'per_trace_analysis');
            if (fs.existsSync(analysisDir) && fs.statSync(analysisDir).isDirectory()) {
                items.push(new ResultItem(
                    'per_trace_analysis',
                    '',
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'analysis',
                    analysisDir
                ));
            }

            const evaluationDir = path.join(element.resourcePath, 'evaluation');
            if (fs.existsSync(evaluationDir) && fs.statSync(evaluationDir).isDirectory()) {
                items.push(new ResultItem(
                    'evaluation',
                    '',
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'analysis',
                    evaluationDir
                ));
            }

            for (const file of files) {
                const fullPath = path.join(element.resourcePath, file);
                if (fs.existsSync(fullPath)) {
                    items.push(new ResultItem(
                        file,
                        '',
                        vscode.TreeItemCollapsibleState.None,
                        'file',
                        fullPath
                    ));
                }
            }

            return Promise.resolve(items);
        }

        if (element.type === 'analysis' && element.resourcePath) {
            try {
                const entries = fs.readdirSync(element.resourcePath)
                    .sort((a, b) => a.localeCompare(b));
                const items = entries.map(entry => {
                    const entryPath = path.join(element.resourcePath!, entry);
                    const isDir = fs.statSync(entryPath).isDirectory();
                    if (isDir) {
                        return new ResultItem(
                            entry,
                            '',
                            vscode.TreeItemCollapsibleState.Collapsed,
                            'analysis',
                            entryPath
                        );
                    }

                    return new ResultItem(
                        entry,
                        '',
                        vscode.TreeItemCollapsibleState.None,
                        'file',
                        entryPath
                    );
                });
                return Promise.resolve(items);
            } catch (error) {
                console.warn('Failed to read analysis directory', error);
                return Promise.resolve([
                    new ResultItem(
                        'Failed to load analysis outputs',
                        'Unable to access directory contents.',
                        vscode.TreeItemCollapsibleState.None,
                        'info'
                    )
                ]);
            }
        }

        return Promise.resolve([]);
    }

    private readSummary(summaryPath: string): Record<string, any> | undefined {
        if (!fs.existsSync(summaryPath)) {
            return undefined;
        }

        try {
            const raw = fs.readFileSync(summaryPath, 'utf8');
            return JSON.parse(raw);
        } catch (error) {
            console.warn(`Failed to read summary: ${summaryPath}`, error);
            return undefined;
        }
    }

    private buildResultDescription(summary: Record<string, any> | undefined, experimentDir: string, timestampLabel?: string): string {
        if (!summary) {
            return timestampLabel ? `${timestampLabel} · ${path.basename(experimentDir)}` : path.basename(experimentDir);
        }

        const runs = summary.total_runs ?? summary.results?.total_runs;
        const successRate = summary.results?.success_rate ?? summary.success_rate;
        const formattedRate = typeof successRate === 'number' ? `${(successRate * 100).toFixed(1)}% success` : undefined;

        const parts: string[] = [];
        if (timestampLabel) {
            parts.push(timestampLabel);
        }
        if (runs !== undefined) {
            parts.push(`${runs} runs`);
        }
        if (formattedRate) {
            parts.push(formattedRate);
        }

        return parts.join(' · ') || 'Experiment results';
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
}

class ResultItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'folder' | 'file' | 'info' | 'command' | 'action' | 'analysis',
        public readonly resourcePath?: string,
        command?: vscode.Command
    ) {
        super(label, collapsibleState);
        this.tooltip = this.label;
        this.description = description;
        switch (type) {
            case 'folder':
                this.iconPath = vscode.ThemeIcon.Folder;
                break;
            case 'file':
                this.iconPath = vscode.ThemeIcon.File;
                if (resourcePath) {
                    if (resourcePath.toLowerCase().endsWith('.html')) {
                        this.command = {
                            command: 'fluxloop.openInBrowser',
                            title: 'Open in Browser',
                            arguments: [vscode.Uri.file(resourcePath)]
                        };
                    } else {
                        this.command = {
                            command: 'vscode.open',
                            title: 'Open Result File',
                            arguments: [vscode.Uri.file(resourcePath)]
                        };
                    }
                }
                break;
            case 'command':
                this.iconPath = new vscode.ThemeIcon('settings-gear');
                if (command) {
                    this.command = command;
                }
                break;
            case 'action':
                this.iconPath = new vscode.ThemeIcon('debug-start');
                if (command) {
                    this.command = command;
                }
                break;
            case 'analysis':
                this.iconPath = vscode.ThemeIcon.Folder;
                break;
            case 'info':
            default:
                this.iconPath = new vscode.ThemeIcon('info');
                break;
        }
    }
}
