import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { parse as parseYaml } from 'yaml';
import { CLIManager } from '../cli/cliManager';
import { EnvironmentManager } from '../environment/environmentManager';
import { WireframeViewer } from '../wireframe/wireframeViewer';
import { InputGenerationWizard } from '../wireframe/inputGenerationWizard';
import { DialogsWireframe } from '../wireframe/dialogsWireframe';
import { WebviewsWireframe } from '../wireframe/webviewsWireframe';
import { InteractiveWireframe } from '../wireframe/interactiveWireframe';
import { ProjectContext } from '../project/projectContext';
import { ProjectEntry, ProjectManager } from '../project/projectManager';
import { InputsProvider } from '../providers/inputsProvider';
import { ResultsProvider } from '../providers/resultsProvider';
import { OutputChannelManager } from '../utils/outputChannel';

type BaseInputSeed = {
    value: string;
    intent?: string;
};

const VARIATION_STRATEGIES = [
    'rephrase',
    'error_prone',
    'typo',
    'verbose',
    'concise',
    'persona_based',
    'adversarial',
    'multilingual',
    'custom'
] as const;

export class CommandManager {
    constructor(
        private context: vscode.ExtensionContext,
        private cliManager: CLIManager,
        private environmentManager: EnvironmentManager,
        private inputsProvider?: InputsProvider,
        private resultsProvider?: ResultsProvider
    ) {}

    registerCommands() {
        // Register all commands
        this.context.subscriptions.push(
            vscode.commands.registerCommand('fluxloop.init', () => this.initProject()),
            vscode.commands.registerCommand('fluxloop.runExperiment', () => this.runExperiment()),
            vscode.commands.registerCommand('fluxloop.parseExperiment', (experimentPath?: string) => this.parseExperiment(experimentPath)),
            vscode.commands.registerCommand('fluxloop.evaluateExperiment', (experimentPath?: string) => this.evaluateExperiment(experimentPath)),
            vscode.commands.registerCommand('fluxloop.runSingle', () => this.runSingle()),
            vscode.commands.registerCommand('fluxloop.generateInputs', () => this.generateInputs()),
            vscode.commands.registerCommand('fluxloop.showStatus', () => this.showStatus()),
            vscode.commands.registerCommand('fluxloop.enableRecording', () => this.enableRecording()),
            vscode.commands.registerCommand('fluxloop.disableRecording', () => this.disableRecording()),
            vscode.commands.registerCommand('fluxloop.showRecordingStatus', () => this.showRecordingStatus()),
            vscode.commands.registerCommand('fluxloop.openConfig', (projectId?: string) => this.openSimulationConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openProjectConfig', (projectId?: string) => this.openProjectConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openInputConfig', (projectId?: string) => this.openInputConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openProjectEnv', (projectId?: string) => this.openProjectEnv(projectId)),
            vscode.commands.registerCommand('fluxloop.openSimulationConfig', (projectId?: string) => this.openSimulationConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openEvaluationConfig', (projectId?: string) => this.openEvaluationConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.selectEnvironment', () => this.selectEnvironment()),
            vscode.commands.registerCommand('fluxloop.showEnvironmentInfo', () => this.showEnvironmentInfo()),
            vscode.commands.registerCommand('fluxloop.runDoctor', () => this.runDoctor()),
            vscode.commands.registerCommand('fluxloop.configureExecutionWrapper', () => this.configureExecutionWrapper()),
            vscode.commands.registerCommand('fluxloop.setProjectSourceRoot', (projectId?: string) => this.setProjectSourceRoot(projectId)),
            vscode.commands.registerCommand('fluxloop.openProjectSourceRoot', (projectId?: string) => this.openProjectSourceRoot(projectId)),
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
        void vscode.commands.executeCommand('fluxloop.integration.refresh');

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
        void vscode.commands.executeCommand('fluxloop.integration.refresh');
    }

    private async parseExperiment(experimentPath?: string) {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        const experimentsDir = path.join(project.path, 'experiments');
        if (!fs.existsSync(experimentsDir)) {
            void vscode.window.showWarningMessage('Experiment results folder not found. Run an experiment first.');
            return;
        }

        let targetPath = experimentPath && fs.existsSync(experimentPath)
            ? experimentPath
            : undefined;

        if (!targetPath) {
            const directories = fs.readdirSync(experimentsDir)
                .filter(name => {
                    try {
                        return fs.statSync(path.join(experimentsDir, name)).isDirectory();
                    } catch {
                        return false;
                    }
                })
                .sort((a, b) => b.localeCompare(a));

            if (directories.length === 0) {
                void vscode.window.showWarningMessage('No experiment results available to parse.');
                return;
            }

            const pick = await vscode.window.showQuickPick(
                directories.map(name => ({
                    label: name,
                    description: path.join('experiments', name)
                })),
                {
                    title: 'Select experiment results',
                    placeHolder: 'Choose the experiment folder to parse.'
                }
            );

            if (!pick) {
                return;
            }

            targetPath = path.join(experimentsDir, pick.label);
        }

        if (!targetPath || !fs.existsSync(targetPath)) {
            void vscode.window.showErrorMessage('Unable to find the selected experiment folder.');
            return;
        }

        const relativePath = path.relative(project.path, targetPath);
        const experimentArg = relativePath && !relativePath.startsWith('..') ? relativePath : targetPath;

        const outputDir = await vscode.window.showInputBox({
            prompt: 'Output directory for parsed results (optional)',
            placeHolder: 'Example: parsed_results (leave empty for default)',
            ignoreFocusOut: true
        });

        if (outputDir === undefined) {
            return;
        }

        const defaultOutputDir = 'per_trace_analysis';
        const trimmedOutput = outputDir.trim();
        const finalOutputDir = trimmedOutput.length > 0 ? trimmedOutput : defaultOutputDir;
        const resolvedOutputPath = path.isAbsolute(finalOutputDir)
            ? finalOutputDir
            : path.join(targetPath, finalOutputDir);

        let overwrite = false;
        if (fs.existsSync(resolvedOutputPath)) {
            const overwriteChoice = await vscode.window.showQuickPick<{ label: string; value: 'overwrite' | 'cancel'; description?: string }>(
                [
                    { label: 'Yes, overwrite', value: 'overwrite' },
                    { label: 'No', value: 'cancel' }
                ],
                {
                    title: `${finalOutputDir} already exists. Overwrite?`,
                    placeHolder: 'Choose "No" to keep the existing files.'
                }
            );

            if (!overwriteChoice || overwriteChoice.value === 'cancel') {
                return;
            }

            overwrite = overwriteChoice.value === 'overwrite';
        }

        const args = ['parse', 'experiment', experimentArg, '--output', finalOutputDir];
        if (overwrite) {
            args.push('--overwrite');
        }

        await this.cliManager.runCommand(args, project.path);
        this.resultsProvider?.refresh();
    }

    private async evaluateExperiment(experimentPath?: string) {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        const experimentsDir = path.join(project.path, 'experiments');
        if (!fs.existsSync(experimentsDir)) {
            void vscode.window.showWarningMessage('Experiment results folder not found. Run an experiment first.');
            return;
        }

        let targetPath = experimentPath && fs.existsSync(experimentPath)
            ? experimentPath
            : undefined;

        if (!targetPath) {
            const directories = fs.readdirSync(experimentsDir)
                .filter(name => {
                    try {
                        return fs.statSync(path.join(experimentsDir, name)).isDirectory();
                    } catch {
                        return false;
                    }
                })
                .sort((a, b) => b.localeCompare(a));

            if (directories.length === 0) {
                void vscode.window.showWarningMessage('No experiment results available to evaluate.');
                return;
            }

            const pick = await vscode.window.showQuickPick(
                directories.map(name => ({
                    label: name,
                    description: path.join('experiments', name)
                })),
                {
                    title: 'Select experiment results to evaluate',
                    placeHolder: 'Choose the experiment folder you want to evaluate.'
                }
            );

            if (!pick) {
                return;
            }

            targetPath = path.join(experimentsDir, pick.label);
        }

        if (!targetPath || !fs.existsSync(targetPath)) {
            void vscode.window.showErrorMessage('Unable to find the selected experiment folder.');
            return;
        }

        const relativePath = path.relative(project.path, targetPath);
        const experimentArg = relativePath && !relativePath.startsWith('..') ? relativePath : targetPath;

        const configRelative = path.join('configs', 'evaluation.yaml');
        const configAbsolute = path.join(project.path, configRelative);
        let configArg = configRelative;
        if (!fs.existsSync(configAbsolute)) {
            void vscode.window.showWarningMessage('configs/evaluation.yaml is missing. Check your CLI configuration.');
        } else {
            const configInfo = await this.loadEvaluationConfig(project.path);
            const goal = this.extractEvaluationGoal(configInfo?.data);
            const goalDecision = await this.confirmEvaluationGoal(goal);
            if (goalDecision === 'cancel') {
                return;
            }
            if (goalDecision === 'edit') {
                await vscode.commands.executeCommand('fluxloop.openEvaluationConfig');
                return;
            }
            const relativeConfig = path.relative(project.path, configAbsolute);
            configArg = relativeConfig && !relativeConfig.startsWith('..') ? relativeConfig : configAbsolute;
        }

        const outputDir = await vscode.window.showInputBox({
            prompt: 'Output directory for evaluation results (optional)',
            placeHolder: 'Example: evaluation (leave empty for default)',
            ignoreFocusOut: true
        });

        if (outputDir === undefined) {
            return;
        }

        const defaultOutputDir = 'evaluation';
        const trimmedOutput = outputDir.trim();
        const finalOutputDir = trimmedOutput.length > 0 ? trimmedOutput : defaultOutputDir;
        const resolvedOutputPath = path.isAbsolute(finalOutputDir)
            ? finalOutputDir
            : path.join(targetPath, finalOutputDir);

        let overwrite = false;
        if (fs.existsSync(resolvedOutputPath)) {
            const overwriteChoice = await vscode.window.showQuickPick<{ label: string; value: 'overwrite' | 'cancel'; description?: string }>(
                [
                    { label: 'Yes, overwrite', value: 'overwrite' },
                    { label: 'No', value: 'cancel' }
                ],
                {
                    title: `${finalOutputDir} already exists. Overwrite?`,
                    placeHolder: 'Choose "No" to keep the existing files.'
                }
            );

            if (!overwriteChoice || overwriteChoice.value === 'cancel') {
                return;
            }

            overwrite = overwriteChoice.value === 'overwrite';
        }

        const args = ['evaluate', 'experiment', experimentArg, '--config', configArg, '--output', finalOutputDir];
        if (overwrite) {
            args.push('--overwrite');
        }

        await this.cliManager.runCommand(args, project.path);
        this.resultsProvider?.refresh();
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
        void vscode.commands.executeCommand('fluxloop.integration.refresh');
    }

    private async generateInputs() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        const configInfo = await this.loadProjectConfig(project.path);
        const config = configInfo?.data;
        const defaultMode = this.getConfigMode(config);
        const strategiesFromConfig = this.getConfigStrategies(config);

        const mode = await this.promptForMode(defaultMode);
        if (mode === null) {
            return;
        }

        const baseSeed = this.getPrimaryBaseInput(config);
        const baseDecision = await this.confirmBaseInput(baseSeed);
        if (baseDecision === 'cancel') {
            return;
        }
        if (baseDecision === 'edit') {
            await vscode.commands.executeCommand('fluxloop.openInputConfig');
            return;
        }

        const strategies = await this.promptForStrategies(strategiesFromConfig);
        if (strategies === null) {
            return;
        }

        if (configInfo?.path) {
            try {
                this.writeVariationStrategies(configInfo.path, strategies);
                if (configInfo.data) {
                    configInfo.data.variation_strategies = [...strategies];
                }
            } catch (error) {
                console.error('Failed to persist variation strategies', error);
                void vscode.window.showWarningMessage(
                    'Selected variation strategies could not be written to configs/input.yaml. Continuing with the chosen values.'
                );
            }
        }

        const limit: string | undefined = undefined;

        const overwrite = await this.promptForBoolean('Overwrite existing outputs?', 'Only needed if the destination file already exists.');
        if (overwrite === null) {
            return;
        }

        const dryRun = false;

        const effectiveMode = mode ?? defaultMode;
        const llmApiKey = await this.resolveLlmApiKey(config, project.path, effectiveMode);
        if (llmApiKey === null) {
            return;
        }

        const args = ['generate', 'inputs'];

        if (mode) {
            args.push('--mode', mode);
        }

        if (strategies.length) {
            for (const strategy of strategies) {
                args.push('--strategy', strategy);
            }
        }

        if (limit) {
            args.push('--limit', limit);
        }

        if (overwrite) {
            args.push('--overwrite');
        }

        if (configInfo?.path) {
            args.push('--config', path.basename(configInfo.path));
        }

        if (llmApiKey) {
            args.push('--llm-api-key', llmApiKey);
        }

        await this.cliManager.runCommand(args, project.path);

            this.inputsProvider?.refresh();
            const outputFile = this.resolveOutputFile(project.path, config);
            if (outputFile && fs.existsSync(outputFile)) {
                const document = await vscode.workspace.openTextDocument(outputFile);
                await vscode.window.showTextDocument(document, { preview: false });
        }
    }

    private async showStatus() {
        const args = ['status', 'check', '--verbose'];
        await this.cliManager.runCommand(args, ProjectContext.getActiveWorkspacePath());
        void vscode.commands.executeCommand('fluxloop.integration.refresh');
    }

    private async openConfig(projectId?: string) {
        await this.openSimulationConfig(projectId);
    }

    private async openProjectConfig(projectId?: string) {
        await this.openConfigSection('project', projectId);
    }

    private async openProjectEnv(projectId?: string): Promise<void> {
        const project = projectId ? ProjectManager.getInstance().getProjectById(projectId) : ProjectContext.ensureActiveProject();
        if (!project) {
            if (projectId) {
                void vscode.window.showWarningMessage('Unable to find the selected project, so .env cannot be opened.');
            }
            return;
        }

        const envPath = path.join(project.path, '.env');
        const envUri = vscode.Uri.file(envPath);

        let exists = true;
        try {
            await vscode.workspace.fs.stat(envUri);
        } catch {
            exists = false;
        }

        if (!exists) {
            const choice = await vscode.window.showInformationMessage('No .env file found. Create one from the default template?', 'Create', 'Cancel');

            if (choice !== 'Create') {
                return;
            }

            try {
                await fs.promises.mkdir(path.dirname(envPath), { recursive: true });
                await fs.promises.writeFile(envPath, this.getDefaultEnvTemplate(), 'utf8');
            } catch (error) {
                void vscode.window.showErrorMessage('Failed to create the .env file. Check the output channel.');
                console.error('Failed to create .env file', error);
                return;
            }
        }

        try {
            const document = await vscode.workspace.openTextDocument(envUri);
            await vscode.window.showTextDocument(document, { preview: false });
        } catch (error) {
            void vscode.window.showErrorMessage('Unable to open the .env file. Check the output channel.');
            console.error('Failed to open .env file', error);
        }
    }

    private async openInputConfig(projectId?: string) {
        await this.openConfigSection('input', projectId);
    }

    private async openSimulationConfig(projectId?: string) {
        await this.openConfigSection('simulation', projectId);
    }

    private async openEvaluationConfig(projectId?: string) {
        await this.openConfigSection('evaluation', projectId);
    }

    private async enableRecording() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        await this.cliManager.runCommand(['record', 'enable'], project.path);
        void vscode.commands.executeCommand('fluxloop.integration.refresh');
    }

    private async disableRecording() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        await this.cliManager.runCommand(['record', 'disable'], project.path);
        void vscode.commands.executeCommand('fluxloop.integration.refresh');
    }

    private async showRecordingStatus() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        await this.cliManager.runCommand(['record', 'status'], project.path);
    }

    private async selectEnvironment() {
        const project = ProjectContext.getActiveProject();
        const targetInfo = this.resolveConfigurationTarget(project);
        const configuration = vscode.workspace.getConfiguration('fluxloop', targetInfo.uri);

        const executionMode = (configuration.get<string>('executionMode') as 'auto' | 'workspace' | 'global' | 'custom' | undefined) ?? 'auto';
        const pythonOverride = configuration.get<string>('pythonPath') ?? '';
        const mcpOverride = configuration.get<string>('mcpCommandPath') ?? '';

        const items: Array<vscode.QuickPickItem & { mode?: 'auto' | 'workspace' | 'global' | 'custom'; action?: 'custom' | 'clear' | 'folder' }> = [
            {
                label: 'Auto (detect project environment)',
                description: 'Use project .venv/uv/conda if available, otherwise fallback to PATH',
                picked: executionMode === 'auto',
                mode: 'auto'
            },
            {
                label: 'Workspace only',
                description: 'Require a virtual environment inside the project',
                picked: executionMode === 'workspace',
                mode: 'workspace'
            },
            {
                label: 'Choose environment folder…',
                description: 'Browse to a project virtual environment (updates target source root)',
                detail: project ? project.path : undefined,
                action: 'folder'
            },
            {
                label: 'Global PATH',
                description: 'Always use globally installed executables',
                picked: executionMode === 'global',
                mode: 'global'
            },
            {
                label: 'Custom executables…',
                description: 'Specify python and fluxloop-mcp paths manually',
                detail: this.formatOverrideSummary(pythonOverride, mcpOverride),
                action: 'custom'
            }
        ];

        if (pythonOverride || mcpOverride) {
            items.push({
                label: 'Clear custom overrides',
                description: 'Remove python/fluxloop-mcp overrides',
                action: 'clear'
            });
        }

        const selection = await vscode.window.showQuickPick(items, {
            title: 'FluxLoop Environment Configuration',
            placeHolder: 'Select execution mode or configure custom executables'
        });

        if (!selection) {
            return;
        }

        const target = targetInfo.target;

        if (selection.action === 'custom') {
            const pythonPath = await this.promptForExecutable(
                'Python executable path (absolute)',
                pythonOverride,
                { optional: true }
            );
            if (pythonPath === undefined) {
                return;
            }

            const mcpPath = await this.promptForExecutable(
                'fluxloop-mcp executable path (absolute, optional)',
                mcpOverride,
                { optional: true }
            );
            if (mcpPath === undefined) {
                return;
            }

            if (!pythonPath && !mcpPath) {
                void vscode.window.showWarningMessage('Provide at least one executable path when using custom mode.');
                return;
            }

            await configuration.update('executionMode', 'custom', target);
            await configuration.update('pythonPath', pythonPath || undefined, target);
            await configuration.update('mcpCommandPath', mcpPath || undefined, target);
            await configuration.update('defaultEnvironment', 'Local Python', target);
            vscode.window.showInformationMessage('Custom FluxLoop executables configured.');
            await this.environmentManager.refreshActiveEnvironment();
            return;
        }

        if (selection.action === 'folder') {
            await this.selectEnvironmentFolder(project, configuration, target);
            return;
        }

        if (selection.action === 'clear') {
            await configuration.update('pythonPath', undefined, target);
            await configuration.update('mcpCommandPath', undefined, target);
            if (executionMode === 'custom') {
                await configuration.update('executionMode', 'auto', target);
            }
            await configuration.update('defaultEnvironment', 'Local Python', target);
            vscode.window.showInformationMessage('FluxLoop environment overrides cleared.');
            await this.environmentManager.refreshActiveEnvironment();
            return;
        }

        if (selection.mode) {
            await configuration.update('executionMode', selection.mode, target);
            await configuration.update('defaultEnvironment', 'Local Python', target);
            vscode.window.showInformationMessage(`FluxLoop execution mode set to ${selection.mode}.`);
            await this.environmentManager.refreshActiveEnvironment();
        }
    }

    private formatOverrideSummary(pythonPath: string, mcpPath: string): string | undefined {
        const parts: string[] = [];
        if (pythonPath) {
            parts.push(`python: ${pythonPath}`);
        }
        if (mcpPath) {
            parts.push(`mcp: ${mcpPath}`);
        }
        return parts.length > 0 ? parts.join(' | ') : undefined;
    }

    private async promptForExecutable(
        prompt: string,
        initialValue: string,
        options: { optional?: boolean } = {}
    ): Promise<string | undefined> {
        const value = await vscode.window.showInputBox({
            prompt,
            value: initialValue,
            ignoreFocusOut: true,
            placeHolder: '/absolute/path/to/executable',
            validateInput: (input) => {
                const trimmed = input.trim();
                if (!trimmed) {
                    return options.optional ? null : null;
                }
                if (!path.isAbsolute(trimmed)) {
                    return 'Enter an absolute path.';
                }
                return null;
            }
        });

        if (value === undefined) {
            return undefined;
        }

        return value.trim();
    }

    private async selectEnvironmentFolder(
        project: ProjectEntry | undefined,
        configuration: vscode.WorkspaceConfiguration,
        target: vscode.ConfigurationTarget
    ): Promise<void> {
        const dialog = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: 'Use this folder',
            title: 'Select FluxLoop environment folder',
            defaultUri: project ? vscode.Uri.file(project.path) : undefined
        });

        if (!dialog || dialog.length === 0) {
            return;
        }

        const selectedPath = dialog[0].fsPath;
        const storedValue = this.computeTargetSourceRootValue(project?.path, selectedPath);

        await configuration.update('targetSourceRoot', storedValue, target);
        await configuration.update('executionMode', 'workspace', target);
        await configuration.update('defaultEnvironment', 'Local Python', target);
        await configuration.update('pythonPath', undefined, target);
        await configuration.update('mcpCommandPath', undefined, target);

        if (project) {
            const configPath = path.join(project.path, 'configs', 'project.yaml');
            if (fs.existsSync(configPath)) {
                this.writeSourceRoot(configPath, storedValue);
                ProjectManager.getInstance().refreshProjectById(project.id);
            }
        }

        const display = this.formatEnvironmentFolderDisplay(selectedPath, project?.path);
        vscode.window.showInformationMessage(`FluxLoop environment folder set to ${display}.`);
        await this.environmentManager.refreshActiveEnvironment();
    }

    private computeTargetSourceRootValue(projectPath: string | undefined, folderPath: string): string {
        const normalizedFolder = path.resolve(folderPath);
        if (!projectPath) {
            return normalizedFolder.replace(/\\/g, '/');
        }

        const normalizedProject = path.resolve(projectPath);
        if (normalizedFolder === normalizedProject) {
            return '.';
        }

        if (normalizedFolder.startsWith(`${normalizedProject}${path.sep}`)) {
            const relative = path.relative(normalizedProject, normalizedFolder);
            return relative ? relative.replace(/\\/g, '/') : '.';
        }

        return normalizedFolder.replace(/\\/g, '/');
    }

    private formatEnvironmentFolderDisplay(folderPath: string, projectPath?: string): string {
        if (!projectPath) {
            return folderPath;
        }

        const normalizedProject = path.resolve(projectPath);
        const normalizedFolder = path.resolve(folderPath);
        if (normalizedFolder === normalizedProject) {
            return projectPath;
        }

        if (normalizedFolder.startsWith(`${normalizedProject}${path.sep}`)) {
            const relative = path.relative(normalizedProject, normalizedFolder);
            return relative || '.';
        }

        return folderPath;
    }

    private resolveConfigurationTarget(project: ProjectEntry | undefined): { target: vscode.ConfigurationTarget; uri?: vscode.Uri } {
        if (project) {
            const workspaceFolder = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(project.path));
            if (workspaceFolder) {
                return { target: vscode.ConfigurationTarget.WorkspaceFolder, uri: workspaceFolder.uri };
            }
            return { target: vscode.ConfigurationTarget.Global, uri: undefined };
        }

        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            return { target: vscode.ConfigurationTarget.WorkspaceFolder, uri: workspaceFolders[0].uri };
        }

        return { target: vscode.ConfigurationTarget.Global, uri: undefined };
    }

    private async showEnvironmentInfo() {
        const environment = this.environmentManager.getActiveEnvironment();
        if (!environment) {
            const choice = await vscode.window.showInformationMessage(
                'FluxLoop environment has not been detected yet.',
                'Refresh'
            );
            if (choice === 'Refresh') {
                await this.environmentManager.refreshActiveEnvironment();
            }
            return;
        }

        const lines = [
            `Source root: ${environment.root}`,
            `Type: ${environment.environmentType}`,
            `Python: ${environment.pythonPath ?? 'not set'}`,
            `fluxloop: ${environment.fluxloopPath ?? 'not set'}`,
            `fluxloop-mcp: ${environment.fluxloopMcpPath ?? 'not set'}`
        ];

        if (environment.notes.length > 0) {
            lines.push('Notes:');
            environment.notes.forEach(note => lines.push(`- ${note}`));
        }

        const action = await vscode.window.showInformationMessage(
            lines.join('\n'),
            { modal: true },
            'Open Output',
            'Refresh'
        );

        if (action === 'Open Output') {
            OutputChannelManager.getInstance().show(true);
        } else if (action === 'Refresh') {
            await this.environmentManager.refreshActiveEnvironment();
        }
    }

    private async runDoctor() {
        await this.cliManager.runCommand(['doctor']);
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
                description: 'Run in Docker container (coming soon)',
                detail: 'Not supported yet',
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

        if (selected?.label === 'Docker') {
            void vscode.window.showInformationMessage('Docker execution will be supported later. Please choose Local Python or Dev Container.');
            return undefined;
        }

        return selected?.label;
    }

    private async setProjectSourceRoot(projectId?: string) {
        const projectManager = ProjectManager.getInstance();
        const project = projectId
            ? projectManager.getProjectById(projectId)
            : ProjectContext.ensureActiveProject();

        if (!project) {
            return;
        }

        const configPath = path.join(project.path, 'configs', 'project.yaml');
        if (!fs.existsSync(configPath)) {
            void vscode.window.showWarningMessage('configs/project.yaml not found, so the target source root cannot be set.');
            return;
        }

        const actions: vscode.QuickPickItem[] = [
            { label: 'Choose Folder…', description: 'Select new target source root directory' }
        ];

        if (project.sourceRoot) {
            actions.push({ label: 'Clear Target Source Root', description: 'Remove the current mapping' });
        }

        const action = await vscode.window.showQuickPick(actions, {
            placeHolder: 'Select what you want to do with the target source root',
            title: project.name
        });

        if (!action) {
            return;
        }

        if (action.label === 'Clear Target Source Root') {
            this.writeSourceRoot(configPath, '');
            projectManager.refreshProjectById(project.id);
            await this.handleSourceRootUpdate(`Target source root cleared for ${project.name}.`);
            return;
        }

        const dialogResult = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectMany: false,
            canSelectFolders: true,
            openLabel: 'Select',
            defaultUri: vscode.Uri.file(project.path),
            title: 'Select Target Source Root Folder'
        });

        if (!dialogResult || dialogResult.length === 0) {
            return;
        }

        const selectedPath = dialogResult[0].fsPath;
        const relative = path.relative(project.path, selectedPath);
        let storedValue: string;

        if (!relative || relative === '') {
            storedValue = '.';
        } else if (relative.startsWith('..')) {
            storedValue = selectedPath;
        } else {
            storedValue = relative;
        }

        storedValue = storedValue.replace(/\\/g, '/');

        this.writeSourceRoot(configPath, storedValue);
        projectManager.refreshProjectById(project.id);
        const displayValue = storedValue === '.' ? project.path : storedValue;
        await this.handleSourceRootUpdate(`Target source root set to ${displayValue} for ${project.name}.`);
    }

    private async handleSourceRootUpdate(summary: string): Promise<void> {
        const environment = await this.environmentManager.refreshActiveEnvironment();

        const lines = [summary];
        if (environment) {
            const details = [
                `Environment: ${environment.environmentType}`,
                `Python: ${environment.pythonPath ?? 'not detected'}`,
                `fluxloop: ${environment.fluxloopPath ?? 'not detected'}`,
                `fluxloop-mcp: ${environment.fluxloopMcpPath ?? 'not detected'}`
            ];
            lines.push(details.join(' | '));
        } else {
            lines.push('No FluxLoop environment detected for the current project.');
        }

        const actions: string[] = ['Select Environment'];
        if (environment) {
            actions.push('Show Environment Info');
        }
        actions.push('Run Doctor');

        const choice = await vscode.window.showInformationMessage(lines.join('\n'), ...actions);

        if (choice === 'Select Environment') {
            await this.selectEnvironment();
        } else if (choice === 'Show Environment Info') {
            await this.showEnvironmentInfo();
        } else if (choice === 'Run Doctor') {
            void vscode.commands.executeCommand('fluxloop.runDoctor');
        }
    }

    private async openProjectSourceRoot(projectId?: string) {
        const projectManager = ProjectManager.getInstance();
        const project = projectId
            ? projectManager.getProjectById(projectId)
            : ProjectContext.ensureActiveProject();

        if (!project) {
            return;
        }

        if (!project.sourceRoot) {
            void vscode.window.showInformationMessage('Target source root is not set.');
            return;
        }

        const resolvedPath = this.resolveSourceRoot(project.path, project.sourceRoot);

        if (!fs.existsSync(resolvedPath)) {
            void vscode.window.showWarningMessage(`Source root path does not exist: ${resolvedPath}`);
            return;
        }

        const targetUri = vscode.Uri.file(resolvedPath);

        try {
            await vscode.commands.executeCommand('revealFileInOS', targetUri);
        } catch (error) {
            console.warn('Failed to reveal source root path', error);
            void vscode.env.openExternal(targetUri);
        }
    }

    private writeSourceRoot(configPath: string, value: string): void {
        const normalizedValue = value.replace(/\\/g, '/');
        const newLine = `source_root: "${normalizedValue}"`;
        const raw = fs.readFileSync(configPath, 'utf8');

        let updated: string;
        if (/^source_root\s*:.*/m.test(raw)) {
            updated = raw.replace(/^source_root\s*:.*/m, newLine);
        } else if (/^name\s*:.*/m.test(raw)) {
            updated = raw.replace(/^name\s*:.*/m, match => `${match}\n${newLine}`);
        } else {
            updated = `${raw.trimEnd()}\n${newLine}\n`;
        }

        if (!updated.endsWith('\n')) {
            updated += '\n';
        }

        fs.writeFileSync(configPath, updated, 'utf8');
    }

    private resolveSourceRoot(projectPath: string, sourceRoot: string): string {
        if (!sourceRoot || sourceRoot === '.') {
            return projectPath;
        }

        if (path.isAbsolute(sourceRoot)) {
            return sourceRoot;
        }

        return path.resolve(projectPath, sourceRoot);
    }

    private async configureExecutionWrapper() {
        const config = vscode.workspace.getConfiguration('fluxloop');
        const currentWrapper = config.get<string>('executionWrapper') ?? '';

        const input = await vscode.window.showInputBox({
            title: 'Configure Execution Wrapper',
            prompt: 'Enter a command to prepend before running the FluxLoop CLI (e.g., uv run). Leave blank to disable.',
            value: currentWrapper,
            ignoreFocusOut: true,
            placeHolder: 'Example: uv run'
        });

        if (input === undefined) {
            return;
        }

        const trimmed = input.trim();
        try {
            await config.update('executionWrapper', trimmed, vscode.ConfigurationTarget.Workspace);
            const message = trimmed ? `Execution wrapper set to "${trimmed}".` : 'Execution wrapper cleared.';
            void vscode.window.showInformationMessage(message);
        } catch (error) {
            console.error('Failed to update execution wrapper', error);
            void vscode.window.showErrorMessage('Failed to configure execution wrapper.');
        }
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

    private async loadProjectConfig(projectPath: string): Promise<{ data?: Record<string, any>; path?: string } | undefined> {
        const configPath = path.join(projectPath, 'configs', 'input.yaml');
        if (!fs.existsSync(configPath)) {
            vscode.window.showWarningMessage('No configs/input.yaml found. Input generation will use defaults.');
            return undefined;
        }

        try {
            const raw = await fs.promises.readFile(configPath, 'utf8');
            const parsed = parseYaml(raw) as Record<string, any> | undefined;
            return { data: parsed, path: configPath };
        } catch (error) {
            console.error('Failed to parse input configuration', error);
            vscode.window.showWarningMessage('Unable to read configs/input.yaml. Input generation will use defaults.');
            return { path: configPath };
        }
    }

    private async loadEvaluationConfig(projectPath: string): Promise<{ data?: Record<string, any>; path?: string } | undefined> {
        const configPath = path.join(projectPath, 'configs', 'evaluation.yaml');
        if (!fs.existsSync(configPath)) {
            return undefined;
        }

        try {
            const raw = await fs.promises.readFile(configPath, 'utf8');
            const parsed = parseYaml(raw) as Record<string, any> | undefined;
            return { data: parsed, path: configPath };
        } catch (error) {
            console.error('Failed to parse evaluation configuration', error);
            vscode.window.showWarningMessage('Unable to read configs/evaluation.yaml. Evaluation will use defaults.');
            return { path: configPath };
        }
    }

    private async openConfigSection(
        section: 'project' | 'input' | 'simulation' | 'evaluation',
        projectId?: string
    ): Promise<void> {
        const project = projectId ? ProjectManager.getInstance().getProjectById(projectId) : ProjectContext.ensureActiveProject();
        if (!project) {
            if (projectId) {
                vscode.window.showWarningMessage('The selected project is no longer available.');
            }
            return;
        }

        const fileName = `${section}.yaml`;
        const configUri = vscode.Uri.joinPath(vscode.Uri.file(project.path), 'configs', fileName);

        try {
            await vscode.workspace.fs.stat(configUri);
        } catch {
            vscode.window.showErrorMessage(`No configs/${fileName} found`);
            return;
        }

        try {
            const document = await vscode.workspace.openTextDocument(configUri);
            await vscode.window.showTextDocument(document);
        } catch (error) {
            vscode.window.showErrorMessage(`Unable to open configs/${fileName}`);
            console.error('Failed to open config section', error);
        }
    }

    private getDefaultEnvTemplate(): string {
        return [
            '# FluxLoop Configuration',
            'FLUXLOOP_COLLECTOR_URL=http://localhost:8000',
            'FLUXLOOP_API_KEY=your-api-key-here',
            'FLUXLOOP_ENABLED=true',
            'FLUXLOOP_DEBUG=false',
            'FLUXLOOP_SAMPLE_RATE=1.0',
            '# Argument Recording (global toggle)',
            'FLUXLOOP_RECORD_ARGS=false',
            'FLUXLOOP_RECORDING_FILE=',
            '# Example: recordings/args_recording.jsonl (project-relative or absolute path)',
            '',
            '# Service Configuration',
            'FLUXLOOP_SERVICE_NAME=my-agent',
            'FLUXLOOP_ENVIRONMENT=development',
            '',
            '# LLM API Keys (if needed)',
            'OPENAI_API_KEY=',
            '# ANTHROPIC_API_KEY=',
            '',
            '# Other Configuration',
            '# Add your custom environment variables here'
        ].join('\n') + '\n';
    }

    private getConfigMode(config: Record<string, any> | undefined): string | undefined {
        const mode = config?.input_generation?.mode;
        if (typeof mode === 'string') {
            return mode.toLowerCase();
        }
        return undefined;
    }

    private getConfigStrategies(config: Record<string, any> | undefined): string[] {
        const primary = this.normalizeStrategyList(config?.variation_strategies);
        if (primary.length) {
            return primary;
        }
        return this.normalizeStrategyList(config?.input_generation?.strategies);
    }

    private normalizeStrategyList(source: unknown): string[] {
        if (!Array.isArray(source)) {
            return [];
        }
        return source
            .map((entry: any) => this.normalizeStrategyValue(typeof entry === 'string' ? entry : entry?.type))
            .filter((value): value is string => Boolean(value));
                }

    private normalizeStrategyValue(value: unknown): string | undefined {
        if (typeof value !== 'string') {
            return undefined;
        }
        const normalized = value.trim().toLowerCase().replace(/[\s-]+/g, '_');
        return VARIATION_STRATEGIES.includes(normalized as (typeof VARIATION_STRATEGIES)[number])
            ? normalized
            : undefined;
                }

    private getPrimaryBaseInput(config: Record<string, any> | undefined): BaseInputSeed | undefined {
        if (!config) {
                return undefined;
        }
        const candidates = Array.isArray(config.base_inputs)
            ? config.base_inputs
            : Array.isArray(config.input?.base_inputs)
                ? config.input.base_inputs
                : undefined;

        if (!candidates || !candidates.length) {
            return undefined;
        }

        const seed = candidates[0] ?? {};
        const value = typeof seed?.input === 'string' ? seed.input : '';
        const intent = typeof seed?.expected_intent === 'string' ? seed.expected_intent : undefined;

        if (!value.trim() && !intent) {
            return undefined;
        }

        return { value, intent };
    }

    private async confirmBaseInput(seed: BaseInputSeed | undefined): Promise<'confirm' | 'edit' | 'cancel'> {
        if (!seed || !seed.value?.trim()) {
            return 'confirm';
        }

        const trimmed = seed.value.trim();
        const preview = trimmed.length > 240 ? `${trimmed.slice(0, 240)}…` : trimmed;
        const lines = [
            'Use this base input as the seed for generation?',
            '',
            preview
        ];
        if (seed.intent) {
            lines.push('', `Intent: ${seed.intent}`);
        }

        const selection = await vscode.window.showInformationMessage(
            lines.join('\n'),
            { modal: true },
            'Use Seed',
            'Edit in configuration'
        );

        if (!selection) {
            return 'cancel';
        }

        return selection === 'Use Seed' ? 'confirm' : 'edit';
    }

    private extractEvaluationGoal(config: Record<string, any> | undefined): string | undefined {
        if (!config) {
            return undefined;
        }
        const goal = config.evaluation_goal;
        if (typeof goal === 'string') {
            return goal;
        }
        if (goal && typeof goal.text === 'string') {
            return goal.text;
        }
        return undefined;
    }

    private async confirmEvaluationGoal(goal: string | undefined): Promise<'confirm' | 'edit' | 'cancel'> {
        if (!goal || !goal.trim()) {
            return 'confirm';
        }

        const trimmed = goal.trim();
        const preview = trimmed.length > 320 ? `${trimmed.slice(0, 320)}…` : trimmed;
        const lines = ['Evaluate experiment with this goal?', '', preview];

        const selection = await vscode.window.showInformationMessage(
            lines.join('\n'),
            { modal: true },
            'Use Goal',
            'Edit in configuration'
        );

        if (!selection) {
            return 'cancel';
        }

        return selection === 'Use Goal' ? 'confirm' : 'edit';
    }

    private writeVariationStrategies(configPath: string, strategies: string[]): void {
        const normalized = strategies
            .map(strategy => this.normalizeStrategyValue(strategy))
            .filter((strategy): strategy is string => Boolean(strategy));

        const block = normalized.length
            ? ['variation_strategies:', ...normalized.map(strategy => `  - ${strategy}`)].join('\n')
            : 'variation_strategies: []';

        const raw = fs.readFileSync(configPath, 'utf8');
        const variationBlockPattern = /(^variation_strategies:[^\r\n]*(?:\r?\n(?:[ \t]*-.*|[ \t]*))*)(?=\r?\n\S|$)/m;
        let updated: string;

        if (variationBlockPattern.test(raw)) {
            updated = raw.replace(variationBlockPattern, block);
        } else {
            const suffix = raw.endsWith('\n') ? '' : '\n';
            updated = `${raw}${suffix}${block}\n`;
        }

        fs.writeFileSync(configPath, updated, 'utf8');
    }

    private async promptForMode(defaultMode?: string): Promise<string | undefined | null> {
        interface ModeItem extends vscode.QuickPickItem {
            value?: string;
        }

        const items: ModeItem[] = [
            {
                label: defaultMode ? `Use configuration default (${defaultMode})` : 'Use configuration default',
                description: 'Do not override mode from configs/input.yaml'
            },
            {
                label: 'Deterministic',
                description: 'Generate variations without using an LLM',
                value: 'deterministic'
            },
            {
                label: 'LLM',
                description: 'Generate variations using the configured LLM provider',
                value: 'llm'
            }
        ];

        const selected = await vscode.window.showQuickPick(items, {
            title: 'Input Generation Mode',
            placeHolder: 'Choose how new inputs should be generated'
        });

        if (!selected) {
            return null;
        }

        return selected.value;
    }

    private async promptForStrategies(defaultStrategies: string[]): Promise<string[] | null> {
        const canonicalDefaults = defaultStrategies
            .map(value => this.normalizeStrategyValue(value))
            .filter((value): value is string => Boolean(value));

        const available = canonicalDefaults.length
            ? Array.from(new Set([...canonicalDefaults, ...VARIATION_STRATEGIES]))
            : VARIATION_STRATEGIES;

        interface StrategyPick extends vscode.QuickPickItem {
            value: string;
        }

        const items: StrategyPick[] = available.map(strategy => ({
            label: strategy.replace(/_/g, ' '),
            detail: strategy,
            picked: canonicalDefaults.includes(strategy),
            value: strategy
        }));

        const selected = await vscode.window.showQuickPick(items, {
            canPickMany: true,
            title: 'Variation Strategies',
            placeHolder: 'Select strategies to override configuration (leave empty to use defaults)'
        });

        if (selected === undefined) {
            return null;
        }

        return selected.map(item => item.value);
    }

    private async promptForBoolean(title: string, detail: string): Promise<boolean | null> {
        const items: vscode.QuickPickItem[] = [
            {
                label: 'Yes',
                description: detail
            },
            {
                label: 'No'
            }
        ];

        const selected = await vscode.window.showQuickPick(items, {
            title,
            placeHolder: detail
        });

        if (!selected) {
            return null;
        }

        return selected.label === 'Yes';
    }

    private resolveOutputFile(projectPath: string, config: Record<string, any> | undefined): string | undefined {
        const configured = config?.inputs_file;
        const relativePath = typeof configured === 'string' && configured.trim().length > 0
            ? configured
            : 'inputs/generated.yaml';

        return path.isAbsolute(relativePath)
            ? relativePath
            : path.join(projectPath, relativePath);
    }

    private async resolveLlmApiKey(
        config: Record<string, any> | undefined,
        projectPath: string,
        mode?: string
    ): Promise<string | undefined | null> {
        const resolvedMode = (mode ?? this.getConfigMode(config))?.toLowerCase();
        const needsLlmKey = resolvedMode === 'llm';
        if (!needsLlmKey) {
            return undefined;
        }

        const configKey = this.getConfigLlmApiKey(config);
        if (configKey) {
            return configKey;
        }

        const envFileKey = await this.getEnvFileLlmApiKey(projectPath);
        if (envFileKey) {
            return envFileKey;
        }

        const storedKey = await this.context.secrets.get('fluxloop.llmApiKey');
        if (storedKey) {
            return storedKey;
        }

        const input = await vscode.window.showInputBox({
            prompt: 'Enter the LLM API key (e.g., OpenAI key)',
            placeHolder: 'sk-...',
            password: true,
            ignoreFocusOut: true
        });

        if (input === undefined) {
            return null;
        }

        const trimmed = input.trim();
        if (!trimmed) {
            vscode.window.showWarningMessage('LLM API key is empty, so LLM mode cannot be used.');
            return null;
        }

        const saveChoice = await vscode.window.showQuickPick(
            [
                { label: 'Save', description: 'Store in VS Code secrets and the project .env.', value: 'persist' },
                { label: 'Use once', description: 'Use only for this run.', value: 'ephemeral' }
            ],
            {
                title: 'LLM API key persistence'
            }
        );

        if (!saveChoice) {
            return null;
        }

        if (saveChoice.value === 'persist') {
            await this.context.secrets.store('fluxloop.llmApiKey', trimmed);
            await this.writeEnvFileLlmApiKey(projectPath, trimmed);
        }

        return trimmed;
    }

    private getConfigLlmApiKey(config: Record<string, any> | undefined): string | undefined {
        const key = config?.input_generation?.llm?.api_key;
        return typeof key === 'string' && key.trim().length > 0 ? key.trim() : undefined;
    }

    private async getEnvFileLlmApiKey(projectPath: string): Promise<string | undefined> {
        const envPath = path.join(projectPath, '.env');
        if (!fs.existsSync(envPath)) {
            return undefined;
        }

        try {
            const raw = await fs.promises.readFile(envPath, 'utf8');
            const lines = raw.replace(/\r\n/g, '\n').split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith('#')) {
                    continue;
                }
                const [key, ...rest] = trimmed.split('=');
                if (key === 'FLUXLOOP_LLM_API_KEY') {
                    const value = rest.join('=').trim();
                    return value.replace(/^['"]|['"]$/g, '') || undefined;
                }
            }
        } catch (error) {
            console.warn('Failed to read .env for LLM API key', error);
        }

        return undefined;
    }

    private async writeEnvFileLlmApiKey(projectPath: string, apiKey: string): Promise<void> {
        const envPath = path.join(projectPath, '.env');
        let content = '';

        if (fs.existsSync(envPath)) {
            try {
                content = await fs.promises.readFile(envPath, 'utf8');
            } catch (error) {
                console.warn('Failed to read existing .env file; creating new one.', error);
            }
        }

        const lines = content ? content.replace(/\r\n/g, '\n').split('\n') : [];
        let updated = false;

        for (let i = 0; i < lines.length; i += 1) {
            const line = lines[i];
            if (line.trim().startsWith('FLUXLOOP_LLM_API_KEY=')) {
                lines[i] = `FLUXLOOP_LLM_API_KEY=${apiKey}`;
                updated = true;
                break;
            }
        }

        if (!updated) {
            lines.push(`FLUXLOOP_LLM_API_KEY=${apiKey}`);
        }

        const output = lines.join('\n');

        try {
            await fs.promises.writeFile(envPath, output.endsWith('\n') ? output : `${output}\n`, 'utf8');
        } catch (error) {
            console.error('Failed to write LLM API key to .env file', error);
            vscode.window.showWarningMessage('Failed to write the LLM API key to .env. Please add it manually.');
        }
    }
}
