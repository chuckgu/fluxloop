import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { parse as parseYaml } from 'yaml';
import { CLIManager } from '../cli/cliManager';
import { WireframeViewer } from '../wireframe/wireframeViewer';
import { InputGenerationWizard } from '../wireframe/inputGenerationWizard';
import { DialogsWireframe } from '../wireframe/dialogsWireframe';
import { WebviewsWireframe } from '../wireframe/webviewsWireframe';
import { InteractiveWireframe } from '../wireframe/interactiveWireframe';
import { ProjectContext } from '../project/projectContext';
import { ProjectManager } from '../project/projectManager';
import { StatusProvider } from '../providers/statusProvider';
import { InputsProvider } from '../providers/inputsProvider';
import { ResultsProvider } from '../providers/resultsProvider';

export class CommandManager {
    constructor(
        private context: vscode.ExtensionContext,
        private cliManager: CLIManager,
        private statusProvider?: StatusProvider,
        private inputsProvider?: InputsProvider,
        private resultsProvider?: ResultsProvider
    ) {}

    registerCommands() {
        // Register all commands
        this.context.subscriptions.push(
            vscode.commands.registerCommand('fluxloop.init', () => this.initProject()),
            vscode.commands.registerCommand('fluxloop.runExperiment', () => this.runExperiment()),
            vscode.commands.registerCommand('fluxloop.parseExperiment', (experimentPath?: string) => this.parseExperiment(experimentPath)),
            vscode.commands.registerCommand('fluxloop.runSingle', () => this.runSingle()),
            vscode.commands.registerCommand('fluxloop.generateInputs', () => this.generateInputs()),
            vscode.commands.registerCommand('fluxloop.showStatus', () => this.showStatus()),
            vscode.commands.registerCommand('fluxloop.enableRecording', () => this.enableRecording()),
            vscode.commands.registerCommand('fluxloop.disableRecording', () => this.disableRecording()),
            vscode.commands.registerCommand('fluxloop.showRecordingStatus', () => this.showRecordingStatus()),
            vscode.commands.registerCommand('fluxloop.openConfig', (projectId?: string) => this.openSimulationConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openProjectConfig', (projectId?: string) => this.openProjectConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openInputConfig', (projectId?: string) => this.openInputConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openSimulationConfig', (projectId?: string) => this.openSimulationConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.openEvaluationConfig', (projectId?: string) => this.openEvaluationConfig(projectId)),
            vscode.commands.registerCommand('fluxloop.selectEnvironment', () => this.selectEnvironment()),
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
        this.statusProvider?.refreshForEnvironment(environment);

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
        this.statusProvider?.refresh();
    }

    private async parseExperiment(experimentPath?: string) {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        const experimentsDir = path.join(project.path, 'experiments');
        if (!fs.existsSync(experimentsDir)) {
            void vscode.window.showWarningMessage('실험 결과 폴더가 없습니다. 먼저 실험을 실행해 주세요.');
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
                void vscode.window.showWarningMessage('파싱할 실험 결과가 없습니다.');
                return;
            }

            const pick = await vscode.window.showQuickPick(
                directories.map(name => ({
                    label: name,
                    description: path.join('experiments', name)
                })),
                {
                    title: '실험 결과 선택',
                    placeHolder: '파싱할 실험 결과 폴더를 선택하세요.'
                }
            );

            if (!pick) {
                return;
            }

            targetPath = path.join(experimentsDir, pick.label);
        }

        if (!targetPath || !fs.existsSync(targetPath)) {
            void vscode.window.showErrorMessage('선택한 실험 결과 폴더를 찾을 수 없습니다.');
            return;
        }

        const relativePath = path.relative(project.path, targetPath);
        const experimentArg = relativePath && !relativePath.startsWith('..') ? relativePath : targetPath;

        const outputDir = await vscode.window.showInputBox({
            prompt: '결과를 저장할 출력 디렉터리 (옵션)',
            placeHolder: '예: parsed_results (비워두면 기본값 사용)',
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
                    { label: '예, 덮어쓰겠습니다', value: 'overwrite' },
                    { label: '아니요', value: 'cancel' }
                ],
                {
                    title: `${finalOutputDir} 디렉터리가 이미 존재합니다. 덮어쓸까요?`,
                    placeHolder: '덮어쓰기를 원하지 않으면 "아니요"를 선택하세요.'
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
        this.statusProvider?.refresh();
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

        const strategies = await this.promptForStrategies(strategiesFromConfig);
        if (strategies === null) {
            return;
        }

        const limit = await vscode.window.showInputBox({
            prompt: 'Limit generated inputs (optional)',
            placeHolder: 'Leave blank to use configuration default',
            validateInput: (value) => {
                if (value && !/^[0-9]+$/.test(value)) {
                    return 'Limit must be a positive integer';
                }
                return null;
            }
        });
        if (limit === undefined) {
            return;
        }

        const overwrite = await this.promptForBoolean('Overwrite existing outputs?', 'Only needed if the destination file already exists.');
        if (overwrite === null) {
            return;
        }

        const dryRun = await this.promptForBoolean('Dry run?', 'Preview the generation without writing files.');
        if (dryRun === null) {
            return;
        }

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

        if (dryRun) {
            args.push('--dry-run');
        }

        if (configInfo?.path) {
            args.push('--config', path.basename(configInfo.path));
        }

        if (llmApiKey) {
            args.push('--llm-api-key', llmApiKey);
        }

        await this.cliManager.runCommand(args, project.path);

        if (!dryRun) {
            this.inputsProvider?.refresh();
            const outputFile = this.resolveOutputFile(project.path, config);
            if (outputFile && fs.existsSync(outputFile)) {
                const document = await vscode.workspace.openTextDocument(outputFile);
                await vscode.window.showTextDocument(document, { preview: false });
            }
        }
    }

    private async showStatus() {
        const args = ['status', 'check', '--verbose'];
        await this.cliManager.runCommand(args, ProjectContext.getActiveWorkspacePath());
        this.statusProvider?.refresh();
    }

    private async openConfig(projectId?: string) {
        await this.openSimulationConfig(projectId);
    }

    private async openProjectConfig(projectId?: string) {
        await this.openConfigSection('project', projectId);
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
        this.statusProvider?.refresh();
    }

    private async disableRecording() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        await this.cliManager.runCommand(['record', 'disable'], project.path);
        this.statusProvider?.refresh();
    }

    private async showRecordingStatus() {
        const project = ProjectContext.ensureActiveProject();
        if (!project) {
            return;
        }

        await this.cliManager.runCommand(['record', 'status'], project.path);
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
                description: 'Run in Docker container (coming soon)',
                detail: '현재는 지원되지 않습니다',
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
            void vscode.window.showInformationMessage('Docker 실행은 향후 지원 예정입니다. Local Python 또는 Dev Container를 선택해 주세요.');
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
            void vscode.window.showWarningMessage('configs/project.yaml 파일을 찾을 수 없어 대상 소스 루트를 설정할 수 없습니다.');
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
            void vscode.window.showInformationMessage(`Target source root cleared for ${project.name}.`);
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
        void vscode.window.showInformationMessage(`Target source root set to ${storedValue} for ${project.name}.`);
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
            title: 'Execution Wrapper 설정',
            prompt: 'FluxLoop CLI 실행 전에 붙일 명령을 입력하세요 (예: uv run). 비워두면 해제됩니다.',
            value: currentWrapper,
            ignoreFocusOut: true,
            placeHolder: '예: uv run'
        });

        if (input === undefined) {
            return;
        }

        const trimmed = input.trim();
        try {
            await config.update('executionWrapper', trimmed, vscode.ConfigurationTarget.Workspace);
            const message = trimmed
                ? `Execution Wrapper를 "${trimmed}"로 설정했습니다.`
                : 'Execution Wrapper를 빈 값으로 설정했습니다.';
            void vscode.window.showInformationMessage(message);
        } catch (error) {
            console.error('Failed to update execution wrapper', error);
            void vscode.window.showErrorMessage('Execution Wrapper 설정에 실패했습니다.');
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

    private getConfigMode(config: Record<string, any> | undefined): string | undefined {
        const mode = config?.input_generation?.mode;
        if (typeof mode === 'string') {
            return mode.toLowerCase();
        }
        return undefined;
    }

    private getConfigStrategies(config: Record<string, any> | undefined): string[] {
        const strategies = config?.input_generation?.strategies;
        if (!Array.isArray(strategies)) {
            return [];
        }
        return strategies
            .map((entry: any) => {
                if (typeof entry === 'string') {
                    return entry;
                }
                if (entry && typeof entry.type === 'string') {
                    return entry.type;
                }
                return undefined;
            })
            .filter((value): value is string => Boolean(value));
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
        const builtinStrategies = [
            'rephrase',
            'error_prone',
            'typo',
            'verbose',
            'concise',
            'persona_based',
            'adversarial',
            'multilingual',
            'custom'
        ];

        const available = defaultStrategies.length
            ? Array.from(new Set([...defaultStrategies, ...builtinStrategies]))
            : builtinStrategies;

        const items = available.map<vscode.QuickPickItem>(strategy => ({
            label: strategy,
            picked: defaultStrategies.includes(strategy)
        }));

        const selected = await vscode.window.showQuickPick(items, {
            canPickMany: true,
            title: 'Variation Strategies',
            placeHolder: 'Select strategies to override configuration (leave empty to use defaults)'
        });

        if (selected === undefined) {
            return null;
        }

        return selected.map(item => item.label);
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
            prompt: 'LLM API Key를 입력하세요 (예: OpenAI Key)',
            placeHolder: 'sk-...',
            password: true,
            ignoreFocusOut: true
        });

        if (input === undefined) {
            return null;
        }

        const trimmed = input.trim();
        if (!trimmed) {
            vscode.window.showWarningMessage('LLM API Key가 비어 있어 LLM 모드를 사용할 수 없습니다.');
            return null;
        }

        const saveChoice = await vscode.window.showQuickPick([
            { label: '저장', description: 'VS Code 시크릿과 프로젝트 .env에 저장합니다.', value: 'persist' },
            { label: '이번만 사용', description: '이번 실행에만 사용합니다.', value: 'ephemeral' }
        ], {
            title: 'LLM API Key 저장 여부'
        });

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
            vscode.window.showWarningMessage('.env 파일에 LLM API Key를 쓰는 데 실패했습니다. 수동으로 추가해 주세요.');
        }
    }
}
