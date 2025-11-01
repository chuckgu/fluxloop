import * as vscode from 'vscode';
import { ExperimentsProvider } from './providers/experimentsProvider';
import { ResultsProvider } from './providers/resultsProvider';
import { StatusProvider } from './providers/statusProvider';
import { ProjectsProvider } from './providers/projectsProvider';
import { InputsProvider } from './providers/inputsProvider';
import { CommandManager } from './commands/commandManager';
import { CLIManager } from './cli/cliManager';
import { OutputChannelManager } from './utils/outputChannel';
import { ProjectEntry, ProjectManager } from './project/projectManager';
import { ProjectContext } from './project/projectContext';
import { ProjectCommands } from './commands/projectCommands';

export async function activate(context: vscode.ExtensionContext) {
    console.log('FluxLoop extension is now active');

    // Initialize output channel
    const outputChannel = OutputChannelManager.getInstance();
    outputChannel.appendLine('FluxLoop extension activated');

    // Initialize project services
    const projectManager = ProjectManager.initialize(context);
    ProjectContext.initialize(context);

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
    const projectsProvider = new ProjectsProvider();
    const inputsProvider = new InputsProvider();
    const experimentsProvider = new ExperimentsProvider(context.workspaceState);
    const resultsProvider = new ResultsProvider();
    const statusProvider = new StatusProvider();

    vscode.window.registerTreeDataProvider('fluxloop.projects', projectsProvider);
    vscode.window.registerTreeDataProvider('fluxloop.inputs', inputsProvider);
    vscode.window.registerTreeDataProvider('fluxloop.experiments', experimentsProvider);
    vscode.window.registerTreeDataProvider('fluxloop.results', resultsProvider);
    vscode.window.registerTreeDataProvider('fluxloop.status', statusProvider);

    // Initialize command manager
    const commandManager = new CommandManager(context, cliManager, statusProvider, inputsProvider);
    commandManager.registerCommands();

    // Register project commands
    const projectCommands = new ProjectCommands(context, cliManager);
    context.subscriptions.push(...projectCommands.register());

    // Refresh providers when project changes
    const refreshProviders = () => {
        projectsProvider.refresh();
        experimentsProvider.refresh();
        inputsProvider.refresh();
        resultsProvider.refresh();
        statusProvider.refresh();
    };

    let activeProjectDisposables: vscode.Disposable[] = [];

    const disposeActiveProjectListeners = () => {
        while (activeProjectDisposables.length) {
            const disposable = activeProjectDisposables.pop();
            disposable?.dispose();
        }
    };

    const registerProjectWatchers = (project: ProjectEntry | undefined) => {
        disposeActiveProjectListeners();

        if (!project) {
            return;
        }

        const disposables: vscode.Disposable[] = [];
 
        const configPattern = new vscode.RelativePattern(project.path, 'configs/**/*');
        const configWatcher = vscode.workspace.createFileSystemWatcher(configPattern);
        const handleConfigUpdate = () => {
            projectManager.refreshProjectById(project.id);
            experimentsProvider.refresh();
            inputsProvider.refresh();
            statusProvider.refresh();
        };

        disposables.push(configWatcher);
        disposables.push(configWatcher.onDidCreate(handleConfigUpdate));
        disposables.push(configWatcher.onDidChange(handleConfigUpdate));
        disposables.push(configWatcher.onDidDelete(handleConfigUpdate));

        const envPattern = new vscode.RelativePattern(project.path, '.env');
        const envWatcher = vscode.workspace.createFileSystemWatcher(envPattern);
        const handleEnvUpdate = () => {
            experimentsProvider.refresh();
            statusProvider.refresh();
        };

        disposables.push(envWatcher);
        disposables.push(envWatcher.onDidCreate(handleEnvUpdate));
        disposables.push(envWatcher.onDidChange(handleEnvUpdate));
        disposables.push(envWatcher.onDidDelete(handleEnvUpdate));

        const experimentsPattern = new vscode.RelativePattern(project.path, 'experiments/**');
        const experimentsWatcher = vscode.workspace.createFileSystemWatcher(experimentsPattern);
        const handleExperimentUpdate = () => {
            experimentsProvider.refresh();
            resultsProvider.refresh();
        };
        const inputsPattern = new vscode.RelativePattern(project.path, 'inputs/**');
        const inputsWatcher = vscode.workspace.createFileSystemWatcher(inputsPattern);
        const handleInputsUpdate = () => {
            inputsProvider.refresh();
        };

        disposables.push(inputsWatcher);
        disposables.push(inputsWatcher.onDidCreate(handleInputsUpdate));
        disposables.push(inputsWatcher.onDidChange(handleInputsUpdate));
        disposables.push(inputsWatcher.onDidDelete(handleInputsUpdate));

        const recordingsPattern = new vscode.RelativePattern(project.path, 'recordings/**');
        const recordingsWatcher = vscode.workspace.createFileSystemWatcher(recordingsPattern);
        const handleRecordingsUpdate = () => {
            inputsProvider.refresh();
        };

        disposables.push(recordingsWatcher);
        disposables.push(recordingsWatcher.onDidCreate(handleRecordingsUpdate));
        disposables.push(recordingsWatcher.onDidChange(handleRecordingsUpdate));
        disposables.push(recordingsWatcher.onDidDelete(handleRecordingsUpdate));


        disposables.push(experimentsWatcher);
        disposables.push(experimentsWatcher.onDidCreate(handleExperimentUpdate));
        disposables.push(experimentsWatcher.onDidChange(handleExperimentUpdate));
        disposables.push(experimentsWatcher.onDidDelete(handleExperimentUpdate));

        activeProjectDisposables = disposables;
        context.subscriptions.push(...disposables);
    };

    const handleActiveProjectChange = (project: ProjectEntry | undefined) => {
        registerProjectWatchers(project);
        refreshProviders();
    };

    handleActiveProjectChange(projectManager.getActiveProject());

    projectManager.onDidChangeActiveProject(handleActiveProjectChange);
    projectManager.onDidChangeProjects(() => {
        projectsProvider.refresh();
        statusProvider.refresh();
        registerProjectWatchers(projectManager.getActiveProject());
    });

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
