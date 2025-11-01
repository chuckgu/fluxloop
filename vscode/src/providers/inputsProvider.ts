import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { parse as parseYaml } from 'yaml';
import { ProjectContext } from '../project/projectContext';

type InputsTreeItem = CategoryItem | BaseInputItem | FileItem | CommandItem | InfoItem;

export class InputsProvider implements vscode.TreeDataProvider<InputsTreeItem> {
    private readonly _onDidChangeTreeData = new vscode.EventEmitter<InputsTreeItem | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: InputsTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: InputsTreeItem): Promise<InputsTreeItem[]> {
        const projectPath = ProjectContext.getActiveWorkspacePath();

        if (!projectPath) {
            return [new InfoItem('No project selected', 'Select a project to view inputs.')];
        }

        if (!element) {
            return [
                new CommandItem('Generate New Inputs…', 'fluxloop.generateInputs', 'Start generation wizard'),
                new CategoryItem('Base Inputs', 'base'),
                new CategoryItem('Generated Inputs', 'generated'),
                new CategoryItem('Recordings', 'recordings')
            ];
        }

        if (element instanceof CategoryItem) {
            switch (element.category) {
                case 'base':
                    return this.getBaseInputs(projectPath);
                case 'generated':
                    return this.getGeneratedInputs(projectPath);
                case 'recordings':
                    return this.getRecordings(projectPath);
                default:
                    return [];
            }
        }

        return [];
    }

    private async getBaseInputs(projectPath: string): Promise<InputsTreeItem[]> {
        const configPath = this.findConfigFile(projectPath);
        if (!configPath) {
            return [new InfoItem('No configuration found', 'Add setting.yaml to configure base inputs.')];
        }

        try {
            const raw = await fs.promises.readFile(configPath, 'utf8');
            const parsed = parseYaml(raw) as { base_inputs?: Array<{ input?: string; expected_intent?: string }> } | undefined;
            const baseInputs = parsed?.base_inputs;

            if (!Array.isArray(baseInputs) || baseInputs.length === 0) {
                return [new InfoItem('No base inputs defined', 'Add base_inputs to setting.yaml.')];
            }

            return baseInputs.map((entry, index) => {
                const label = entry?.input || `Base Input ${index + 1}`;
                const description = entry?.expected_intent ? `Intent: ${entry.expected_intent}` : undefined;
                return new BaseInputItem(label, description);
            });
        } catch (error) {
            console.error('Failed to parse setting.yaml', error);
            return [new InfoItem('Unable to load base inputs', 'Check setting.yaml for YAML errors.')];
        }
    }

    private async getGeneratedInputs(projectPath: string): Promise<InputsTreeItem[]> {
        const inputsDir = path.join(projectPath, 'inputs');
        if (!fs.existsSync(inputsDir)) {
            return [new InfoItem('No generated inputs yet', 'Run input generation to create files.')];
        }

        const entries = await fs.promises.readdir(inputsDir, { withFileTypes: true });
        const files = entries.filter(entry => entry.isFile());

        if (files.length === 0) {
            return [new InfoItem('No generated inputs yet', 'Run input generation to create files.')];
        }

        return files
            .sort((a, b) => a.name.localeCompare(b.name))
            .map(file => {
                const filePath = path.join(inputsDir, file.name);
                return new FileItem(
                    file.name,
                    vscode.Uri.file(filePath),
                    this.labelForFile(file.name)
                );
            });
    }

    private async getRecordings(projectPath: string): Promise<InputsTreeItem[]> {
        const recordingsDir = path.join(projectPath, 'recordings');
        if (!fs.existsSync(recordingsDir)) {
            return [new InfoItem('No recordings found', 'Use Run Single to capture recordings.')];
        }

        const entries = await fs.promises.readdir(recordingsDir, { withFileTypes: true });
        const files = entries.filter(entry => entry.isFile());

        if (files.length === 0) {
            return [new InfoItem('No recordings found', 'Use Run Single to capture recordings.')];
        }

        return files
            .sort((a, b) => a.name.localeCompare(b.name))
            .map(file => {
                const filePath = path.join(recordingsDir, file.name);
                return new FileItem(
                    file.name,
                    vscode.Uri.file(filePath),
                    this.labelForFile(file.name)
                );
            });
    }

    private findConfigFile(projectPath: string): string | undefined {
        const candidates = ['setting.yaml', 'setting.yml', 'fluxloop.yaml', 'fluxloop.yml'];
        for (const candidate of candidates) {
            const fullPath = path.join(projectPath, candidate);
            if (fs.existsSync(fullPath)) {
                return fullPath;
            }
        }
        return undefined;
    }

    private labelForFile(filename: string): string | undefined {
        if (filename.endsWith('.jsonl')) {
            return 'JSONL';
        }
        if (filename.endsWith('.yaml') || filename.endsWith('.yml')) {
            return 'YAML';
        }
        if (filename.endsWith('.json')) {
            return 'JSON';
        }
        return undefined;
    }
}

class CategoryItem extends vscode.TreeItem {
    constructor(
        label: string,
        public readonly category: 'base' | 'generated' | 'recordings'
    ) {
        super(label, vscode.TreeItemCollapsibleState.Collapsed);
        this.contextValue = `inputs.category.${category}`;
    }
}

class BaseInputItem extends vscode.TreeItem {
    constructor(label: string, description?: string) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.iconPath = new vscode.ThemeIcon('symbol-string');
        this.command = {
            command: 'fluxloop.openConfig',
            title: 'Open Configuration'
        };
        this.contextValue = 'inputs.baseInput';
    }
}

class FileItem extends vscode.TreeItem {
    constructor(label: string, uri: vscode.Uri, description?: string) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.resourceUri = uri;
        this.description = description;
        this.iconPath = vscode.ThemeIcon.File;
        this.command = {
            command: 'vscode.open',
            title: 'Open File',
            arguments: [uri]
        };
        this.contextValue = 'inputs.file';
    }
}

class CommandItem extends vscode.TreeItem {
    constructor(label: string, command: string, tooltip?: string) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.command = {
            command,
            title: label
        };
        this.tooltip = tooltip;
        this.iconPath = new vscode.ThemeIcon('play');
        this.contextValue = 'inputs.command';
    }
}

class InfoItem extends vscode.TreeItem {
    constructor(label: string, description?: string) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.iconPath = new vscode.ThemeIcon('info');
        this.contextValue = 'inputs.info';
    }
}

