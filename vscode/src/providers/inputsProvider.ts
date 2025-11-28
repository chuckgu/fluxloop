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
            return [new InfoItem('Select a project to view inputs', undefined)];
        }

        if (!element) {
            return [
                new CategoryItem('Configuration', 'config'),
                new CommandItem('Generate New Inputs…', 'fluxloop.generateInputs', 'Start generation wizard', 'debug-start'),
                new CategoryItem('Generated Inputs', 'generated')
            ];
        }

        if (element instanceof CategoryItem) {
            if (element.category === 'config') {
                return [
                    new CommandItem('Open Configuration', 'fluxloop.openInputConfig', 'Open configs/input.yaml', 'gear'),
                    new CategoryItem('Base Input', 'base')
                ];
            }
            if (element.category === 'base') {
                    return this.getBaseInputs(projectPath);
            }
            if (element.category === 'generated') {
                    return this.getGeneratedInputs(projectPath);
            }
        }

        return [];
    }

    private async getBaseInputs(projectPath: string): Promise<InputsTreeItem[]> {
        const configInfo = this.resolveInputConfig(projectPath);
        if (!configInfo) {
            return [new InfoItem('No input configuration found', 'Create configs/input.yaml to define the base input.')];
        }

        try {
            const raw = await fs.promises.readFile(configInfo.path, 'utf8');
            const parsed = parseYaml(raw) as { base_inputs?: Array<{ input?: string; expected_intent?: string }>; input?: { base_inputs?: Array<{ input?: string; expected_intent?: string }> } } | undefined;
            const baseInputs = Array.isArray(parsed?.base_inputs)
                ? parsed?.base_inputs
                : Array.isArray(parsed?.input?.base_inputs)
                    ? parsed?.input?.base_inputs
                    : undefined;

            if (!Array.isArray(baseInputs) || baseInputs.length === 0) {
                return [new InfoItem('No base input defined', `Add base_inputs[0] to ${configInfo.label}.`)];
            }

            const primary = baseInputs[0];
            const configUri = vscode.Uri.file(configInfo.path);
            const label = primary?.input || 'Base Input';
            const description = primary?.expected_intent ? `Intent: ${primary.expected_intent}` : 'Primary seed for generation';
            return [
                new InfoItem('This base input seeds the generator', `Edit ${configInfo.label} to update it.`),
                new BaseInputItem(label, description, configUri)
            ];
        } catch (error) {
            console.error('Failed to parse input configuration', error);
            return [new InfoItem('Unable to load base input', `Check ${configInfo.label} for YAML errors.`)];
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
            return [new InfoItem('No recordings found', 'Use FluxLoop: Enable Recording or CLI record commands to capture inputs.')];
        }

        const entries = await fs.promises.readdir(recordingsDir, { withFileTypes: true });
        const files = entries.filter(entry => entry.isFile());

        if (files.length === 0) {
            return [new InfoItem('No recordings found', 'Use FluxLoop: Enable Recording or CLI record commands to capture inputs.')];
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

    private resolveInputConfig(projectPath: string): { path: string; label: string } | undefined {
        const newPath = path.join(projectPath, 'configs', 'input.yaml');
        if (fs.existsSync(newPath)) {
            return { path: newPath, label: 'configs/input.yaml' };
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
        public readonly category: 'config' | 'base' | 'generated'
    ) {
        super(label, vscode.TreeItemCollapsibleState.Collapsed);
        this.contextValue = `inputs.category.${category}`;
        if (category === 'config') {
            this.iconPath = new vscode.ThemeIcon('settings-gear');
        }
    }
}

class BaseInputItem extends vscode.TreeItem {
    constructor(label: string, description: string | undefined, configUri: vscode.Uri) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.iconPath = new vscode.ThemeIcon('symbol-string');
        this.command = {
            command: 'vscode.open',
            title: 'Open Input Configuration',
            arguments: [configUri]
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
    constructor(label: string, command: string, tooltip?: string, iconId = 'debug-start') {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.command = {
            command,
            title: label
        };
        this.tooltip = tooltip;
        this.iconPath = new vscode.ThemeIcon(iconId);
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

