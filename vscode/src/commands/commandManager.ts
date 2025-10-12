import * as vscode from 'vscode';
import * as path from 'path';
import { CLIManager } from '../cli/cliManager';
import { WireframeViewer } from '../wireframe/wireframeViewer';
import { InputGenerationWizard } from '../wireframe/inputGenerationWizard';
import { DialogsWireframe } from '../wireframe/dialogsWireframe';
import { WebviewsWireframe } from '../wireframe/webviewsWireframe';
import { InteractiveWireframe } from '../wireframe/interactiveWireframe';
import { ProjectContext } from '../project/projectContext';
import { ProjectManager } from '../project/projectManager';

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
            vscode.commands.registerCommand('fluxloop.openConfig', (projectId?: string) => this.openConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.selectEnvironment', () => this.selectEnvironment()),
            vscode.commands.registerCommand('fluxloop.showWireframe', () => this.showWireframe()),
            vscode.commands.registerCommand('fluxloop.showInputWizard', () => this.showInputWizard()),
            vscode.commands.registerCommand('fluxloop.showDialogsWireframe', () => this.showDialogsWireframe()),
            vscode.commands.registerCommand('fluxloop.showWebviewsWireframe', () => this.showWebviewsWireframe()),
            vscode.commands.registerCommand('fluxloop.showInteractiveWireframe', () => this.showInteractiveWireframe())
        );
    }

    private async initProject() {
        void vscode.commands.executeCommand('fluxloop.createProject');
    }

    private async runExperiment() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
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

        if (environment === 'Docker') {
            vscode.window.showWarningMessage('Docker execution from VSCode is not yet implemented. Please run the CLI manually.');
            return;
        }

        if (environment === 'Dev Container' && !process.env.REMOTE_CONTAINERS) {
            vscode.window.showErrorMessage('Dev Container execution requires running inside a Dev Container.');
            return;
        }

        await this.cliManager.runCommand(args, project.path);
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
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        const relativePath = path.relative(project.path, document.fileName);
        if (!relativePath || relativePath.startsWith('..')) {
            vscode.window.showErrorMessage('Active file is not within the selected FluxLoop project');
            return;
        }
        const modulePath = relativePath.replace(/\.py$/, '').replace(/[\\/]+/g, '.');

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
        await this.cliManager.runCommand(args, project.path);
    }

    private async showStatus() {
        const args = ['status', 'check', '--verbose'];
        await this.cliManager.runCommand(args, ProjectContext.getActiveWorkspacePath());
    }

    private async openConfig(projectId?: string) {
        const project = projectId ? ProjectManager.getInstance().getProjectById(projectId) : ProjectContext.ensureActiveProject();
        if (!project) {
            if (projectId) {
                vscode.window.showWarningMessage('The selected project is no longer available.');
            }
            return;
        }

        const configUri = vscode.Uri.joinPath(vscode.Uri.file(project.path), 'setting.yaml');
        try {
            const document = await vscode.workspace.openTextDocument(configUri);
            vscode.window.showTextDocument(document);
        } catch {
            vscode.window.showErrorMessage('No setting.yaml found');
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

    private showWireframe() {
        const wireframeViewer = new WireframeViewer(this.context);
        wireframeViewer.createOrShow();
    }

    private showInputWizard() {
        const inputWizard = new InputGenerationWizard(this.context);
        inputWizard.createOrShow();
    }

    private showDialogsWireframe() {
        const dialogsWireframe = new DialogsWireframe(this.context);
        dialogsWireframe.createOrShow();
    }

    private showWebviewsWireframe() {
        const webviewsWireframe = new WebviewsWireframe(this.context);
        webviewsWireframe.createOrShow();
    }

    private showInteractiveWireframe() {
        const interactiveWireframe = new InteractiveWireframe(this.context);
        interactiveWireframe.createOrShow();
    }
}
