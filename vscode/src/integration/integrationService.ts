import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as os from 'os';
import * as path from 'path';
import { promises as fs } from 'fs';
import { CLIManager } from '../cli/cliManager';
import {
    IntegrationProvider,
    SystemStatusItem,
    StatusState,
    IntegrationSuggestion,
} from '../providers/integrationProvider';
import { OutputChannelManager } from '../utils/outputChannel';
import { ProjectContext } from '../project/projectContext';
import * as https from 'https';
import { IntegrationPanel } from './integrationPanel';
import { EnvironmentManager } from '../environment/environmentManager';
import { IntegrationPlannerBridge } from './planner/integrationPlannerBridge';
import { PlannerOrchestrator } from './planner/plannerOrchestrator';
import {
    ChatMessage,
    FluxAgentMode,
    IntegrationContextSelection,
    IntegrationContextResponse,
    ModeContextResponse,
    RagDocument,
    RagTopic,
} from './planner/types';

interface CommandResult {
    success: boolean;
    stdout: string;
    stderr: string;
}

const FLUX_AGENT_MODES: { id: FluxAgentMode; label: string; description: string }[] = [
    {
        id: 'integration',
        label: 'Integration',
        description: 'Generate code integration plans (structure + doc-driven suggestion).',
    },
    {
        id: 'baseInput',
        label: 'Base Input',
        description: 'Craft base input candidates referencing existing samples and repo signals.',
    },
    {
        id: 'experiment',
        label: 'Experiment',
        description: 'Design simulation.yaml updates and multi-turn experiment scenarios.',
    },
    {
        id: 'insight',
        label: 'Insight',
        description: 'Analyze evaluation logs to surface insights and recommendations.',
    },
];

export class IntegrationService {
    private readonly output = OutputChannelManager.getInstance();
    private readonly refreshLock = new Map<string, boolean>();
    private lastStatuses: SystemStatusItem[] = [];
    private readonly plannerBridge = new IntegrationPlannerBridge();

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly cliManager: CLIManager,
        private readonly integrationProvider: IntegrationProvider,
        private readonly environmentManager: EnvironmentManager,
    ) {}

    async refreshStatus(): Promise<void> {
        if (this.refreshLock.get('status')) {
            return;
        }

        this.refreshLock.set('status', true);
        try {
            await this.environmentManager.refreshActiveEnvironment();

            const statuses: SystemStatusItem[] = [];
            statuses.push(await this.checkFluxloopCli());
            statuses.push(await this.checkPython());
            statuses.push(await this.checkMcpPackage());
            statuses.push(await this.checkMcpIndex());

            this.lastStatuses = statuses;
            this.integrationProvider.setSystemStatuses(statuses);
        } finally {
            this.refreshLock.delete('status');
        }
    }

    async handleConnectMcp(): Promise<void> {
        await this.refreshStatus();

        const mcpStatus = this.lastStatuses.find((status) => status.id === 'fluxloop-mcp');
        if (mcpStatus?.state === 'ok') {
            vscode.window.showInformationMessage('fluxloop-mcp package is already installed.');
        } else {
            vscode.window
                .showWarningMessage(
                    'fluxloop-mcp package is missing. Run "pip install fluxloop-mcp" to install it.',
                    'View install instructions',
                )
                .then((selection) => {
                    if (selection === 'View install instructions') {
                        void vscode.env.openExternal(
                            vscode.Uri.parse('https://pypi.org/project/fluxloop-mcp/0.1.0/'),
                        );
                    }
                });
        }
    }

    async openKnowledgeSearch(): Promise<void> {
        const query = await vscode.window.showInputBox({
            prompt: 'Ask anything about the FluxLoop documentation.',
            placeHolder:
                'Examples: "How do I initialize the FluxLoop SDK in FastAPI?" · "Where do I configure MCP credentials?" · "What does the MCP index include?"',
        });

        if (!query) {
            return;
        }

        await this.refreshStatus();
        const mcpStatus = this.lastStatuses.find((status) => status.id === 'fluxloop-mcp');
        if (mcpStatus?.state !== 'ok') {
            vscode.window.showErrorMessage('fluxloop-mcp package is not installed. Install it before running a document search.');
            return;
        }

        this.output.show();
        this.output.appendLine('');
        this.output.appendLine('='.repeat(60));
        this.output.appendLine(`[Document Search] ${query}`);

        const workspacePath =
            ProjectContext.getActiveWorkspacePath() || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        const result = await this.runCommand('fluxloop-mcp', ['--once', '--query', query], workspacePath);

        if (result.success) {
            const answer = result.stdout.trim() || 'No response returned.';
            this.output.appendLine(answer);

            await this.integrationProvider.addSuggestion({
                query,
                answer,
            });
            vscode.window.showInformationMessage('MCP response written to the FluxLoop output channel.');
        } else {
            this.output.appendLine(result.stderr || 'Failed to retrieve MCP response.');
            vscode.window.showErrorMessage(
                'MCP query failed. Ensure the index is built or run "fluxloop-mcp --once --query" manually.',
            );
        }
    }

    async runFluxAgent(): Promise<void> {
        try {
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Flux Agent',
                    cancellable: false,
                },
                async (progress) => {
                    progress.report({ message: 'Refreshing environment status...' });
                    await this.refreshStatus();
                    const statuses = this.integrationProvider.getSystemStatuses();
                    const pythonStatus = statuses.find((status) => status.id === 'python');
                    const mcpStatus = statuses.find((status) => status.id === 'fluxloop-mcp');
                    if (pythonStatus?.state !== 'ok') {
                        throw new Error('Python environment is not available. Install python3 to continue.');
                    }
                    if (mcpStatus?.state !== 'ok') {
                        throw new Error('fluxloop-mcp package is not installed. Install it before running Flux Agent.');
                    }

                    const workspacePath =
                        ProjectContext.getActiveWorkspacePath() || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                    if (!workspacePath) {
                        throw new Error('Open a FluxLoop project workspace before running Flux Agent.');
                    }

                    const editor = vscode.window.activeTextEditor;
                    if (!editor) {
                        throw new Error('Open a file and place the cursor where you need guidance.');
                    }

                    const document = editor.document;
                    const selection = editor.selection;
                    const selectedText = selection && !selection.isEmpty ? document.getText(selection) : '';
                    const truncatedSelection = selectedText ? this.truncate(selectedText, 4000) : '';

                    this.output.show();
                    this.output.appendLine('');
                    this.output.appendLine('='.repeat(60));
                    this.output.appendLine('[Flux Agent] Running Flux Agent MCP pipeline...');

                    const integrationContext = await this.promptIntegrationContext(
                        workspacePath,
                        document,
                        selection,
                        truncatedSelection,
                    );
                    const mode = await this.promptAgentMode();
                    const modeLabel = this.getModeLabel(mode);
                    this.output.appendLine(`[Flux Agent] Context Scope Selected:`);
                    this.output.appendLine(integrationContext.summary);
                    this.output.appendLine(`[Flux Agent] Mode Selected: ${modeLabel}`);

                    const apiKey = await this.ensureOpenAIApiKey();
                    const config = vscode.workspace.getConfiguration('fluxloop');
                    const structureModel =
                        config.get<string>('fluxAgent.structureModel')?.trim() || 'gpt-5-turbo';
                    const suggestionModel =
                        config.get<string>('fluxAgent.suggestionModel')?.trim() || 'gpt-5.1-mini';

                    progress.report({ message: `Running ${modeLabel} planning flow...` });
                    const orchestrator = this.createPlannerOrchestrator(apiKey, workspacePath);
                    const runResult = await orchestrator.run({
                        mode,
                        contextSelection: integrationContext,
                        contextSummary: integrationContext.summary,
                        structureModel,
                        suggestionModel,
                    });
                    this.output.appendLine('[Flux Agent] Suggestion received.');

                    const workflowPayload = runResult.workflow
                        ? {
                              ...runResult.workflow,
                        contextSummary: integrationContext.summary,
                        planner: {
                                  structureReport: runResult.structureReport,
                                  ragDocuments: runResult.ragDocuments,
                                  ragTopics: runResult.ragTopics,
                        },
                          }
                        : undefined;

                    IntegrationPanel.render(this.context.extensionUri, {
                        filePath: document.uri.fsPath,
                        selection: truncatedSelection,
                        workflow: workflowPayload,
                        suggestion: runResult.suggestion,
                        contextSummary: integrationContext.summary,
                        mode,
                        modeContext: runResult.modeContext,
                        warnings: runResult.warnings,
                    });

                    await this.integrationProvider.addSuggestion({
                        query: `${modeLabel} suggestion for ${path.basename(document.uri.fsPath)}`,
                        answer: runResult.suggestion,
                        filePath: document.uri.fsPath,
                        selection: truncatedSelection,
                        workflow: workflowPayload,
                        mode,
                        modeContext: runResult.modeContext,
                        warnings: runResult.warnings,
                    });
                },
            );
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`Flux Agent failed: ${message}`);
            this.output.appendLine(`[Flux Agent] Error: ${message}`);
        }
    }

    showSuggestionDetail(suggestion: IntegrationSuggestion): void {
        if (suggestion.workflow || suggestion.filePath || suggestion.modeContext) {
            const contextSummary =
                suggestion.workflow && typeof suggestion.workflow === 'object'
                    ? (suggestion.workflow as { contextSummary?: string }).contextSummary
                    : undefined;

            IntegrationPanel.render(this.context.extensionUri, {
                filePath: suggestion.filePath ?? 'Unknown file',
                selection: suggestion.selection ?? '',
                workflow: suggestion.workflow,
                suggestion: suggestion.answer ?? 'No response stored.',
                contextSummary,
                mode: suggestion.mode,
                modeContext: suggestion.modeContext,
                warnings: suggestion.warnings,
            });
            return;
        }

        this.output.show(true);
        this.output.appendLine('');
        this.output.appendLine('='.repeat(60));
        this.output.appendLine(`[Suggestion Query] ${suggestion.query}`);
        this.output.appendLine('');
        this.output.appendLine('[Response]');
        this.output.appendLine(suggestion.answer ?? 'No response stored.');
    }

    private async checkFluxloopCli(): Promise<SystemStatusItem> {
        const installed = await this.cliManager.checkInstallation();
        const state: StatusState = installed ? 'ok' : 'warn';

        return {
            id: 'fluxloop-cli',
            label: 'FluxLoop CLI',
            state,
            description: installed ? 'Installed' : 'Install required (pip install fluxloop-cli)',
        };
    }

    private async checkPython(): Promise<SystemStatusItem> {
        const result = await this.runCommand('python3', ['--version']);
        if (result.success) {
            return {
                id: 'python',
            label: 'Python Environment',
                state: 'ok',
                description: result.stdout.trim(),
            };
        }

        return {
            id: 'python',
            label: 'Python Environment',
            state: 'warn',
            description: 'python3 command not found.',
        };
    }

    private async checkMcpPackage(): Promise<SystemStatusItem> {
        const result = await this.runCommand('fluxloop-mcp', ['--help']);
        const state: StatusState = result.success ? 'ok' : 'warn';
        const description = result.success
            ? 'fluxloop-mcp CLI detected.'
            : (result.stderr.trim() || 'fluxloop-mcp is not installed. Run "pip install fluxloop-mcp".');

        this.integrationProvider.setMcpConnection(state, description);

        return {
            id: 'fluxloop-mcp',
            label: 'fluxloop-mcp Package',
            state,
            description,
        };
    }

    private async checkMcpIndex(): Promise<SystemStatusItem> {
        const defaultPath = path.join(os.homedir(), '.fluxloop', 'mcp', 'index', 'dev');

        try {
            await fs.access(defaultPath);
            return {
                id: 'mcp-index',
                label: 'MCP 인덱스',
                state: 'ok',
                description: 'Default index located.',
            };
        } catch {
            return {
                id: 'mcp-index',
                label: 'MCP Index',
                state: 'warn',
                description: 'Index missing. Run scripts/rebuild_index.sh to build it.',
            };
        }
    }

    private async ensureOpenAIApiKey(): Promise<string> {
        const secretKey = await this.context.secrets.get('fluxloop.openaiApiKey');
        if (secretKey) {
            return secretKey;
        }

        const configKey = vscode.workspace.getConfiguration('fluxloop').get<string>('openaiApiKey')?.trim();
        if (configKey) {
            return configKey;
        }

        const entered = await vscode.window.showInputBox({
            prompt: 'Enter your OpenAI API key to run Flux Agent.',
            placeHolder: 'sk-...',
            password: true,
            ignoreFocusOut: true,
        });

        if (!entered) {
            throw new Error('OpenAI API key is required to run Flux Agent.');
        }

        const store = await vscode.window.showInformationMessage('Save this key to VS Code secret storage?', 'Save', 'Skip');
        if (store === 'Save') {
            await this.context.secrets.store('fluxloop.openaiApiKey', entered);
        }

        return entered;
    }

    private async requestOpenAiChatCompletion(
        apiKey: string,
        model: string,
        messages: ChatMessage[],
        temperature = 0.3,
    ): Promise<string> {
        const requestBody = JSON.stringify({
            model,
            messages,
            temperature,
        });

        return new Promise<string>((resolve, reject) => {
            const request = https.request(
                {
                    method: 'POST',
                    hostname: 'api.openai.com',
                    path: '/v1/chat/completions',
                    headers: {
                        'Content-Type': 'application/json',
                        'Content-Length': Buffer.byteLength(requestBody),
                        Authorization: `Bearer ${apiKey}`,
                    },
                },
                (response) => {
                    let data = '';
                    response.on('data', (chunk) => {
                        data += chunk.toString();
                    });
                    response.on('end', () => {
                        if (response.statusCode && response.statusCode >= 200 && response.statusCode < 300) {
                            try {
                                const parsed = JSON.parse(data);
                                const content =
                                    parsed.choices?.[0]?.message?.content ||
                                    parsed.choices?.[0]?.text ||
                                    'OpenAI response did not include content.';
                                resolve(content);
                            } catch (error) {
                                reject(new Error(`Failed to parse OpenAI response: ${String(error)}`));
                            }
                        } else {
                            reject(new Error(`OpenAI API error: ${response.statusCode} ${data}`));
                        }
                    });
                },
            );

            request.on('error', (error) => {
                reject(error);
            });

            request.write(requestBody);
            request.end();
        });
    }

    private async promptAgentMode(): Promise<FluxAgentMode> {
        const pick = await vscode.window.showQuickPick(
            FLUX_AGENT_MODES.map((mode) => ({
                label: mode.label,
                description: mode.description,
                mode: mode.id,
            })),
            {
                title: 'Select Flux Agent Mode',
                placeHolder: 'Choose the objective for this Flux Agent run',
            },
        );

        if (!pick) {
            throw new Error('Flux Agent cancelled by user.');
        }

        return pick.mode;
    }

    private getModeLabel(mode: FluxAgentMode): string {
        return FLUX_AGENT_MODES.find((entry) => entry.id === mode)?.label ?? mode;
    }

    private async promptIntegrationContext(
        workspacePath: string,
        document: vscode.TextDocument,
        selection: vscode.Selection,
        truncatedSelection: string,
    ): Promise<IntegrationContextSelection> {
        const workspaceFolders = vscode.workspace.workspaceFolders ?? [];
        let selectedWorkspace = workspacePath;

        if (workspaceFolders.length > 1) {
            const workspacePick = await vscode.window.showQuickPick(
                workspaceFolders.map((folder) => ({
                    label: folder.name,
                    description: folder.uri.fsPath,
                })),
                {
                    title: 'Select workspace for Flux Agent',
                    placeHolder: 'Choose the workspace that contains your FluxLoop project',
                },
            );

            if (!workspacePick) {
                throw new Error('Flux Agent cancelled by user.');
            }

            selectedWorkspace = workspacePick.description ?? workspacePath;
        }

        const editorPath = document.uri.fsPath;
        const relativeFilePath = path.relative(selectedWorkspace, editorPath) || path.basename(editorPath);
        const hasSelection = selection && !selection.isEmpty;

        const scopeChoices: vscode.QuickPickItem[] = [
            {
                label: '$(file-code) Active file',
                description: relativeFilePath,
                detail: 'Use the entire active file as context',
                picked: true,
            },
        ];

        if (hasSelection) {
            scopeChoices.push({
                label: '$(selection) Selection only',
                description: relativeFilePath,
                detail: 'Use only the highlighted text as context',
            });
        }

        scopeChoices.push(
            {
                label: '$(folder-opened) Pick folder…',
                description: 'Choose one or more folders to emphasize',
            },
            {
                label: '$(files) Pick files…',
                description: 'Choose one or more files to emphasize',
            },
        );

        const scopePick = await vscode.window.showQuickPick(scopeChoices, {
            title: 'Flux Agent context scope',
            placeHolder: 'Control which paths are prioritized for MCP analysis',
        });

        if (!scopePick) {
            throw new Error('Flux Agent cancelled by user.');
        }

        let scope: IntegrationContextSelection['scope'] = 'activeFile';
        let targets: string[] = [editorPath];

        if (scopePick.label.includes('Selection') && hasSelection) {
            scope = 'selection';
        } else if (scopePick.label.includes('folder')) {
            scope = 'folder';
            const folders = await vscode.window.showOpenDialog({
                canSelectFiles: false,
                canSelectFolders: true,
                canSelectMany: true,
                defaultUri: vscode.Uri.file(selectedWorkspace),
                openLabel: 'Select folders',
            });

            if (!folders || folders.length === 0) {
                throw new Error('No folders selected for Flux Agent context.');
            }

            targets = folders.map((uri) => uri.fsPath);
        } else if (scopePick.label.includes('files')) {
            scope = 'files';
            const files = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectFolders: false,
                canSelectMany: true,
                defaultUri: document.uri,
                openLabel: 'Select files',
            });

            if (!files || files.length === 0) {
                throw new Error('No files selected for Flux Agent context.');
            }

            targets = files.map((uri) => uri.fsPath);
        }

        const summaryLines = [
            `Workspace: ${selectedWorkspace}`,
            `Scope: ${scopePick.label
                .replace('$(file-code) ', '')
                .replace('$(selection) ', '')
                .replace('$(folder-opened) ', '')
                .replace('$(files) ', '')}`,
            'Targets:',
            ...targets.map((target) => ` • ${path.relative(selectedWorkspace, target) || target}`),
        ];

        return {
            workspacePath: selectedWorkspace,
            scope,
            targets,
            summary: summaryLines.join('\n'),
            selectionSnippet: scope === 'selection' ? truncatedSelection : undefined,
        };
    }

    private createPlannerOrchestrator(apiKey: string, workspacePath: string): PlannerOrchestrator {
        return new PlannerOrchestrator({
            integrationBridge: this.plannerBridge,
            fetchIntegrationContext: (selection) => this.fetchIntegrationContext(workspacePath, selection),
            fetchBaseInputContext: (selection) => this.fetchBaseInputContext(workspacePath, selection),
            fetchExperimentContext: (selection) => this.fetchExperimentContext(workspacePath, selection),
            fetchInsightContext: (selection) => this.fetchInsightContext(workspacePath, selection),
            retrieveRagDocuments: (topics) => this.retrieveRagDocuments(workspacePath, topics),
            callOpenAi: (model, messages, temperature) =>
                this.requestOpenAiChatCompletion(apiKey, model, messages, temperature),
        });
    }

    private async fetchIntegrationContext(
        root: string,
        context: IntegrationContextSelection,
    ): Promise<IntegrationContextResponse> {
        const raw = await this.invokeContextTool<Record<string, unknown>>(root, context, 'IntegrationContextTool');
        return raw as IntegrationContextResponse;
    }

    private async fetchBaseInputContext(root: string, context: IntegrationContextSelection): Promise<ModeContextResponse> {
        const raw = await this.invokeContextTool<Record<string, unknown>>(root, context, 'BaseInputContextTool', {
            limit: 5,
        });
        return {
            data: raw,
            rag_topics: (Array.isArray(raw['rag_topics']) ? (raw['rag_topics'] as RagTopic[]) : undefined) ?? [],
            warnings: this.normalizeWarnings(raw['warnings']),
            error: typeof raw['error'] === 'string' ? (raw['error'] as string) : undefined,
        };
    }

    private async fetchExperimentContext(
        root: string,
        context: IntegrationContextSelection,
    ): Promise<ModeContextResponse> {
        const raw = await this.invokeContextTool<Record<string, unknown>>(root, context, 'ExperimentContextTool', {
            limit: 5,
        });
        return {
            data: raw,
            rag_topics: (Array.isArray(raw['rag_topics']) ? (raw['rag_topics'] as RagTopic[]) : undefined) ?? [],
            warnings: this.normalizeWarnings(raw['warnings']),
            error: typeof raw['error'] === 'string' ? (raw['error'] as string) : undefined,
        };
    }

    private async fetchInsightContext(root: string, context: IntegrationContextSelection): Promise<ModeContextResponse> {
        const raw = await this.invokeContextTool<Record<string, unknown>>(root, context, 'InsightContextTool', {
            limit: 5,
        });
        return {
            data: raw,
            rag_topics: (Array.isArray(raw['rag_topics']) ? (raw['rag_topics'] as RagTopic[]) : undefined) ?? [],
            warnings: this.normalizeWarnings(raw['warnings']),
            error: typeof raw['error'] === 'string' ? (raw['error'] as string) : undefined,
        };
    }

    private async invokeContextTool<T extends Record<string, unknown>>(
        root: string,
        context: IntegrationContextSelection,
        toolName: string,
        extras?: Record<string, unknown>,
    ): Promise<T> {
        const payload = {
            root,
            context: {
                scope: context.scope,
                targets: context.targets,
                selectionSnippet: context.selectionSnippet,
            },
            ...(extras ?? {}),
        };

        const script = `
import json
import pathlib
import sys
from fluxloop_mcp.tools import ${toolName}

payload = ${JSON.stringify(payload)}
payload["root"] = pathlib.Path(payload["root"]).expanduser().resolve().as_posix()
ctx = payload.get("context") or {}
    targets = ctx.get("targets") or []
    resolved_targets = []
    for target in targets:
        target_path = pathlib.Path(target)
        if not target_path.is_absolute():
        target_path = pathlib.Path(payload["root"]) / target_path
        resolved_targets.append(target_path.resolve().as_posix())
    ctx["targets"] = resolved_targets

tool = ${toolName}()
result = tool.fetch(payload)
json.dump(result, sys.stdout)
`;

        const result = await this.runCommand('python3', ['-c', script], root);
        if (!result.success) {
            throw new Error(result.stderr || `Failed to execute ${toolName} via fluxloop-mcp.`);
        }

        try {
            return JSON.parse(result.stdout || '{}') as T;
        } catch (error) {
            throw new Error(`Unable to parse ${toolName} output: ${String(error)}`);
        }
    }

    private normalizeWarnings(value: unknown): string[] {
        if (Array.isArray(value)) {
            return value.filter((entry): entry is string => typeof entry === 'string' && entry.trim() !== '');
        }
        if (typeof value === 'string' && value.trim()) {
            return [value.trim()];
        }
        return [];
    }

    private async retrieveRagDocuments(root: string, topics: RagTopic[]): Promise<RagDocument[]> {
        const sanitizedTopics = topics
            .filter((topic) => typeof topic?.query === 'string' && topic.query.trim() !== '')
            .map((topic, index): RagTopic | undefined => {
                const query = typeof topic.query === 'string' ? topic.query.trim() : '';
                if (!query) {
                    return undefined;
                }
                return {
                id: topic.id || `topic_${index}`,
                    query,
                };
            })
            .filter((topic): topic is RagTopic => Boolean(topic?.query));

        if (sanitizedTopics.length === 0) {
            return [];
        }

        const script = `
import json
import sys
from fluxloop_mcp.tools import RagService

topics = json.loads(${JSON.stringify(JSON.stringify(sanitizedTopics))})
service = RagService()
docs = service.retrieve(topics)
json.dump(docs, sys.stdout)
`;

        const result = await this.runCommand('python3', ['-c', script], root);
        if (!result.success) {
            throw new Error(result.stderr || 'Failed to retrieve RAG documents via fluxloop-mcp.');
        }

        try {
            return JSON.parse(result.stdout || '[]') as RagDocument[];
        } catch (error) {
            this.output.appendLine(`[Flux Agent] Warning: Unable to parse RAG output (${String(error)})`);
            return [];
        }
    }


    private truncate(text: string, maxLength: number): string {
        if (text.length <= maxLength) {
            return text;
        }
        return `${text.slice(0, maxLength)}\n... [truncated]`;
    }

    private async runCommand(command: string, args: string[], cwd?: string): Promise<CommandResult> {
        const resolved = await this.environmentManager.resolveCommand(command);
        const display = [resolved.command, ...args].join(' ');
        this.output.appendLine(`[FluxLoop Integration] > ${display}`);

        return new Promise<CommandResult>((resolve) => {
            let stdout = '';
            let stderr = '';

            const child = spawn(resolved.command, args, {
                cwd,
                shell: process.platform === 'win32',
                env: resolved.env,
            });

            child.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            child.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            child.on('error', (error) => {
                resolve({
                    success: false,
                    stdout: '',
                    stderr: error.message,
                });
            });

            child.on('close', (code) => {
                resolve({
                    success: code === 0,
                    stdout,
                    stderr,
                });

                if (code === 0) {
                    this.output.appendLine(`[FluxLoop Integration] ✅ ${display}`);
                    if (stdout.trim()) {
                        this.output.appendLine(stdout.trim());
                    }
                } else {
                    this.output.appendLine(`[FluxLoop Integration] ❌ ${display}`);
                    if (stderr.trim()) {
                        this.output.appendLine(stderr.trim());
                    }
                }
            });
        });
    }
}

