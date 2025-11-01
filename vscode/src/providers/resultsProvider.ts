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
                const description = this.buildResultDescription(summary, entry.fullPath);
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
            const files = ['summary.json', 'traces.jsonl', 'observations.jsonl', 'errors.json', 'logs.json'];
            const items: ResultItem[] = [];

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

    private buildResultDescription(summary: Record<string, any> | undefined, experimentDir: string): string {
        if (!summary) {
            return path.basename(experimentDir);
        }

        const runs = summary.total_runs ?? summary.results?.total_runs;
        const successRate = summary.results?.success_rate ?? summary.success_rate;
        const formattedRate = typeof successRate === 'number' ? `${(successRate * 100).toFixed(1)}% success` : undefined;

        const parts: string[] = [];
        if (runs !== undefined) {
            parts.push(`${runs} runs`);
        }
        if (formattedRate) {
            parts.push(formattedRate);
        }

        return parts.join(' · ') || 'Experiment results';
    }
}

class ResultItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'folder' | 'file' | 'info' | 'command',
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
                    this.command = {
                        command: 'vscode.open',
                        title: 'Open Result File',
                        arguments: [vscode.Uri.file(resourcePath)]
                    };
                }
                break;
            case 'command':
                this.iconPath = new vscode.ThemeIcon('settings-gear');
                if (command) {
                    this.command = command;
                }
                break;
            case 'info':
            default:
                this.iconPath = new vscode.ThemeIcon('info');
                break;
        }
    }
}
