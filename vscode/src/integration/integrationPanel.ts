import * as vscode from 'vscode';
import { FluxAgentMode } from './planner/types';

interface IntegrationPanelData {
    filePath: string;
    selection: string;
    workflow?: unknown;
    suggestion: string;
    contextSummary?: string;
    mode?: FluxAgentMode;
    modeContext?: unknown;
    warnings?: string[];
    caution?: string;
}

export class IntegrationPanel {
    private static panel: vscode.WebviewPanel | undefined;

    static render(extensionUri: vscode.Uri, data: IntegrationPanelData): void {
        if (IntegrationPanel.panel) {
            IntegrationPanel.panel.reveal(IntegrationPanel.panel.viewColumn);
            IntegrationPanel.panel.webview.html = this.buildHtml(IntegrationPanel.panel.webview, extensionUri, data);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'fluxloop.integrationPanel',
            'Flux Agent Suggestion',
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
            },
        );

        panel.onDidDispose(() => {
            IntegrationPanel.panel = undefined;
        });

        panel.webview.html = this.buildHtml(panel.webview, extensionUri, data);
        IntegrationPanel.panel = panel;
    }

    private static buildHtml(webview: vscode.Webview, extensionUri: vscode.Uri, data: IntegrationPanelData): string {
        const safeSelection = data.selection ? this.escapeHtml(data.selection) : 'N/A';
        const workflowJson = data.workflow ? this.escapeHtml(JSON.stringify(data.workflow, null, 2)) : undefined;
        const modeContextJson = data.modeContext
            ? this.escapeHtml(JSON.stringify(data.modeContext, null, 2))
            : undefined;
        const suggestionMarkdown = this.escapeHtml(data.suggestion);
        const fileName = this.escapeHtml(data.filePath);
        const contextSummary = data.contextSummary ? this.escapeHtml(data.contextSummary) : undefined;
        const modeLabel = data.mode ? `${data.mode.charAt(0).toUpperCase()}${data.mode.slice(1)}` : undefined;
        const warnings =
            data.warnings && data.warnings.length
                ? data.warnings.map((warning) => `<li>${this.escapeHtml(warning)}</li>`).join('')
                : undefined;

        return `
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src ${webview.cspSource};" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
            body {
                font-family: var(--vscode-font-family);
                color: var(--vscode-foreground);
                background-color: var(--vscode-editor-background);
                padding: 16px;
                line-height: 1.6;
            }
            pre {
                background-color: var(--vscode-editor-inactiveSelectionBackground, rgba(125,125,125,0.1));
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
                font-family: var(--vscode-editor-font-family);
            }
            h1, h2, h3 {
                border-bottom: 1px solid var(--vscode-editor-foreground, rgba(255,255,255,0.18));
                padding-bottom: 4px;
            }
            section {
                margin-bottom: 24px;
            }
            code {
                font-family: var(--vscode-editor-font-family);
            }
            .label {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        ${data.caution ? `<div class="caution">${this.escapeHtml(data.caution)}</div>` : ''}
        <h1>Flux Agent Suggestion</h1>
        <section>
            <div class="label">Target File</div>
            <pre>${fileName}</pre>
        </section>
        ${modeLabel ? `<section>
            <div class="label">Mode</div>
            <pre>${this.escapeHtml(modeLabel)}</pre>
        </section>` : ''}
        <section>
            <div class="label">Selected Snippet</div>
            <pre>${safeSelection}</pre>
        </section>
        ${contextSummary ? `<section>
            <div class="label">Context Summary</div>
            <pre>${contextSummary}</pre>
        </section>` : ''}
        ${warnings ? `<section>
            <div class="label">Warnings</div>
            <ul>${warnings}</ul>
        </section>` : ''}
        ${workflowJson ? `<section>
            <h2>Integration Workflow</h2>
            <pre>${workflowJson}</pre>
        </section>` : ''}
        ${!workflowJson && modeContextJson ? `<section>
            <h2>Mode Context</h2>
            <pre>${modeContextJson}</pre>
        </section>` : ''}
        <section>
            <h2>Suggested Plan</h2>
            <pre>${suggestionMarkdown}</pre>
        </section>
    </body>
</html>
        `;
    }

    private static escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}

