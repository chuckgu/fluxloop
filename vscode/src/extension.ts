import * as vscode from 'vscode';
import { ExperimentsProvider } from './providers/experimentsProvider';
import { ResultsProvider } from './providers/resultsProvider';
import { ProjectsProvider } from './providers/projectsProvider';
import { InputsProvider } from './providers/inputsProvider';
import { CommandManager } from './commands/commandManager';
import { CLIManager } from './cli/cliManager';
import { OutputChannelManager } from './utils/outputChannel';
import { ProjectEntry, ProjectManager } from './project/projectManager';
import { ProjectContext } from './project/projectContext';
import { ProjectCommands } from './commands/projectCommands';
import { IntegrationProvider, IntegrationSuggestion, IntegrationItem } from './providers/integrationProvider';
import { IntegrationService, FluxAgentCommandOptions } from './integration/integrationService';
import { EnvironmentManager } from './environment/environmentManager';
import { DashboardViewProvider, FluxloopActiveView, OnboardingCard } from './providers/dashboardViewProvider';

export async function activate(context: vscode.ExtensionContext) {
    console.log('FluxLoop extension is now active');

    // Initialize output channel
    const outputChannel = OutputChannelManager.getInstance();
    outputChannel.appendLine('FluxLoop extension activated');

    // Initialize project services
    const projectManager = ProjectManager.initialize(context);
    ProjectContext.initialize(context);

    // Initialize environment manager and CLI manager
    const environmentManager = new EnvironmentManager();
    context.subscriptions.push(environmentManager);
    await environmentManager.refreshActiveEnvironment();
    const cliManager = new CLIManager(context, environmentManager);

    // Register tree data providers
    const projectsProvider = new ProjectsProvider();
    const inputsProvider = new InputsProvider();
    const experimentsProvider = new ExperimentsProvider(context.workspaceState);
    const resultsProvider = new ResultsProvider();
    const integrationProvider = new IntegrationProvider();
    const integrationService = new IntegrationService(context, cliManager, integrationProvider, environmentManager);

    const ONBOARDING_STORAGE_KEY = 'fluxloop.onboarding.dismissedCards';
    const dismissedOnboardingCards = new Set(
        context.globalState.get<string[]>(ONBOARDING_STORAGE_KEY, [])
    );

    const allOnboardingCards: OnboardingCard[] = [
        /*
        {
            id: 'quick-start',
            title: 'Quick Start Guide',
            description: 'Step 1. Workspace: Set up your workspace\nStep 2. Playground: Run your experiments\nStep 3. Insights: View your analysis'
        },
        {
            id: 'layout-tip',
            title: 'Adjust tree layout',
            description: 'Drag the header grab line above each tree view to reposition or collapse it.'
        }
        */
    ];

    const getActiveOnboardingCards = (): OnboardingCard[] =>
        allOnboardingCards.filter(card => !dismissedOnboardingCards.has(card.id));

    let currentActiveView: FluxloopActiveView = 'workspace';

    const dashboardProvider = new DashboardViewProvider(context.extensionUri, {
        onSwitchView: view => {
            if (view !== currentActiveView) {
                setActiveView(view);
            }
        },
        onDismissOnboarding: async cardId => {
            if (!dismissedOnboardingCards.has(cardId)) {
                dismissedOnboardingCards.add(cardId);
                await context.globalState.update(ONBOARDING_STORAGE_KEY, Array.from(dismissedOnboardingCards));
                refreshOnboardingCards();
            }
        }
    });

    function setActiveView(view: FluxloopActiveView): void {
        currentActiveView = view;
        void vscode.commands.executeCommand('setContext', 'fluxloop.activeView', view);
        dashboardProvider.updateSnapshot({ activeView: view });
    }

    function refreshOnboardingCards(): void {
        dashboardProvider.updateSnapshot({ onboardingCards: getActiveOnboardingCards() });
    }

    dashboardProvider.updateSnapshot({
        project: projectManager.getActiveProject(),
        environment: environmentManager.getActiveEnvironment()
    });
    refreshOnboardingCards();
    setActiveView(currentActiveView);

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            DashboardViewProvider.viewType,
            dashboardProvider,
            { webviewOptions: { retainContextWhenHidden: true } }
        ),
        vscode.window.registerTreeDataProvider('fluxloop.projects', projectsProvider),
        vscode.window.registerTreeDataProvider('fluxloop.inputs', inputsProvider),
        vscode.window.registerTreeDataProvider('fluxloop.experiments', experimentsProvider),
        vscode.window.registerTreeDataProvider('fluxloop.results', resultsProvider),
        vscode.window.registerTreeDataProvider('fluxloop.integration', integrationProvider)
    );

    const fallbackAlertState = new Map<string, boolean>();

    context.subscriptions.push(
        environmentManager.onDidChangeEnvironment(environment => {
            dashboardProvider.updateSnapshot({ environment });

            if (!environment) {
                return;
            }

            const rootKey = environment.root || '__unknown__';
            const fallbackActive = environment.fallbackReason === 'missingLocalEnv';

            if (!fallbackActive) {
                fallbackAlertState.set(rootKey, false);
                return;
            }

            if (fallbackAlertState.get(rootKey)) {
                return;
            }

            fallbackAlertState.set(rootKey, true);
            const warning =
                'No virtual environment (.venv/venv) was detected for this FluxLoop project, so the global Python interpreter is being used temporarily. Create a virtual environment (e.g. python -m venv .venv) and rerun System Status -> Select Environment to rebind it.';

            void vscode.window.showWarningMessage(warning, 'Select Environment').then(selection => {
                if (selection === 'Select Environment') {
                    void vscode.commands.executeCommand('fluxloop.selectEnvironment');
                }
            });
        })
    );

    const resolveWorkspaceUri = (project?: ProjectEntry): vscode.Uri | undefined => {
        if (project?.path) {
            return vscode.Uri.file(project.path);
        }
        const folder = vscode.workspace.workspaceFolders?.[0];
        return folder?.uri;
    };

    await integrationProvider.setWorkspaceRoot(resolveWorkspaceUri(projectManager.getActiveProject()));

    // Initialize command manager
    const commandManager = new CommandManager(context, cliManager, environmentManager, inputsProvider, resultsProvider);
    commandManager.registerCommands();

    // Register project commands
    const projectCommands = new ProjectCommands(context, cliManager, environmentManager);
    context.subscriptions.push(...projectCommands.register());

    // Refresh providers when project changes
    const refreshProviders = () => {
        projectsProvider.refresh();
        experimentsProvider.refresh();
        inputsProvider.refresh();
        resultsProvider.refresh();
        integrationProvider.refresh();
        void integrationService.refreshStatus();
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
            void vscode.commands.executeCommand('fluxloop.integration.refresh');
        };

        disposables.push(configWatcher);
        disposables.push(configWatcher.onDidCreate(handleConfigUpdate));
        disposables.push(configWatcher.onDidChange(handleConfigUpdate));
        disposables.push(configWatcher.onDidDelete(handleConfigUpdate));

        const envPattern = new vscode.RelativePattern(project.path, '.env');
        const envWatcher = vscode.workspace.createFileSystemWatcher(envPattern);
        const handleEnvUpdate = () => {
            experimentsProvider.refresh();
            experimentsProvider.refresh();
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
        dashboardProvider.updateSnapshot({ project });
        void environmentManager.refreshActiveEnvironment();
        void integrationProvider.setWorkspaceRoot(resolveWorkspaceUri(project));
        refreshProviders();
    };

    handleActiveProjectChange(projectManager.getActiveProject());

    projectManager.onDidChangeActiveProject(handleActiveProjectChange);
    projectManager.onDidChangeProjects(() => {
        projectsProvider.refresh();
        integrationProvider.refresh();
        void environmentManager.refreshActiveEnvironment();
        void integrationService.refreshStatus();
        registerProjectWatchers(projectManager.getActiveProject());
        void integrationProvider.setWorkspaceRoot(resolveWorkspaceUri(projectManager.getActiveProject()));
        dashboardProvider.updateSnapshot({ project: projectManager.getActiveProject() });
    });

    context.subscriptions.push(
        vscode.commands.registerCommand('fluxloop.integration.connectMcp', () => {
            void integrationService.handleConnectMcp();
        }),
        vscode.commands.registerCommand('fluxloop.integration.showSetupGuide', () => {
            void integrationService.showSystemConsoleGuide();
        }),
        vscode.commands.registerCommand('fluxloop.integration.showPlaygroundGuide', () => {
            void integrationService.showPlaygroundGuide();
        }),
        vscode.commands.registerCommand('fluxloop.integration.runAgent', (options?: FluxAgentCommandOptions) => {
            void integrationService.runFluxAgent(options);
        }),
        vscode.commands.registerCommand('fluxloop.integration.openKnowledgeSearch', () => {
            void integrationService.openKnowledgeSearch();
        }),
        vscode.commands.registerCommand('fluxloop.integration.refresh', () => {
            void integrationService.refreshStatus();
        }),
        vscode.commands.registerCommand('fluxloop.integration.showSuggestion', (suggestion: IntegrationSuggestion) => {
            integrationService.showSuggestionDetail(suggestion);
        }),
        vscode.commands.registerCommand(
            'fluxloop.integration.removeSuggestion',
            async (target: IntegrationItem | IntegrationSuggestion) => {
                const suggestion =
                    target instanceof IntegrationItem ? target.suggestion : (target as IntegrationSuggestion | undefined);

                if (!suggestion) {
                    return;
                }

                await integrationProvider.removeSuggestion(suggestion.id);
                vscode.window.setStatusBarMessage('Integration suggestion removed.', 3000);
            },
        ),
        vscode.commands.registerCommand('fluxloop.integration.clearHistory', async () => {
            await integrationProvider.clearSuggestions();
            vscode.window.showInformationMessage('Flux Agent suggestion history cleared.');
        })
    );

    // Show welcome message if first time
    const hasShownWelcome = context.globalState.get('fluxloop.hasShownWelcome');
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
        context.globalState.update('fluxloop.hasShownWelcome', true);
    }

    await environmentManager.refreshActiveEnvironment();
    void integrationService.refreshStatus();
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
