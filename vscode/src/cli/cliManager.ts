import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as which from 'which';
import { OutputChannelManager } from '../utils/outputChannel';
import { ProjectContext } from '../project/projectContext';
import { EnvironmentManager } from '../environment/environmentManager';

export class CLIManager {
    private cliPath: string | null = null;
    private lastLoggedPath: string | null = null;
    
    constructor(
        private context: vscode.ExtensionContext,
        private environmentManager: EnvironmentManager
    ) {}

    async checkInstallation(): Promise<boolean> {
        const environment = await this.environmentManager.getResolvedEnvironment();

        if (environment?.fluxloopPath) {
            this.cliPath = environment.fluxloopPath;
            this.logCliPath(this.cliPath, true);
            return true;
        }

        try {
            this.cliPath = await which.default('fluxloop');
            this.logCliPath(this.cliPath, false);
            return true;
        } catch {
            OutputChannelManager.getInstance().appendLine('FluxLoop CLI not found on PATH');
            return false;
        }
    }

    async promptInstall(): Promise<boolean> {
        const action = await vscode.window.showInformationMessage(
            'FluxLoop CLI is not installed. Would you like to install it?',
            'Install with pip',
            'Install with pipx',
            'Skip'
        );

        if (action === 'Install with pip') {
            return await this.installWithPip();
        } else if (action === 'Install with pipx') {
            return await this.installWithPipx();
        }

        return false;
    }

    private async installWithPip(): Promise<boolean> {
        const terminal = vscode.window.createTerminal('FluxLoop Install');
        terminal.show();
        terminal.sendText('pip install fluxloop-cli');
        
        // Wait for user to complete installation
        const result = await vscode.window.showInformationMessage(
            'Installing FluxLoop CLI. Click "Done" when installation is complete.',
            'Done',
            'Cancel'
        );

        if (result === 'Done') {
            // Re-check installation
            return await this.checkInstallation();
        }

        return false;
    }

    private async installWithPipx(): Promise<boolean> {
        const terminal = vscode.window.createTerminal('FluxLoop Install');
        terminal.show();
        terminal.sendText('pipx install fluxloop-cli');
        
        // Wait for user to complete installation
        const result = await vscode.window.showInformationMessage(
            'Installing FluxLoop CLI. Click "Done" when installation is complete.',
            'Done',
            'Cancel'
        );

        if (result === 'Done') {
            // Re-check installation
            return await this.checkInstallation();
        }

        return false;
    }

    async runCommand(args: string[], cwd?: string): Promise<void> {
        const environment = await this.environmentManager.getResolvedEnvironment();

        // Ensure CLI is available when no environment-specific executable exists
        if (!environment?.fluxloopPath) {
        if (!this.cliPath && !await this.checkInstallation()) {
            const installed = await this.promptInstall();
            if (!installed) {
                vscode.window.showErrorMessage('FluxLoop CLI is required to run this command');
                return;
                }
            }
        }

        const workspaceFolder = cwd || ProjectContext.getActiveWorkspacePath() || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('Select a FluxLoop project to continue.');
            ProjectContext.ensureActiveProject();
            return;
        }

        const outputChannel = OutputChannelManager.getInstance();
        const config = vscode.workspace.getConfiguration('fluxloop');
        
        if (config.get<boolean>('showOutputChannel')) {
            outputChannel.show();
        }

        const executionWrapper = config.get<string>('executionWrapper')?.trim();
        const resolved = await this.environmentManager.resolveCommand('fluxloop');
        const executable = this.quoteExecutable(resolved.command);
        const baseCommand = [executable, ...args].filter(Boolean).join(' ');
        const commandLine = executionWrapper ? `${executionWrapper} ${baseCommand}` : baseCommand;

        outputChannel.appendLine(`\n> ${commandLine}`);
        outputChannel.appendLine(`Working directory: ${workspaceFolder}`);
        outputChannel.appendLine('-'.repeat(50));

        // Create terminal and run command
        const terminal = vscode.window.createTerminal({
            name: 'FluxLoop',
            cwd: workspaceFolder,
            env: await this.environmentManager.getProcessEnv(this.getEnvironmentVariables())
        });

        terminal.show();
        terminal.sendText(commandLine);
    }

    private getEnvironmentVariables(): { [key: string]: string } {
        const config = vscode.workspace.getConfiguration('fluxloop');
        const env: { [key: string]: string } = {};

        const collectorUrl = config.get<string>('collectorUrl');
        if (collectorUrl) {
            env['FLUXLOOP_COLLECTOR_URL'] = collectorUrl;
        }

        const apiKey = config.get<string>('apiKey');
        if (apiKey) {
            env['FLUXLOOP_API_KEY'] = apiKey;
        }

        return env;
    }

    private quoteExecutable(executable: string): string {
        if (executable.includes(' ')) {
            if (process.platform === 'win32') {
                return `"${executable.replace(/"/g, '""')}"`;
            }
            return `"${executable.replace(/"/g, '\\"')}"`;
        }
        return executable;
    }

    private logCliPath(path: string, fromEnvironment: boolean): void {
        if (this.lastLoggedPath === path) {
            return;
        }
        this.lastLoggedPath = path;
        const source = fromEnvironment ? '[FluxLoop Env] fluxloop CLI resolved from environment' : 'FluxLoop CLI found at';
        OutputChannelManager.getInstance().appendLine(`${source}: ${path}`);
    }
}
