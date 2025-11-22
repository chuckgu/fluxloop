export type FluxAgentMode = 'integration' | 'baseInput' | 'experiment' | 'insight';

export interface IntegrationContextSelection {
    workspacePath: string;
    scope: 'activeFile' | 'selection' | 'folder' | 'files';
    targets: string[];
    summary: string;
    selectionSnippet?: string;
}

export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

export interface PromptDefinition {
    system?: string;
    user?: string;
}

export interface SuggestionPromptDefinition extends PromptDefinition {
    user_template?: string;
    placeholders?: string[];
}

export interface RagTopic {
    id?: string;
    query?: string;
    reasons?: string[];
}

export interface RagDocument {
    id?: string;
    title?: string;
    path?: string;
    excerpt?: string;
    citation?: string;
    score?: number;
    topic?: string;
}

export interface IntegrationContextResponse {
    workflow?: Record<string, unknown>;
    repo_profile?: Record<string, unknown>;
    integration_context?: Record<string, unknown>;
    structure_context?: Record<string, unknown>;
    rag_topics?: RagTopic[];
    warnings?: string[];
    error?: string;
}

export interface ModeContextResponse {
    data: Record<string, unknown>;
    rag_topics?: RagTopic[];
    warnings?: string[];
    error?: string;
}


