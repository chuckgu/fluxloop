import {
    ChatMessage,
    IntegrationContextResponse,
    RagDocument,
    RagTopic,
    SuggestionPromptDefinition,
} from './types';

export class IntegrationPlannerBridge {
    buildStructureMessages(context: IntegrationContextResponse): ChatMessage[] {
        const repoProfile = context.repo_profile ?? {};
        const integrationContext = context.integration_context ?? {};
        const structureSignals = context.structure_context ?? {};

        const systemPrompt =
            'You are FluxLoop Structure Analyst. Determine the primary framework, key entrypoints, and missing information required to integrate FluxLoop SDK.';
        const userPrompt = [
            '## Repository Profile',
            this.stringify(repoProfile),
            '',
            '## Integration Context',
            this.stringify(integrationContext),
            '',
            '## Current Signals',
            this.stringify(structureSignals),
            '',
            'Respond with a concise JSON object containing:',
            '- primary_framework: string',
            '- confidence: number (0-1)',
            '- keywords: string[]',
            '- missing_info: string[]',
        ].join('\n');

        return [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt },
        ];
    }

    buildSuggestionPrompt(workflow?: Record<string, unknown>): SuggestionPromptDefinition {
        const editPlan = (workflow?.['edit_plan'] as Record<string, unknown>) ?? {};
        const validation = (workflow?.['validation'] as Record<string, unknown>) ?? {};

        return {
            system:
                'You are FluxLoop Integration Expert. Produce an actionable plan using the provided analysis, RAG documents, and edit templates. Cite supporting documents when available.',
            user_template: [
                '## Structure Analysis',
                '{structure_report}',
                '',
                '## RAG Documents (with citations)',
                '{rag_documents}',
                '',
                '## Proposed Edit Plan',
                this.stringify(editPlan),
                '',
                '## Validation Notes',
                this.stringify(validation),
                '',
                'Return Markdown with sections: Summary, Steps, Code Changes, Validation, References.',
            ].join('\n'),
            placeholders: ['structure_report', 'rag_documents'],
        };
    }

    buildSuggestionMessages(
        prompt: SuggestionPromptDefinition,
        structureReport: Record<string, unknown>,
        ragDocuments: RagDocument[],
    ): ChatMessage[] {
        const template =
            prompt.user_template ??
            [
                '## Structure Report',
                '{structure_report}',
                '',
                '## RAG Documents',
                '{rag_documents}',
                '',
                'Provide Markdown with Summary, Steps, Code Changes, Validation, References.',
            ].join('\n');

        const replacements: Record<string, string> = {
            structure_report: this.stringify(structureReport),
            rag_documents: this.formatRagDocuments(ragDocuments),
        };

        const userContent = Object.entries(replacements).reduce((content, [key, value]) => {
            const pattern = new RegExp(`\\{${key}\\}`, 'g');
            return content.replace(pattern, value);
        }, template);

        return [
            { role: 'system', content: prompt.system ?? 'You are FluxLoop Integration Expert.' },
            { role: 'user', content: userContent },
        ];
    }

    mergeRagTopics(baseTopics: RagTopic[] | undefined, structureReport: Record<string, unknown>): RagTopic[] {
        const sanitizedBase: RagTopic[] = (Array.isArray(baseTopics) ? baseTopics : [])
            .filter((topic) => typeof topic?.query === 'string' && topic.query.trim() !== '')
            .map((topic, index) => ({
                id: topic.id || `topic_${index}`,
                query: topic.query?.trim(),
                reasons: topic.reasons,
            }));

        const existing = new Set(sanitizedBase.map((topic) => topic.query));

        for (const additional of this.buildKeywordTopics(structureReport)) {
            if (additional.query && !existing.has(additional.query)) {
                sanitizedBase.push(additional);
                existing.add(additional.query);
            }
        }

        return sanitizedBase;
    }

    private buildKeywordTopics(structureReport: Record<string, unknown>): RagTopic[] {
        const keywords = Array.isArray(structureReport['keywords']) ? structureReport['keywords'] : [];
        return keywords
            .map((keyword, index): RagTopic | undefined => {
                if (typeof keyword !== 'string') {
                    return undefined;
                }
                const query = keyword.trim();
                if (!query) {
                    return undefined;
                }
                return {
                    id: `llm_kw_${index}`,
                    query,
                    reasons: ['structure_keyword'],
                };
            })
            .filter((topic): topic is RagTopic => Boolean(topic?.query));
    }

    private formatRagDocuments(documents: RagDocument[]): string {
        if (!documents.length) {
            return 'No supporting documents retrieved.';
        }

        return documents
            .map((doc) => {
                const citation = doc.citation || doc.id || 'ref:unknown';
                const source = doc.path || doc.title || 'unknown source';
                const excerpt = (doc.excerpt || '').trim();
                return `- (${citation}) ${source}\n  ${excerpt}`;
            })
            .join('\n');
    }

    private stringify(value: unknown): string {
        try {
            return JSON.stringify(value ?? {}, null, 2);
        } catch {
            return String(value);
        }
    }
}


