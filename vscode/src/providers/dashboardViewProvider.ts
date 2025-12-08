import * as vscode from 'vscode';
import { ProjectEntry } from '../project/projectManager';
import { DetectedEnvironment } from '../environment/environmentManager';

export type FluxloopActiveView = 'workspace' | 'playground' | 'insights';

export interface OnboardingCard {
    id: string;
    title: string;
    description: string;
    actionLabel?: string;
    actionCommand?: string;
    actionArguments?: unknown[];
}

interface DashboardSnapshot {
    activeView: FluxloopActiveView;
    project?: ProjectEntry;
    environment?: DetectedEnvironment;
    onboardingCards: OnboardingCard[];
}

interface DashboardStatePayload {
    activeView: FluxloopActiveView;
    projectName: string;
    projectPath?: string;
    environmentLabel: string;
    onboardingCards: OnboardingCard[];
}

export class DashboardViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'fluxloop.dashboard';

    private view?: vscode.WebviewView;
    private snapshot: DashboardSnapshot = {
        activeView: 'workspace',
        onboardingCards: []
    };

    constructor(
        private readonly extensionUri: vscode.Uri,
        private readonly callbacks: {
            onSwitchView: (view: FluxloopActiveView) => void;
            onDismissOnboarding: (cardId: string) => void;
        }
    ) {}

    resolveWebviewView(webviewView: vscode.WebviewView): void | Thenable<void> {
        this.view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };

        webviewView.webview.html = this.renderHtml();

        webviewView.webview.onDidReceiveMessage(message => {
            if (!message?.type) {
                return;
            }

            if (message.type === 'switchView') {
                const view = message.view as FluxloopActiveView | undefined;
                if (view && ['workspace', 'playground', 'insights'].includes(view)) {
                    this.callbacks.onSwitchView(view);
                }
                return;
            }

            if (message.type === 'openVideoGuide') {
                void vscode.env.openExternal(
                    vscode.Uri.parse('https://docs.fluxloop.ai/vscode/user-guide/video-guide')
                );
                return;
            }

            if (message.type === 'dismissOnboarding') {
                const cardId = message.cardId as string | undefined;
                if (cardId) {
                    this.callbacks.onDismissOnboarding(cardId);
                }
                return;
            }

            if (message.type === 'runOnboardingAction') {
                const command = message.command as string | undefined;
                const args = Array.isArray(message.arguments) ? message.arguments : undefined;
                if (command) {
                    void vscode.commands.executeCommand(command, ...(args ?? []));
                }
                return;
            }
        });

        this.pushState();
    }

    updateSnapshot(partial: Partial<DashboardSnapshot>): void {
        this.snapshot = {
            ...this.snapshot,
            ...partial,
            onboardingCards: partial.onboardingCards ?? this.snapshot.onboardingCards
        };
        this.pushState();
    }

    getActiveView(): FluxloopActiveView {
        return this.snapshot.activeView;
    }

    private pushState(): void {
        if (!this.view) {
            return;
        }

        const payload: DashboardStatePayload = {
            activeView: this.snapshot.activeView,
            projectName: this.snapshot.project?.name ?? 'No project selected',
            projectPath: this.snapshot.project?.path,
            environmentLabel: this.buildEnvironmentLabel(this.snapshot.environment),
            onboardingCards: this.snapshot.onboardingCards
        };

        this.view.webview.postMessage({ type: 'state', payload });
    }

    private buildEnvironmentLabel(environment: DetectedEnvironment | undefined): string {
        if (!environment) {
            return 'Environment not detected';
        }

        const parts: string[] = [];
        parts.push(environment.environmentType ?? 'unknown');

        if (environment.pythonPath) {
            parts.push('python ✓');
        }

        if (environment.fluxloopPath || environment.fluxloopMcpPath) {
            parts.push('fluxloop ✓');
        }

        return parts.join(' • ');
    }

    private renderHtml(): string {
        const nonce = Date.now().toString(36);

        return /* html */`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            color-scheme: var(--vscode-color-scheme);
        }

        body {
            padding: 8px 12px 4px;
            margin: 0;
            background-color: transparent;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
        }

        .dashboard {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .summary {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            padding: 6px 8px;
            border-radius: 6px;
            background-color: color-mix(in srgb, var(--vscode-foreground) 8%, transparent);
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
        }

        .summary-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 0;
            min-height: 16px;
            min-width: 0;
            border-radius: 4px;
        }

        .summary-icon {
            width: 14px;
            height: 14px;
            fill: var(--vscode-descriptionForeground);
            flex-shrink: 0;
        }

        .summary-value {
            font-size: 10px;
            font-weight: 500;
            color: var(--vscode-descriptionForeground);
            display: inline-flex;
            gap: 4px;
            align-items: center;
            white-space: nowrap;
            max-width: 220px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .summary-value strong {
            font-weight: 600;
            color: var(--vscode-foreground);
        }

        .video-guide-cta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid color-mix(in srgb, var(--vscode-editorWidget-border) 65%, transparent);
            background: linear-gradient(
                120deg,
                color-mix(in srgb, var(--vscode-button-background) 85%, transparent),
                color-mix(in srgb, var(--vscode-button-background) 35%, var(--vscode-sideBar-background) 65%)
            );
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
        }

        .video-guide-content {
            flex: 1 1 220px;
        }

        .video-guide-title {
            margin: 0;
            font-size: 13px;
            font-weight: 700;
        }

        .video-guide-description {
            margin: 4px 0 0;
            font-size: 11px;
            color: color-mix(in srgb, var(--vscode-foreground) 80%, var(--vscode-editorWidget-background));
        }

        .video-guide-button {
            align-self: center;
            padding: 8px 14px;
            border-radius: 5px;
            border: none;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            color: var(--vscode-button-foreground);
            background-color: var(--vscode-button-background);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            transition: transform 120ms ease, box-shadow 120ms ease;
        }

        .video-guide-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
        }

        .tabs {
            display: flex;
            gap: 8px;
            align-items: center;
            padding: 2px 0 4px;
        }

        .tab-button {
            appearance: none;
            border: none;
            border-bottom: 2px solid transparent;
            background-color: transparent;
            color: var(--vscode-descriptionForeground);
            font-size: 12px;
            font-family: inherit;
            font-weight: 500;
            padding: 6px 10px;
            cursor: pointer;
            transition: color 120ms ease, border-color 120ms ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .tab-button:hover {
            color: var(--vscode-foreground);
        }

        .tab-button.active {
            color: var(--vscode-foreground);
            border-bottom-color: var(--vscode-foreground);
        }

        .tab-icon {
            width: 14px;
            height: 14px;
            fill: currentColor;
        }

        .onboarding {
            display: none;
            flex-direction: column;
            gap: 6px;
        }

        .onboarding-card {
            position: relative;
            padding: 8px 10px 10px;
            border-radius: 4px;
            border: 1px solid color-mix(in srgb, var(--vscode-button-background) 80%, var(--vscode-editorWidget-border));
            background-color: var(--vscode-button-background);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
        }

        .onboarding-title {
            font-size: 12px;
            font-weight: 600;
            margin: 0 20px 4px 0;
            color: var(--vscode-button-foreground);
        }

        .onboarding-body {
            font-size: 11px;
            color: color-mix(in srgb, var(--vscode-button-foreground) 82%, var(--vscode-editorWidget-background));
            margin: 0;
            white-space: pre-line;
        }

        .onboarding-actions {
            margin-top: 8px;
            display: flex;
            gap: 6px;
        }

        .onboarding-button {
            padding: 4px 10px;
            border-radius: 3px;
            border: 1px solid color-mix(in srgb, var(--vscode-button-foreground) 60%, transparent);
            background-color: color-mix(in srgb, var(--vscode-button-background) 65%, var(--vscode-button-foreground) 10%);
            color: var(--vscode-button-foreground);
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
        }

        .onboarding-button:hover {
            background-color: color-mix(in srgb, var(--vscode-button-background) 80%, var(--vscode-button-foreground) 15%);
        }

        .onboarding-dismiss {
            position: absolute;
            top: 6px;
            right: 6px;
            border: none;
            background: transparent;
            color: color-mix(in srgb, var(--vscode-button-foreground) 75%, var(--vscode-editorWidget-background));
            cursor: pointer;
            padding: 2px;
            border-radius: 3px;
        }

        .onboarding-dismiss:hover {
            color: var(--vscode-button-foreground);
            background-color: color-mix(in srgb, var(--vscode-button-foreground) 20%, transparent);
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="summary">
            <div class="summary-item">
                <svg class="summary-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M2.5 3h3.8l1 1H13a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm0 1v8H13V5H7.9l-1-1H2.5z"/>
                </svg>
                <span class="summary-value" id="projectSummary">
                    <strong id="projectName">Loading…</strong>
                    <span id="projectPath" class="summary-detail"></span>
                </span>
            </div>
            <div class="summary-item">
                <svg class="summary-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M8 1a3 3 0 0 1 3 3h4a1 1 0 0 1 0 2h-2l-1.3 7.1A2 2 0 0 1 9.7 14H6.3a2 2 0 0 1-1.976-1.672L3 6H1a1 1 0 1 1 0-2h4a3 3 0 0 1 3-3Zm0 2a1 1 0 0 0-.995.9L7 4H9a1 1 0 0 0-1-1Zm-1.8 9h3.6l1-5H5.2l1 5Z"/>
                </svg>
                <span class="summary-value">
                    <strong id="environmentLabel">Detecting…</strong>
                </span>
            </div>
        </div>
        <div class="video-guide-cta">
            <div class="video-guide-content">
                <p class="video-guide-title">Watch the Video Tutorial</p>
                <p class="video-guide-description">Tour the key workflows in under 3 minutes.</p>
            </div>
            <button class="video-guide-button" id="videoGuideButton">Open Tutorial</button>
        </div>
        <div class="tabs">
            <button class="tab-button" data-view="workspace">
                <svg class="tab-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M2.5 3h3.8l1 1H13a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm0 1v8H13V5H7.9l-1-1H2.5z"/>
                </svg>
                <span>Workspace</span>
            </button>
            <button class="tab-button" data-view="playground">
                <svg class="tab-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M6 2.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 .5.5v1.1l1.9 4.3c.1.2.1.4.1.6v3c0 1.4-1.1 2.5-2.5 2.5H6.5A2.5 2.5 0 0 1 4 11.5v-3c0-.2 0-.4.1-.6L6 3.6V2.5Zm1 .5v1L4.8 8.1a.5.5 0 0 0-.1.4v3c0 .8.6 1.5 1.5 1.5h3c.9 0 1.5-.7 1.5-1.5v-3c0-.1 0-.3-.1-.4L9 4V3h-2Z"/>
                    <path d="M5.5 8h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1 0-1Zm0 2h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1 0-1Z"/>
                </svg>
                <span>Playground</span>
            </button>
            <button class="tab-button" data-view="insights">
                <svg class="tab-icon" viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M2 3.5a.5.5 0 0 1 .5-.5H5a.5.5 0 0 1 .5.5V11l2.3-3.1a.5.5 0 0 1 .4-.2h2a.5.5 0 0 1 .4.2l1.4 1.9 1.1-1.5a.5.5 0 0 1 .4-.2h.6a.5.5 0 1 1 0 1h-.3l-1.4 1.9a.5.5 0 0 1-.4.2.5.5 0 0 1-.4-.2L9.9 9H8.4L6 12.2a.5.5 0 0 1-.9-.3V4H2.5a.5.5 0 0 1-.5-.5Z"/>
                    <path d="M2 13.5a.5.5 0 0 1 .5-.5h11a.5.5 0 1 1 0 1h-11a.5.5 0 0 1-.5-.5Z"/>
                </svg>
                <span>Insights</span>
            </button>
        </div>
        <div class="onboarding" id="onboardingCards"></div>
    </div>
    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        const onboardingContainer = document.getElementById('onboardingCards');

        function setActiveButton(view) {
            document.querySelectorAll('.tab-button').forEach(button => {
                if (button.dataset.view === view) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }
            });
        }

        function renderOnboardingCards(cards) {
            if (!onboardingContainer) {
                return;
            }

            onboardingContainer.innerHTML = '';

            if (!cards || cards.length === 0) {
                onboardingContainer.style.display = 'none';
                return;
            }

            onboardingContainer.style.display = 'flex';

            cards.forEach(card => {
                const cardEl = document.createElement('div');
                cardEl.className = 'onboarding-card';
                cardEl.dataset.cardId = card.id;

                const dismissBtn = document.createElement('button');
                dismissBtn.className = 'onboarding-dismiss';
                dismissBtn.setAttribute('aria-label', 'Dismiss');
                dismissBtn.textContent = '×';
                dismissBtn.addEventListener('click', () => {
                    vscode.postMessage({ type: 'dismissOnboarding', cardId: card.id });
                });
                cardEl.appendChild(dismissBtn);

                const titleEl = document.createElement('h4');
                titleEl.className = 'onboarding-title';
                titleEl.textContent = card.title;
                cardEl.appendChild(titleEl);

                const bodyEl = document.createElement('p');
                bodyEl.className = 'onboarding-body';
                bodyEl.textContent = card.description;
                cardEl.appendChild(bodyEl);

                if (card.actionLabel && card.actionCommand) {
                    const actionsEl = document.createElement('div');
                    actionsEl.className = 'onboarding-actions';

                    const actionButton = document.createElement('button');
                    actionButton.className = 'onboarding-button';
                    actionButton.textContent = card.actionLabel;
                    actionButton.addEventListener('click', () => {
                        vscode.postMessage({
                            type: 'runOnboardingAction',
                            command: card.actionCommand,
                            arguments: card.actionArguments ?? [],
                            cardId: card.id
                        });
                    });

                    actionsEl.appendChild(actionButton);
                    cardEl.appendChild(actionsEl);
                }

                onboardingContainer.appendChild(cardEl);
            });
        }

        function updateState(state) {
            if (!state) {
                return;
            }
            document.getElementById('projectName').textContent = state.projectName;
            const projectPathEl = document.getElementById('projectPath');
            if (state.projectPath) {
                projectPathEl.textContent = '- ' + state.projectPath;
                projectPathEl.style.display = 'inline';
            } else {
                projectPathEl.textContent = '';
                projectPathEl.style.display = 'none';
            }

            document.getElementById('environmentLabel').textContent = state.environmentLabel;

            setActiveButton(state.activeView);
            renderOnboardingCards(state.onboardingCards);
        }

        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                const view = button.dataset.view;
                vscode.postMessage({ type: 'switchView', view });
            });
        });

        const videoGuideButton = document.getElementById('videoGuideButton');
        if (videoGuideButton) {
            videoGuideButton.addEventListener('click', () => {
                vscode.postMessage({ type: 'openVideoGuide' });
            });
        }

        window.addEventListener('message', event => {
            const message = event.data;
            if (message?.type === 'state') {
                updateState(message.payload);
            }
        });
    </script>
</body>
</html>`;
    }
}

