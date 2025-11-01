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

export class CommandManager {
    constructor(
        private context: vscode.ExtensionContext,
        private cliManager: CLIManager,
        private statusProvider?: StatusProvider,
        private inputsProvider?: InputsProvider
    ) {}

    registerCommands() {
        // Register all commands
        this.context.subscriptions.push(
            vscode.commands.registerCommand('fluxloop.init', () => this.initProject()),
            vscode.commands.registerCommand('fluxloop.runExperiment', () => this.runExperiment()),
            vscode.commands.registerCommand('fluxloop.runSingle', () => this.runSingle()),
            vscode.commands.registerCommand('fluxloop.generateInputs', () => this.generateInputs()),
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

        const fromRecording = await this.promptForRecording(project.path);
        if (fromRecording === undefined) {
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

        if (fromRecording) {
            args.push('--from-recording', fromRecording);
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

    private async loadProjectConfig(projectPath: string): Promise<{ data?: Record<string, any>; path?: string } | undefined> {
        const candidates = ['setting.yaml', 'setting.yml', 'fluxloop.yaml', 'fluxloop.yml'];
        for (const candidate of candidates) {
            const fullPath = path.join(projectPath, candidate);
            if (!fs.existsSync(fullPath)) {
                continue;
            }

            try {
                const raw = await fs.promises.readFile(fullPath, 'utf8');
                const parsed = parseYaml(raw) as Record<string, any> | undefined;
                return { data: parsed, path: fullPath };
            } catch (error) {
                console.error('Failed to parse project configuration', error);
                vscode.window.showWarningMessage('Unable to read setting.yaml. Input generation will use defaults.');
                return { path: fullPath };
            }
        }

        vscode.window.showWarningMessage('No setting.yaml found. Input generation will use defaults.');
        return undefined;
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
                description: 'Do not override mode from setting.yaml'
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
        const available = defaultStrategies.length
            ? Array.from(new Set([...defaultStrategies, 'rephrase', 'verbose', 'error_prone', 'concise']))
            : ['rephrase', 'verbose', 'error_prone', 'concise'];

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

    private async promptForRecording(projectPath: string): Promise<string | undefined | null> {
        const recordingsDir = path.join(projectPath, 'recordings');
        if (!fs.existsSync(recordingsDir)) {
            return '';
        }

        const useRecording = await this.promptForBoolean('Use recording as template?', 'Leverage a previous recording to seed generated inputs.');
        if (useRecording === null) {
            return undefined;
        }

        if (!useRecording) {
            return '';
        }

        const selection = await vscode.window.showOpenDialog({
            title: 'Select recording template',
            canSelectFolders: false,
            canSelectFiles: true,
            defaultUri: vscode.Uri.file(recordingsDir),
            filters: {
                Recordings: ['jsonl']
            }
        });

        if (!selection || selection.length === 0) {
            return undefined;
        }

        return selection[0].fsPath;
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
