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

interface CommandResult {
    success: boolean;
    stdout: string;
    stderr: string;
}

export class IntegrationService {
    private readonly output = OutputChannelManager.getInstance();
    private readonly refreshLock = new Map<string, boolean>();
    private lastStatuses: SystemStatusItem[] = [];

    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly cliManager: CLIManager,
        private readonly integrationProvider: IntegrationProvider,
    ) {}

    async refreshStatus(): Promise<void> {
        if (this.refreshLock.get('status')) {
            return;
        }

        this.refreshLock.set('status', true);
        try {
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
            prompt: 'Enter a question for the FluxLoop documentation.',
            placeHolder: 'Example: How do I initialize the FluxLoop SDK in FastAPI?',
        });

        if (!query) {
            return;
        }

        await this.refreshStatus();
        const mcpStatus = this.lastStatuses.find((status) => status.id === 'fluxloop-mcp');
        if (mcpStatus?.state !== 'ok') {
            vscode.window.showErrorMessage('fluxloop-mcp package is not installed. Install it before running a knowledge search.');
            return;
        }

        this.output.show();
        this.output.appendLine('');
        this.output.appendLine('='.repeat(60));
        this.output.appendLine(`[MCP FAQ] ${query}`);

        const workspacePath =
            ProjectContext.getActiveWorkspacePath() || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        const result = await this.runCommand('fluxloop-mcp', ['--once', '--query', query], workspacePath);

        if (result.success) {
            const answer = result.stdout.trim() || 'No response returned.';
            this.output.appendLine(answer);

            this.integrationProvider.addSuggestion({
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
                    const fullText = document.getText();
                    const truncatedContent = this.truncate(fullText, 4000);
                    const truncatedSelection = selectedText ? this.truncate(selectedText, 4000) : '';

                    this.output.show();
                    this.output.appendLine('');
                    this.output.appendLine('='.repeat(60));
                    this.output.appendLine('[Flux Agent] Running integration workflow...');

                    progress.report({ message: 'Analyzing repository...' });
                    const workflowResult = await this.runIntegrationWorkflow(workspacePath);
                    this.output.appendLine('[Flux Agent] Workflow result received.');

                    const apiKey = await this.ensureOpenAIApiKey();
                    const model =
                        vscode.workspace.getConfiguration('fluxloop').get<string>('openaiModel') || 'gpt-4o-mini';

                    const prompt = this.composePrompt({
                        workspacePath,
                        filePath: document.uri.fsPath,
                        content: truncatedContent,
                        selection: truncatedSelection,
                        workflow: workflowResult,
                    });

                    progress.report({ message: 'Generating recommendation...' });
                    this.output.appendLine('[Flux Agent] Requesting suggestion from OpenAI...');
                    const suggestion = await this.requestOpenAiCompletion(apiKey, model, prompt);
                    this.output.appendLine('[Flux Agent] Suggestion received.');

                    IntegrationPanel.render(this.context.extensionUri, {
                        filePath: document.uri.fsPath,
                        selection: truncatedSelection,
                        workflow: workflowResult,
                        suggestion,
                    });

                    this.integrationProvider.addSuggestion({
                        query: `Integration suggestion for ${path.basename(document.uri.fsPath)}`,
                        answer: suggestion,
                        filePath: document.uri.fsPath,
                        selection: truncatedSelection,
                        workflow: workflowResult,
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
        if (suggestion.workflow || suggestion.filePath) {
            IntegrationPanel.render(this.context.extensionUri, {
                filePath: suggestion.filePath ?? 'Unknown file',
                selection: suggestion.selection ?? '',
                workflow: suggestion.workflow ?? {},
                suggestion: suggestion.answer ?? 'No response stored.',
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
        const result = await this.runCommand('fluxloop-mcp', ['--version']);
        const state: StatusState = result.success ? 'ok' : 'warn';
        const description = result.success
            ? result.stdout.trim()
            : 'fluxloop-mcp is not installed. Run "pip install fluxloop-mcp".';

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

    private composePrompt(input: {
        workspacePath: string;
        filePath: string;
        content: string;
        selection: string;
        workflow: unknown;
    }): string {
        const relativePath = path.relative(input.workspacePath, input.filePath);
        return [
            'You are Flux Agent, an assistant that helps developers integrate FluxLoop SDK into repositories.',
            'Use the provided repository analysis and edit plan to craft actionable, step-by-step guidance.',
            '',
            `Active file: ${relativePath}`,
            '',
            input.selection
                ? `Selected code snippet:\n${input.selection}\n`
                : 'No explicit selection was provided. Focus on the entire file context.',
            '',
            'File excerpt (truncated):',
            input.content,
            '',
            'Integration workflow result (JSON):',
            JSON.stringify(input.workflow, null, 2),
            '',
            'Instructions:',
            '- Provide a concise summary (less than 5 sentences).',
            '- Outline the recommended changes as ordered steps.',
            '- Highlight any critical checks or testing commands.',
            '- Include relevant files or anchors mentioned in the plan.',
            '- Use Markdown formatting (## headings, bullet lists, code blocks).',
        ].join('\n');
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

    private async requestOpenAiCompletion(apiKey: string, model: string, prompt: string): Promise<string> {
        const requestBody = JSON.stringify({
            model,
            messages: [
                { role: 'system', content: 'You are Flux Agent, an expert developer advocate for FluxLoop SDK.' },
                { role: 'user', content: prompt },
            ],
            temperature: 0.3,
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

    private async runIntegrationWorkflow(root: string): Promise<unknown> {
        const script = `
import json
import pathlib
import sys
from fluxloop_mcp.tools import RunIntegrationWorkflowTool

root_path = pathlib.Path(${JSON.stringify(root)}).resolve()
result = RunIntegrationWorkflowTool().run({"root": root_path.as_posix()})
json.dump(result, sys.stdout)
`;

        const result = await this.runCommand('python3', ['-c', script], root);
        if (!result.success) {
            throw new Error(result.stderr || 'Failed to execute integration workflow via fluxloop-mcp.');
        }

        try {
            return JSON.parse(result.stdout);
        } catch (error) {
            throw new Error(`Unable to parse workflow output: ${String(error)}`);
        }
    }

    private truncate(text: string, maxLength: number): string {
        if (text.length <= maxLength) {
            return text;
        }
        return `${text.slice(0, maxLength)}\n... [truncated]`;
    }

    private async runCommand(command: string, args: string[], cwd?: string): Promise<CommandResult> {
        return new Promise<CommandResult>((resolve) => {
            let stdout = '';
            let stderr = '';

            const child = spawn(command, args, {
                cwd,
                shell: process.platform === 'win32',
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
            });
        });
    }
}

