import { IntegrationPlannerBridge } from './integrationPlannerBridge';
import {
    ChatMessage,
    FluxAgentMode,
    IntegrationContextResponse,
    IntegrationContextSelection,
    ModeContextResponse,
    RagDocument,
    RagTopic,
} from './types';

interface PlannerOrchestratorDeps {
    integrationBridge: IntegrationPlannerBridge;
    fetchIntegrationContext: (selection: IntegrationContextSelection) => Promise<IntegrationContextResponse>;
    fetchBaseInputContext: (selection: IntegrationContextSelection) => Promise<ModeContextResponse>;
    fetchExperimentContext: (selection: IntegrationContextSelection) => Promise<ModeContextResponse>;
    fetchInsightContext: (selection: IntegrationContextSelection) => Promise<ModeContextResponse>;
    retrieveRagDocuments: (topics: RagTopic[]) => Promise<RagDocument[]>;
    callOpenAi: (model: string, messages: ChatMessage[], temperature?: number) => Promise<string>;
}

export interface PlannerRunRequest {
    mode: FluxAgentMode;
    contextSelection: IntegrationContextSelection;
    contextSummary: string;
    structureModel: string;
    suggestionModel: string;
}

export interface PlannerRunResult {
    mode: FluxAgentMode;
    suggestion: string;
    contextSummary: string;
    workflow?: Record<string, unknown>;
    structureReport?: Record<string, unknown>;
    ragDocuments?: RagDocument[];
    ragTopics?: RagTopic[];
    modeContext?: Record<string, unknown>;
    warnings?: string[];
}

export class PlannerOrchestrator {
    constructor(private readonly deps: PlannerOrchestratorDeps) {}

    async run(request: PlannerRunRequest): Promise<PlannerRunResult> {
        switch (request.mode) {
            case 'integration':
                return this.runIntegration(request);
            case 'baseInput':
                return this.runBaseInput(request);
            case 'experiment':
                return this.runExperiment(request);
            case 'insight':
                return this.runInsight(request);
            default:
                throw new Error(`Unsupported mode: ${request.mode}`);
        }
    }

    private async runIntegration(request: PlannerRunRequest): Promise<PlannerRunResult> {
        const context = await this.deps.fetchIntegrationContext(request.contextSelection);
        if (context.error) {
            throw new Error(context.error);
        }

        const structureMessages = this.deps.integrationBridge.buildStructureMessages(context);
        const structureRaw = await this.deps.callOpenAi(request.structureModel, structureMessages, 0.2);
        const structureReport = this.safeParseJson(structureRaw);

        const ragTopics = this.deps.integrationBridge.mergeRagTopics(context.rag_topics, structureReport);
        const ragDocuments = await this.fetchRagDocs(ragTopics);

        const suggestionPrompt = this.deps.integrationBridge.buildSuggestionPrompt(context.workflow);
        const suggestionMessages = this.deps.integrationBridge.buildSuggestionMessages(
            suggestionPrompt,
            structureReport,
            ragDocuments,
        );

        const suggestion = await this.deps.callOpenAi(request.suggestionModel, suggestionMessages, 0.35);

        return {
            mode: request.mode,
            suggestion,
            workflow: context.workflow,
            structureReport,
            ragDocuments,
            ragTopics,
            contextSummary: request.contextSummary,
            warnings: context.warnings,
        };
    }

    private async runBaseInput(request: PlannerRunRequest): Promise<PlannerRunResult> {
        return this.runSingleStageMode(
            request,
            () => this.deps.fetchBaseInputContext(request.contextSelection),
            (context, ragDocuments) => this.buildBaseInputMessages(request, context, ragDocuments),
        );
    }

    private async runExperiment(request: PlannerRunRequest): Promise<PlannerRunResult> {
        return this.runSingleStageMode(
            request,
            () => this.deps.fetchExperimentContext(request.contextSelection),
            (context, ragDocuments) => this.buildExperimentMessages(request, context, ragDocuments),
            0.35,
        );
    }

    private async runInsight(request: PlannerRunRequest): Promise<PlannerRunResult> {
        return this.runSingleStageMode(
            request,
            () => this.deps.fetchInsightContext(request.contextSelection),
            (context, ragDocuments) => this.buildInsightMessages(request, context, ragDocuments),
            0.2,
        );
    }

    private async runSingleStageMode(
        request: PlannerRunRequest,
        fetcher: () => Promise<ModeContextResponse>,
        promptBuilder: (context: ModeContextResponse, ragDocuments: RagDocument[]) => ChatMessage[],
        temperature = 0.3,
    ): Promise<PlannerRunResult> {
        const context = await fetcher();
        if (context.error) {
            throw new Error(context.error);
        }

        const ragTopics = context.rag_topics ?? [];
        const ragDocuments = await this.fetchRagDocs(ragTopics);

        const messages = promptBuilder(context, ragDocuments);
        const suggestion = await this.deps.callOpenAi(request.suggestionModel, messages, temperature);

        return {
            mode: request.mode,
            suggestion,
            ragDocuments,
            ragTopics,
            modeContext: context.data,
            contextSummary: request.contextSummary,
            warnings: context.warnings,
        };
    }

    private buildBaseInputMessages(
        request: PlannerRunRequest,
        context: ModeContextResponse,
        ragDocuments: RagDocument[],
    ): ChatMessage[] {
        const repoProfile = context.data['repo_profile'];
        const samples = context.data['input_samples'];
        const settings = context.data['service_settings'];

        const sections = [
            '## Repository Profile',
            this.stringify(repoProfile),
            '',
            '## Existing Input Samples',
            this.stringify(samples),
            '',
            '## Service Settings',
            this.stringify(settings),
            '',
            '## VS Code Selection Summary',
            request.contextSelection.summary,
        ];

        const ragSection = this.buildRagSection(ragDocuments);
        if (ragSection) {
            sections.push('', ragSection);
        }

        sections.push(
            '',
            'Create 2-3 Base Input proposals including:',
            '- Persona/goal summary',
            '- YAML snippet ready for inputs/generated.yaml',
            '- Recommended follow-up experiments',
            'Return Markdown with sections: Summary, Candidates, Next Steps.',
        );

        return [
            {
                role: 'system',
                content:
                    'You are FluxLoop Base Input Planner. Craft grounded base input candidates referencing existing samples and repo context.',
            },
            { role: 'user', content: sections.join('\n') },
        ];
    }

    private buildExperimentMessages(
        request: PlannerRunRequest,
        context: ModeContextResponse,
        ragDocuments: RagDocument[],
    ): ChatMessage[] {
        const repoProfile = context.data['repo_profile'];
        const runnerConfigs = context.data['runner_configs'];
        const experiments = context.data['recent_experiments'];
        const templates = context.data['simulation_templates'];

        const sections = [
            '## Repository Profile',
            this.stringify(repoProfile),
            '',
            '## Runner Configurations',
            this.stringify(runnerConfigs),
            '',
            '## Simulation Templates',
            this.stringify(templates),
            '',
            '## Recent Experiments',
            this.stringify(experiments),
            '',
            '## VS Code Selection Summary',
            request.contextSelection.summary,
        ];

        const ragSection = this.buildRagSection(ragDocuments);
        if (ragSection) {
            sections.push('', ragSection);
        }

        sections.push(
            '',
            'Produce a detailed experiment plan including:',
            '- Recommended updates to simulation.yaml (diff format if possible)',
            '- Multi-turn input suggestions referencing Base Inputs',
            '- Runner cautions / telemetry hooks',
            'Return Markdown with sections: Summary, Simulation Updates, Input Plan, Execution Checklist.',
        );

        return [
            {
                role: 'system',
                content:
                    'You are FluxLoop Experiment Designer. Create actionable simulation plans grounded in runner configs and experiment history.',
            },
            { role: 'user', content: sections.join('\n') },
        ];
    }

    private buildInsightMessages(
        request: PlannerRunRequest,
        context: ModeContextResponse,
        ragDocuments: RagDocument[],
    ): ChatMessage[] {
        const reports = context.data['reports'];
        const metrics = context.data['aggregated_metrics'];

        const sections = [
            '## Aggregated Metrics',
            this.stringify(metrics),
            '',
            '## Recent Reports',
            this.stringify(reports),
            '',
            '## VS Code Selection Summary',
            request.contextSelection.summary,
        ];

        const ragSection = this.buildRagSection(ragDocuments);
        if (ragSection) {
            sections.push('', ragSection);
        }

        sections.push(
            '',
            'Provide deep insight analysis including:',
            '- Key findings / anomalies across runs',
            '- Recommended follow-up experiments or code changes',
            '- Telemetry or instrumentation gaps',
            'Return Markdown with sections: Executive Summary, Detailed Findings, Recommendations.',
        );

        return [
            {
                role: 'system',
                content:
                    'You are FluxLoop Insight Analyst. Summarize evaluation results and suggest high-leverage changes.',
            },
            { role: 'user', content: sections.join('\n') },
        ];
    }

    private async fetchRagDocs(topics: RagTopic[]): Promise<RagDocument[]> {
        const validTopics = topics.filter((topic) => typeof topic?.query === 'string' && topic.query.trim() !== '');
        if (!validTopics.length) {
            return [];
        }
        return this.deps.retrieveRagDocuments(validTopics);
    }

    private buildRagSection(ragDocuments: RagDocument[]): string | undefined {
        if (!ragDocuments.length) {
            return undefined;
        }

        const formatted = ragDocuments
            .map((doc) => {
                const citation = doc.citation || doc.id || 'ref:unknown';
                const source = doc.path || doc.title || 'unknown source';
                const excerpt = (doc.excerpt || '').trim();
                return `- (${citation}) ${source}\n  ${excerpt}`;
            })
            .join('\n');

        return ['## RAG Documents', formatted].join('\n');
    }

    private stringify(value: unknown): string {
        try {
            return JSON.stringify(value ?? {}, null, 2);
        } catch {
            return String(value);
        }
    }

    private safeParseJson(content: string): Record<string, unknown> {
        const trimmed = content?.trim();
        try {
            const parsed = JSON.parse(trimmed);
            if (parsed && typeof parsed === 'object') {
                return parsed as Record<string, unknown>;
            }
        } catch {
            // ignore direct parse failure
        }

        const start = trimmed.indexOf('{');
        const end = trimmed.lastIndexOf('}');
        if (start !== -1 && end > start) {
            const candidate = trimmed.slice(start, end + 1);
            try {
                const parsed = JSON.parse(candidate);
                if (parsed && typeof parsed === 'object') {
                    return parsed as Record<string, unknown>;
                }
            } catch {
                // ignore
            }
        }

        return { raw: trimmed };
    }
}


