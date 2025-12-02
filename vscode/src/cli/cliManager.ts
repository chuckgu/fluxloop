import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as which from 'which';
import { OutputChannelManager } from '../utils/outputChannel';
import { ProjectContext } from '../project/projectContext';
import { EnvironmentManager } from '../environment/environmentManager';

type RunCommandOptions = {
    executablePath?: string;
};

type PipInstallCommand = {
    command: string;
    cwd?: string;
    scope: 'environment' | 'global';
};

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
        const installSpec = await this.buildEnvironmentAwarePipCommand('fluxloop-cli');
        const terminal = vscode.window.createTerminal({
            name: 'FluxLoop Install',
            cwd: installSpec.cwd
        });

        terminal.show();
        if (installSpec.scope === 'environment' && installSpec.cwd) {
            terminal.sendText(`# Installing FluxLoop CLI inside ${installSpec.cwd}`);
        }
        terminal.sendText(installSpec.command);
        
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

    async runCommand(args: string[], cwd?: string, options: RunCommandOptions = {}): Promise<void> {
        const environment = await this.environmentManager.getResolvedEnvironment();

        // Ensure CLI is available when no environment-specific executable exists
        if (!options.executablePath && !environment?.fluxloopPath) {
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

        let resolvedExecutablePath = options.executablePath;
        if (!resolvedExecutablePath) {
        const resolved = await this.environmentManager.resolveCommand('fluxloop');
            resolvedExecutablePath = resolved.command;
        }

        const executable = this.quoteExecutable(resolvedExecutablePath);
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

    private async buildEnvironmentAwarePipCommand(packageName: string): Promise<PipInstallCommand> {
        try {
            const environment = await this.environmentManager.getResolvedEnvironment(true);
            if (environment && environment.environmentType !== 'global') {
                const pythonExecutable =
                    environment.pythonPath && fs.existsSync(environment.pythonPath) ? environment.pythonPath : undefined;
                if (pythonExecutable) {
                    const command = `${this.quoteExecutable(pythonExecutable)} -m pip install ${packageName}`;
                    return { command, cwd: environment.root, scope: 'environment' };
                }

                const pipExecutable = this.findPipExecutable(environment.root);
                if (pipExecutable) {
                    const command = `${this.quoteExecutable(pipExecutable)} install ${packageName}`;
                    return { command, cwd: environment.root, scope: 'environment' };
                }
            }
        } catch (error) {
            OutputChannelManager.getInstance().appendLine(`[FluxLoop Install] Failed to inspect environment: ${String(error)}`);
        }

        return {
            command: `pip install ${packageName}`,
            scope: 'global'
        };
    }

    private findPipExecutable(root?: string): string | undefined {
        if (!root) {
            return undefined;
        }

        const pipDir = process.platform === 'win32' ? path.join(root, 'Scripts') : path.join(root, 'bin');
        const candidates = process.platform === 'win32' ? ['pip.exe', 'pip3.exe', 'pip'] : ['pip', 'pip3'];

        for (const candidateName of candidates) {
            const candidatePath = path.join(pipDir, candidateName);
            try {
                if (fs.existsSync(candidatePath) && fs.statSync(candidatePath).isFile()) {
                    return candidatePath;
                }
            } catch {
                // ignore filesystem errors while probing for pip executables
            }
        }

        return undefined;
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
