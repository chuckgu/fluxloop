import * as vscode from 'vscode';
import { FluxLoopProvider } from './providers/fluxloopProvider';
import { ExperimentsProvider } from './providers/experimentsProvider';
import { ResultsProvider } from './providers/resultsProvider';
import { StatusProvider } from './providers/statusProvider';
import { CommandManager } from './commands/commandManager';
import { CLIManager } from './cli/cliManager';
import { OutputChannelManager } from './utils/outputChannel';

export async function activate(context: vscode.ExtensionContext) {
    console.log('FluxLoop extension is now active');

    // Initialize output channel
    const outputChannel = OutputChannelManager.getInstance();
    outputChannel.appendLine('FluxLoop extension activated');

    // Initialize CLI manager
    const cliManager = new CLIManager(context);
    
    // Check CLI installation
    const cliInstalled = await cliManager.checkInstallation();
    if (!cliInstalled) {
        const config = vscode.workspace.getConfiguration('fluxloop');
        if (config.get<boolean>('autoInstallCli')) {
            await cliManager.promptInstall();
        }
    }

    // Register tree data providers
    const experimentsProvider = new ExperimentsProvider(context.workspaceState);
    const resultsProvider = new ResultsProvider();
    const statusProvider = new StatusProvider();

    vscode.window.registerTreeDataProvider('fluxloop.experiments', experimentsProvider);
    vscode.window.registerTreeDataProvider('fluxloop.results', resultsProvider);
    vscode.window.registerTreeDataProvider('fluxloop.status', statusProvider);

    // Initialize command manager
    const commandManager = new CommandManager(context, cliManager);
    commandManager.registerCommands();

    // Register file watcher for setting.yaml
    const watcher = vscode.workspace.createFileSystemWatcher('**/fluxloop.{yaml,yml}');
    watcher.onDidCreate(() => {
        experimentsProvider.refresh();
        outputChannel.appendLine('FluxLoop configuration created');
    });
    watcher.onDidChange(() => {
        experimentsProvider.refresh();
        outputChannel.appendLine('FluxLoop configuration updated');
    });
    watcher.onDidDelete(() => {
        experimentsProvider.refresh();
        outputChannel.appendLine('FluxLoop configuration deleted');
    });
    context.subscriptions.push(watcher);

    // Show welcome message if first time
    const hasShownWelcome = context.globalState.get('fluxloop.hasShownWelcome');
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
        context.globalState.update('fluxloop.hasShownWelcome', true);
    }
}

function showWelcomeMessage(context: vscode.ExtensionContext) {
    vscode.window.showInformationMessage(
        'Welcome to FluxLoop! Get started by initializing a project.',
        'Initialize Project',
        'Documentation'
    ).then(selection => {
        if (selection === 'Initialize Project') {
            vscode.commands.executeCommand('fluxloop.init');
        } else if (selection === 'Documentation') {
            vscode.env.openExternal(vscode.Uri.parse('https://docs.fluxloop.dev'));
        }
    });
}

export function deactivate() {
    OutputChannelManager.getInstance().dispose();
}
