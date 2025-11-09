import * as vscode from 'vscode';

export type IntegrationNodeType =
    | 'mcpConnection'
    | 'fluxAgent'
    | 'systemStatus'
    | 'recentSuggestions'
    | 'statusItem'
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

function getIconForState(state: StatusState): string {
    switch (state) {
        case 'ok':
            return '$(check)';
        case 'warn':
            return '$(warning)';
        case 'error':
            return '$(error)';
        default:
            return '$(question)';
    }
}

export class IntegrationItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly nodeType: IntegrationNodeType,
        options: {
            description?: string;
            command?: vscode.Command;
            tooltip?: string;
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
    }
}

export class IntegrationProvider implements vscode.TreeDataProvider<IntegrationItem> {
    private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
    private mcpState: RootMcpState = { state: 'unknown', message: 'Status pending' };
    private systemStatuses: SystemStatusItem[] = DEFAULT_SYSTEM_STATUSES;
    private suggestions: IntegrationSuggestion[] = [];

    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    setMcpConnection(state: StatusState, message?: string): void {
        this.mcpState = { state, message };
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

    addSuggestion(suggestion: Omit<IntegrationSuggestion, 'id' | 'timestamp'>): void {
        const entry: IntegrationSuggestion = {
            id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            query: suggestion.query,
            answer: suggestion.answer,
            filePath: suggestion.filePath,
            selection: suggestion.selection,
            workflow: suggestion.workflow,
            timestamp: Date.now(),
        };

        this.suggestions = [entry, ...this.suggestions].slice(0, MAX_SUGGESTIONS);
        this.refresh();
    }

    clearSuggestions(): void {
        this.suggestions = [];
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

    private getRootItems(): IntegrationItem[] {
        const mcpLabel = `${getIconForState(this.mcpState.state)} MCP Connection`;
        const fluxAgentLabel = '$(sparkle) Run Flux Agent';

        return [
            new IntegrationItem(mcpLabel, vscode.TreeItemCollapsibleState.None, 'mcpConnection', {
                description: this.mcpState.message,
                command: {
                    command: 'fluxloop.integration.connectMcp',
                    title: 'Connect MCP',
                },
            }),
            new IntegrationItem(fluxAgentLabel, vscode.TreeItemCollapsibleState.None, 'fluxAgent', {
                command: {
                    command: 'fluxloop.integration.runAgent',
                    title: 'Run Flux Agent',
                },
            }),
            new IntegrationItem('System Status', vscode.TreeItemCollapsibleState.Collapsed, 'systemStatus'),
            new IntegrationItem('Recent Suggestions', vscode.TreeItemCollapsibleState.Collapsed, 'recentSuggestions'),
        ];
    }

    private getSystemStatusItems(): IntegrationItem[] {
        return this.systemStatuses.map((status) => {
            const label = `${getIconForState(status.state)} ${status.label}`;
            return new IntegrationItem(label, vscode.TreeItemCollapsibleState.None, 'statusItem', {
                description: status.description,
            });
        });
    }

    private getRecentSuggestionItems(): IntegrationItem[] {
        if (!this.suggestions.length) {
            return [
                new IntegrationItem('No suggestions yet', vscode.TreeItemCollapsibleState.None, 'suggestionItem', {
                    description: undefined,
                }),
            ];
        }

        return this.suggestions.map((suggestion) => {
            const date = new Date(suggestion.timestamp);
            const label = `${date.toLocaleString()} • ${suggestion.query}`;
            const description = suggestion.filePath ? suggestion.filePath.split(/[\\/]/).pop() : undefined;
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
            });
        });
    }
}

