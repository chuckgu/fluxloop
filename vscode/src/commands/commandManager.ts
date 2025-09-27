import * as vscode from 'vscode';
import * as path from 'path';
import { CLIManager } from '../cli/cliManager';
import { OutputChannelManager } from '../utils/outputChannel';

export class CommandManager {
    constructor(
        private context: vscode.ExtensionContext,
        private cliManager: CLIManager
    ) {}

    registerCommands() {
        // Register all commands
        this.context.subscriptions.push(
            vscode.commands.registerCommand('fluxloop.init', () => this.initProject()),
            vscode.commands.registerCommand('fluxloop.runExperiment', () => this.runExperiment()),
            vscode.commands.registerCommand('fluxloop.runSingle', () => this.runSingle()),
            vscode.commands.registerCommand('fluxloop.showStatus', () => this.showStatus()),
            vscode.commands.registerCommand('fluxloop.openConfig', () => this.openConfig()),
            vscode.commands.registerCommand('fluxloop.selectEnvironment', () => this.selectEnvironment())
        );
    }

    private async initProject() {
        const folderUri = await vscode.window.showOpenDialog({
            canSelectFolders: true,
            canSelectFiles: false,
            canSelectMany: false,
            openLabel: 'Select Project Folder',
            title: 'Initialize FluxLoop Project'
        });

        if (!folderUri || folderUri.length === 0) {
            return;
        }

        const projectPath = folderUri[0].fsPath;
        const projectName = await vscode.window.showInputBox({
            prompt: 'Enter project name',
            value: path.basename(projectPath),
            validateInput: (value) => {
                if (!value) {
                    return 'Project name is required';
                }
                return null;
            }
        });

        if (!projectName) {
            return;
        }

        const withExample = await vscode.window.showQuickPick(
            ['Yes', 'No'],
            {
                placeHolder: 'Include example agent?'
            }
        );

        const args = ['init', 'project', projectPath, '--name', projectName];
        if (withExample === 'No') {
            args.push('--no-example');
        }

        await this.cliManager.runCommand(args, projectPath);

        // Open the project
        const openInNewWindow = await vscode.window.showQuickPick(
            ['Current Window', 'New Window'],
            {
                placeHolder: 'Open project in...'
            }
        );

        if (openInNewWindow === 'New Window') {
            vscode.commands.executeCommand('vscode.openFolder', folderUri[0], true);
        } else if (openInNewWindow === 'Current Window') {
            vscode.commands.executeCommand('vscode.openFolder', folderUri[0], false);
        }
    }

    private async runExperiment() {
        // Check for config file
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const configUri = vscode.Uri.joinPath(workspaceFolders[0].uri, 'fluxloop.yaml');
        try {
            await vscode.workspace.fs.stat(configUri);
        } catch {
            const action = await vscode.window.showErrorMessage(
                'No fluxloop.yaml found. Initialize a project first?',
                'Initialize Project'
            );
            if (action === 'Initialize Project') {
                vscode.commands.executeCommand('fluxloop.init');
            }
            return;
        }

        // Select execution environment
        const environment = await this.selectExecutionEnvironment();
        if (!environment) {
            return;
        }

        // Get optional parameters
        const iterations = await vscode.window.showInputBox({
            prompt: 'Number of iterations (leave empty for default)',
            validateInput: (value) => {
                if (value && isNaN(parseInt(value))) {
                    return 'Must be a number';
                }
                return null;
            }
        });

        // Build command
        const args = ['run', 'experiment'];
        if (iterations) {
            args.push('--iterations', iterations);
        }

        // Run based on environment
        if (environment === 'Docker') {
            await this.runInDocker(args);
        } else if (environment === 'Dev Container') {
            await this.runInDevContainer(args);
        } else {
            await this.cliManager.runCommand(args);
        }
    }

    private async runSingle() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active Python file');
            return;
        }

        const document = editor.document;
        if (document.languageId !== 'python') {
            vscode.window.showErrorMessage('Current file is not a Python file');
            return;
        }

        // Get module path
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('File is not in a workspace');
            return;
        }

        const relativePath = path.relative(workspaceFolder.uri.fsPath, document.fileName);
        const modulePath = relativePath.replace(/\.py$/, '').replace(/\//g, '.');

        // Get function name
        const functionName = await vscode.window.showInputBox({
            prompt: 'Function name to run',
            value: 'run',
            validateInput: (value) => {
                if (!value) {
                    return 'Function name is required';
                }
                return null;
            }
        });

        if (!functionName) {
            return;
        }

        // Get input
        const input = await vscode.window.showInputBox({
            prompt: 'Input text for the agent',
            validateInput: (value) => {
                if (!value) {
                    return 'Input is required';
                }
                return null;
            }
        });

        if (!input) {
            return;
        }

        // Run command
        const args = ['run', 'single', modulePath, input, '--function', functionName];
        await this.cliManager.runCommand(args);
    }

    private async showStatus() {
        const args = ['status', 'check', '--verbose'];
        await this.cliManager.runCommand(args);
    }

    private async openConfig() {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const configUri = vscode.Uri.joinPath(workspaceFolders[0].uri, 'fluxloop.yaml');
        try {
            const document = await vscode.workspace.openTextDocument(configUri);
            vscode.window.showTextDocument(document);
        } catch {
            vscode.window.showErrorMessage('No fluxloop.yaml found');
        }
    }

    private async selectEnvironment() {
        const environment = await this.selectExecutionEnvironment();
        if (environment) {
            const config = vscode.workspace.getConfiguration('fluxloop');
            await config.update('defaultEnvironment', environment, vscode.ConfigurationTarget.Workspace);
            vscode.window.showInformationMessage(`Default environment set to: ${environment}`);
        }
    }

    private async selectExecutionEnvironment(): Promise<string | undefined> {
        const config = vscode.workspace.getConfiguration('fluxloop');
        const defaultEnv = config.get<string>('defaultEnvironment') || 'Local Python';

        const items: vscode.QuickPickItem[] = [
            {
                label: 'Local Python',
                description: 'Run with local Python interpreter',
                detail: 'Uses the current Python environment',
                picked: defaultEnv === 'Local Python'
            },
            {
                label: 'Docker',
                description: 'Run in Docker container',
                detail: 'Requires Docker Desktop',
                picked: defaultEnv === 'Docker'
            },
            {
                label: 'Dev Container',
                description: 'Run in current Dev Container',
                detail: 'If running in a Dev Container',
                picked: defaultEnv === 'Dev Container'
            }
        ];

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select execution environment',
            title: 'FluxLoop Execution Environment'
        });

        return selected?.label;
    }

    private async runInDocker(args: string[]) {
        // TODO: Implement Docker execution
        vscode.window.showInformationMessage('Docker execution not yet implemented');
    }

    private async runInDevContainer(args: string[]) {
        // Check if in Dev Container
        if (!process.env.REMOTE_CONTAINERS) {
            vscode.window.showErrorMessage('Not running in a Dev Container');
            return;
        }
        
        // Run normally (already in container)
        await this.cliManager.runCommand(args);
    }
}
