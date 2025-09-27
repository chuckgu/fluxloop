import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

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
        if (!vscode.workspace.workspaceFolders) {
            return Promise.resolve([]);
        }

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
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];

        if (!workspaceFolder) {
            return experiments;
        }

        // Check for fluxloop.yaml
        const configPath = path.join(workspaceFolder.uri.fsPath, 'fluxloop.yaml');
        if (fs.existsSync(configPath)) {
            experiments.push(new ExperimentItem(
                'Current Experiment',
                'fluxloop.yaml',
                vscode.TreeItemCollapsibleState.Collapsed,
                'experiment',
                configPath
            ));
        }

        // Check experiments directory
        const experimentsDir = path.join(workspaceFolder.uri.fsPath, 'experiments');
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
            details.push(new ExperimentItem(
                'Configuration',
                element.resourcePath || '',
                vscode.TreeItemCollapsibleState.None,
                'file'
            ));
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
                        filePath
                    ));
                }
            }
        }

        return details;
    }
}

class ExperimentItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'experiment' | 'result' | 'file' | 'run' | 'info',
        public readonly resourcePath?: string
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
