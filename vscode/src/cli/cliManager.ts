import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as which from 'which';
import { OutputChannelManager } from '../utils/outputChannel';
import { ProjectContext } from '../project/projectContext';

export class CLIManager {
    private cliPath: string | null = null;
    
    constructor(private context: vscode.ExtensionContext) {}

    async checkInstallation(): Promise<boolean> {
        try {
            this.cliPath = await which.default('fluxloop');
            OutputChannelManager.getInstance().appendLine(`FluxLoop CLI found at: ${this.cliPath}`);
            return true;
        } catch {
            OutputChannelManager.getInstance().appendLine('FluxLoop CLI not found');
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
        // Ensure CLI is installed
        if (!this.cliPath && !await this.checkInstallation()) {
            const installed = await this.promptInstall();
            if (!installed) {
                vscode.window.showErrorMessage('FluxLoop CLI is required to run this command');
                return;
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
        const baseCommand = `fluxloop ${args.join(' ')}`;
        const commandLine = executionWrapper ? `${executionWrapper} ${baseCommand}` : baseCommand;

        outputChannel.appendLine(`\n> ${commandLine}`);
        outputChannel.appendLine(`Working directory: ${workspaceFolder}`);
        outputChannel.appendLine('-'.repeat(50));

        // Create terminal and run command
        const terminal = vscode.window.createTerminal({
            name: 'FluxLoop',
            cwd: workspaceFolder,
            env: this.getEnvironmentVariables()
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
}
