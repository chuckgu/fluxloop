import * as vscode from 'vscode';
import type { FluxAgentMode } from '../integration/planner/types';

export type IntegrationNodeType =
    | 'mcpConnection'
    | 'knowledgeSearch'
    | 'fluxAgent'
    | 'systemStatus'
    | 'recentSuggestions'
    | 'refreshStatus'
    | 'selectEnvironment'
    | 'showEnvironment'
    | 'runDoctor'
    | 'clearHistory'
    | 'statusItem'
    | 'suggestionPlaceholder'
    | 'suggestionItem';

export type StatusState = 'ok' | 'warn' | 'error' | 'unknown';

export interface SystemStatusItem {
    id: string;
    label: string;
    description?: string;
    state: StatusState;
}

export interface IntegrationSuggestion {
    id: string;
    query: string;
    answer?: string;
    timestamp: number;
    filePath?: string;
    selection?: string;
    workflow?: unknown;
    mode?: FluxAgentMode;
    modeContext?: unknown;
    warnings?: string[];
}

interface RootMcpState {
    state: StatusState;
    message?: string;
}

const DEFAULT_SYSTEM_STATUSES: SystemStatusItem[] = [
    { id: 'fluxloop-cli', label: 'FluxLoop CLI', state: 'unknown', description: 'Status pending' },
    { id: 'python', label: 'Python Environment', state: 'unknown', description: 'Status pending' },
    { id: 'fluxloop-mcp', label: 'fluxloop-mcp Package', state: 'unknown', description: 'Status pending' },
    { id: 'mcp-index', label: 'MCP Index', state: 'unknown', description: 'Status pending' },
];

const MAX_SUGGESTIONS = 5;
const SUGGESTION_DIRECTORY = ['.fluxloop', 'integration', 'suggestions'];

function getIconForState(state: StatusState): string {
    switch (state) {
        case 'ok':
            return 'check';
        case 'warn':
            return 'warning';
        case 'error':
            return 'error';
        default:
            return 'question';
    }
}

export class IntegrationItem extends vscode.TreeItem {
    readonly suggestion?: IntegrationSuggestion;

    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly nodeType: IntegrationNodeType,
        options: {
            description?: string;
            command?: vscode.Command;
            tooltip?: string;
            iconId?: string;
            iconColor?: vscode.ThemeColor;
            suggestion?: IntegrationSuggestion;
        } = {},
    ) {
        super(label, collapsibleState);
        this.contextValue = nodeType;

        if (options.description) {
            this.description = options.description;
        }

        if (options.command) {
            this.command = options.command;
        }

        if (options.tooltip) {
            this.tooltip = options.tooltip;
        }

        if (options.iconId) {
            this.iconPath = new vscode.ThemeIcon(options.iconId, options.iconColor);
        }

        if (options.suggestion) {
            this.suggestion = options.suggestion;
        }
    }
}

export class IntegrationProvider implements vscode.TreeDataProvider<IntegrationItem> {
    private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
    private mcpState: RootMcpState = { state: 'unknown', message: 'Status pending' };
    private systemStatuses: SystemStatusItem[] = DEFAULT_SYSTEM_STATUSES;
    private suggestions: IntegrationSuggestion[] = [];
    private suggestionFiles = new Map<string, vscode.Uri>();
    private storageRoot?: vscode.Uri;

    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    setMcpConnection(state: StatusState, message?: string): void {
        const normalizedMessage =
            message ??
            {
                ok: 'Ready',
                warn: 'Attention required',
                error: 'Unavailable',
                unknown: 'Status pending',
            }[state];

        this.mcpState = { state, message: normalizedMessage };
        this.refresh();
    }

    getSystemStatuses(): SystemStatusItem[] {
        return this.systemStatuses;
    }

    getMcpState(): RootMcpState {
        return this.mcpState;
    }

    setSystemStatuses(statuses: SystemStatusItem[]): void {
        if (!statuses.length) {
            this.systemStatuses = DEFAULT_SYSTEM_STATUSES;
        } else {
            this.systemStatuses = statuses;
        }
        this.refresh();
    }

    async addSuggestion(suggestion: Omit<IntegrationSuggestion, 'id' | 'timestamp'>): Promise<void> {
        const entry: IntegrationSuggestion = {
            id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            query: suggestion.query,
            answer: suggestion.answer,
            filePath: suggestion.filePath,
            selection: suggestion.selection,
            workflow: suggestion.workflow,
            mode: suggestion.mode,
            modeContext: suggestion.modeContext,
            warnings: suggestion.warnings,
            timestamp: Date.now(),
        };

        this.suggestions = [entry, ...this.suggestions];

        if (this.storageRoot) {
            await this.writeSuggestionFile(entry);
        }

        if (this.suggestions.length > MAX_SUGGESTIONS) {
            const removed = this.suggestions.splice(MAX_SUGGESTIONS);
            for (const stale of removed) {
                await this.deleteSuggestionFromDisk(stale.id);
            }
        }

        this.refresh();
    }

    async clearSuggestions(): Promise<void> {
        this.suggestions = [];

        for (const uri of this.suggestionFiles.values()) {
            try {
                await vscode.workspace.fs.delete(uri, { recursive: false, useTrash: false });
            } catch {
                // ignore deletion errors
            }
        }

        this.suggestionFiles.clear();

        if (this.storageRoot) {
            try {
                await vscode.workspace.fs.createDirectory(this.storageRoot);
            } catch {
                // ignore
            }
        }

        this.refresh();
    }

    getTreeItem(element: IntegrationItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: IntegrationItem): Thenable<IntegrationItem[]> {
        if (!element) {
            return Promise.resolve(this.getRootItems());
        }

        if (element.nodeType === 'systemStatus') {
            return Promise.resolve(this.getSystemStatusItems());
        }

        if (element.nodeType === 'recentSuggestions') {
            return Promise.resolve(this.getRecentSuggestionItems());
        }

        return Promise.resolve([]);
    }

    async setWorkspaceRoot(workspaceUri: vscode.Uri | undefined): Promise<void> {
        if (!workspaceUri) {
            this.storageRoot = undefined;
            this.suggestions = [];
            this.suggestionFiles.clear();
            this.refresh();
            return;
        }

        const [first, ...rest] = SUGGESTION_DIRECTORY;
        let suggestionsUri = vscode.Uri.joinPath(workspaceUri, first);
        for (const segment of rest) {
            suggestionsUri = vscode.Uri.joinPath(suggestionsUri, segment);
        }

        this.storageRoot = suggestionsUri;

        try {
            await vscode.workspace.fs.createDirectory(suggestionsUri);
        } catch {
            // ignore directory creation errors; subsequent operations will report failure
        }

        await this.loadSuggestionsFromDisk();
    }

    private getRootItems(): IntegrationItem[] {
        const rootItems: IntegrationItem[] = [];

        rootItems.push(
            new IntegrationItem('System Status', vscode.TreeItemCollapsibleState.Collapsed, 'systemStatus', {
                iconId: 'settings-gear',
            }),
        );

        rootItems.push(
            new IntegrationItem(
                'Search in Documents…',
                vscode.TreeItemCollapsibleState.None,
                'knowledgeSearch',
                {
                    command: {
                        command: 'fluxloop.integration.openKnowledgeSearch',
                        title: 'Search in Documents',
                    },
                    iconId: 'search',
                    tooltip: 'Search FluxLoop documentation using the MCP index',
                },
            ),
        );

        rootItems.push(
            new IntegrationItem('Run Flux Agent', vscode.TreeItemCollapsibleState.None, 'fluxAgent', {
                command: {
                    command: 'fluxloop.integration.runAgent',
                    title: 'Run Flux Agent',
                },
                iconId: 'debug-start',
                tooltip: 'Generate integration suggestions for the active file',
            }),
        );

        rootItems.push(
            new IntegrationItem('Recent Suggestions', vscode.TreeItemCollapsibleState.Collapsed, 'recentSuggestions', {
                iconId: 'history',
            }),
        );

        return rootItems;
    }

    private getSystemStatusItems(): IntegrationItem[] {
        const items = this.systemStatuses.map((status) => {
            return new IntegrationItem(status.label, vscode.TreeItemCollapsibleState.None, 'statusItem', {
                description: status.description,
                iconId: getIconForState(status.state),
            });
        });

        items.push(
            new IntegrationItem('Connect MCP', vscode.TreeItemCollapsibleState.None, 'mcpConnection', {
                description: this.mcpState.message,
                command: {
                    command: 'fluxloop.integration.connectMcp',
                    title: 'Connect MCP',
                },
                iconId: 'plug',
                tooltip: this.mcpState.message,
            }),
        );

        items.push(
            new IntegrationItem('Refresh Status', vscode.TreeItemCollapsibleState.None, 'refreshStatus', {
                command: {
                    command: 'fluxloop.integration.refresh',
                    title: 'Refresh Integration Status',
                },
                iconId: 'refresh',
                tooltip: 'Re-run environment diagnostics',
            }),
        );

        items.push(
            new IntegrationItem('Select Environment', vscode.TreeItemCollapsibleState.None, 'selectEnvironment', {
                command: {
                    command: 'fluxloop.selectEnvironment',
                    title: 'Select FluxLoop Environment',
                },
                iconId: 'settings-gear',
                tooltip: 'Choose execution mode or custom executables for FluxLoop',
            }),
        );

        items.push(
            new IntegrationItem('Show Environment', vscode.TreeItemCollapsibleState.None, 'showEnvironment', {
                command: {
                    command: 'fluxloop.showEnvironmentInfo',
                    title: 'Show Environment Info',
                },
                iconId: 'info',
                tooltip: 'Display details about the current FluxLoop environment',
            }),
        );

        items.push(
            new IntegrationItem('Run Doctor', vscode.TreeItemCollapsibleState.None, 'runDoctor', {
                command: {
                    command: 'fluxloop.runDoctor',
                    title: 'Run Environment Doctor',
                },
                iconId: 'pulse',
                tooltip: 'Collect detailed diagnostics for FluxLoop CLI and MCP',
            }),
        );

        return items;
    }

    private getRecentSuggestionItems(): IntegrationItem[] {
        const suggestionItems = this.suggestions.map((suggestion) => {
            const date = new Date(suggestion.timestamp);
            const label = `${date.toLocaleString()} • ${suggestion.query}`;
            const descriptionParts: string[] = [];
            if (suggestion.mode) {
                descriptionParts.push(suggestion.mode);
            }
            if (suggestion.filePath) {
                descriptionParts.push(suggestion.filePath.split(/[\\/]/).pop() ?? suggestion.filePath);
            }
            const description = descriptionParts.length ? descriptionParts.join(' • ') : undefined;
            const tooltip = suggestion.answer
                ? `${suggestion.answer.slice(0, 180)}${suggestion.answer.length > 180 ? '…' : ''}`
                : suggestion.query;

            return new IntegrationItem(label, vscode.TreeItemCollapsibleState.None, 'suggestionItem', {
                description,
                tooltip,
                command: {
                    command: 'fluxloop.integration.showSuggestion',
                    title: 'Show Suggestion Detail',
                    arguments: [suggestion],
                },
                suggestion,
            });
        });

        if (!suggestionItems.length) {
            suggestionItems.push(
                new IntegrationItem(
                    'No suggestions yet',
                    vscode.TreeItemCollapsibleState.None,
                    'suggestionPlaceholder',
                    {
                        description: undefined,
                        iconId: 'info',
                    },
                ),
            );
        }

        suggestionItems.push(
            new IntegrationItem('Clear Suggestion History', vscode.TreeItemCollapsibleState.None, 'clearHistory', {
                command: {
                    command: 'fluxloop.integration.clearHistory',
                    title: 'Clear Integration Suggestion History',
                },
                iconId: 'trash',
                tooltip: 'Remove all stored integration suggestions',
            }),
        );

        return suggestionItems;
    }

    async removeSuggestion(id: string): Promise<void> {
        this.suggestions = this.suggestions.filter((suggestion) => suggestion.id !== id);
        await this.deleteSuggestionFromDisk(id);
        this.refresh();
    }

    private async loadSuggestionsFromDisk(): Promise<void> {
        if (!this.storageRoot) {
            return;
        }

        let directoryEntries: [string, vscode.FileType][];

        try {
            directoryEntries = await vscode.workspace.fs.readDirectory(this.storageRoot);
        } catch {
            this.suggestions = [];
            this.suggestionFiles.clear();
            this.refresh();
            return;
        }

        const loaded: IntegrationSuggestion[] = [];
        const fileIndex = new Map<string, vscode.Uri>();

        for (const [name, type] of directoryEntries) {
            if (type !== vscode.FileType.File || !name.endsWith('.md')) {
                continue;
            }

            const fileUri = vscode.Uri.joinPath(this.storageRoot, name);

            try {
                const raw = await vscode.workspace.fs.readFile(fileUri);
                const content = Buffer.from(raw).toString('utf8');
                const parsed = this.parseSuggestionFile(content);
                if (!parsed) {
                    continue;
                }

                loaded.push(parsed);
                fileIndex.set(parsed.id, fileUri);
            } catch {
                // Ignore malformed files
                continue;
            }
        }

        loaded.sort((a, b) => b.timestamp - a.timestamp);

        const kept = loaded.slice(0, MAX_SUGGESTIONS);
        const removed = loaded.slice(MAX_SUGGESTIONS);

        for (const stale of removed) {
            const uri = fileIndex.get(stale.id);
            if (uri) {
                try {
                    await vscode.workspace.fs.delete(uri, { recursive: false, useTrash: false });
                } catch {
                    // ignore
                }
                fileIndex.delete(stale.id);
            }
        }

        const keptFiles = new Map<string, vscode.Uri>();
        for (const suggestion of kept) {
            const uri = fileIndex.get(suggestion.id);
            if (uri) {
                keptFiles.set(suggestion.id, uri);
            }
        }

        this.suggestions = kept;
        this.suggestionFiles = keptFiles;

        this.refresh();
    }

    private async writeSuggestionFile(suggestion: IntegrationSuggestion): Promise<void> {
        if (!this.storageRoot) {
            return;
        }

        try {
            await vscode.workspace.fs.createDirectory(this.storageRoot);
        } catch {
            // ignore
        }

        const existingUri = this.suggestionFiles.get(suggestion.id);
        let fileUri: vscode.Uri;

        if (existingUri) {
            fileUri = existingUri;
        } else {
            const slug = this.slugify(suggestion.query);
            let fileName = `${suggestion.timestamp}-${slug || 'suggestion'}.md`;
            fileUri = vscode.Uri.joinPath(this.storageRoot, fileName);
            let counter = 1;
            let needsCheck = true;

            while (needsCheck) {
                try {
                    await vscode.workspace.fs.stat(fileUri);
                    fileName = `${suggestion.timestamp}-${slug || 'suggestion'}-${counter}.md`;
                    fileUri = vscode.Uri.joinPath(this.storageRoot, fileName);
                    counter += 1;
                } catch {
                    needsCheck = false;
                }
            }
        }

        const metadata = {
            id: suggestion.id,
            query: suggestion.query,
            timestamp: suggestion.timestamp,
            filePath: suggestion.filePath ?? null,
            selection: suggestion.selection ?? null,
            workflow: suggestion.workflow ?? null,
            mode: suggestion.mode ?? null,
            modeContext: suggestion.modeContext ?? null,
            warnings: suggestion.warnings ?? null,
        };

        const content =
            `<!-- fluxloop-suggestion\n${JSON.stringify(metadata, null, 2)}\n-->\n\n` +
            `${suggestion.answer ?? ''}\n`;

        await vscode.workspace.fs.writeFile(fileUri, Buffer.from(content, 'utf8'));
        this.suggestionFiles.set(suggestion.id, fileUri);
    }

    private async deleteSuggestionFromDisk(id: string): Promise<void> {
        const uri = this.suggestionFiles.get(id);
        if (!uri) {
            return;
        }

        try {
            await vscode.workspace.fs.delete(uri, { recursive: false, useTrash: false });
        } catch {
            // ignore
        } finally {
            this.suggestionFiles.delete(id);
        }
    }

    private parseSuggestionFile(content: string): IntegrationSuggestion | undefined {
        const match = content.match(/<!--\s*fluxloop-suggestion\s*\n([\s\S]*?)\n-->\s*([\s\S]*)$/);
        if (!match) {
            return undefined;
        }

        let metadata: Partial<IntegrationSuggestion & { workflow: unknown }> = {};
        try {
            metadata = JSON.parse(match[1]);
        } catch {
            return undefined;
        }

        const answer = match[2]?.trim() ?? '';

        let workflowValue: unknown = undefined;
        if (metadata.workflow !== undefined && metadata.workflow !== null) {
            if (typeof metadata.workflow === 'string') {
                try {
                    workflowValue = JSON.parse(metadata.workflow);
                } catch {
                    workflowValue = metadata.workflow;
                }
            } else {
                workflowValue = metadata.workflow;
            }
        }

        const suggestion: IntegrationSuggestion = {
            id: typeof metadata.id === 'string' ? metadata.id : `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            query: typeof metadata.query === 'string' ? metadata.query : 'FluxLoop Integration Suggestion',
            timestamp: typeof metadata.timestamp === 'number' ? metadata.timestamp : Date.now(),
            answer,
            filePath: typeof metadata.filePath === 'string' ? metadata.filePath : undefined,
            selection: typeof metadata.selection === 'string' ? metadata.selection : undefined,
            workflow: workflowValue,
            mode: typeof metadata.mode === 'string' ? (metadata.mode as FluxAgentMode) : undefined,
            modeContext: metadata.modeContext ?? undefined,
            warnings: Array.isArray(metadata.warnings)
                ? metadata.warnings.filter((entry: unknown): entry is string => typeof entry === 'string')
                : undefined,
        };

        return suggestion;
    }

    private slugify(value: string): string {
        return value
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .slice(0, 48);
    }
}

