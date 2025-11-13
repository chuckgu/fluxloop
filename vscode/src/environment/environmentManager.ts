import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as vscode from 'vscode';
import which from 'which';
import { ProjectContext } from '../project/projectContext';
import { ProjectEntry } from '../project/projectManager';
import { OutputChannelManager } from '../utils/outputChannel';

const EXECUTABLE_EXTENSIONS = process.platform === 'win32' ? ['.exe', '.cmd', '.bat', ''] : ['', '.sh'];

export type EnvironmentType = 'venv' | 'conda' | 'workspace' | 'global' | 'custom' | 'unknown';

export interface DetectedEnvironment {
    root: string;
    pythonPath?: string;
    fluxloopPath?: string;
    fluxloopMcpPath?: string;
    environmentType: EnvironmentType;
    notes: string[];
}

export interface EnvironmentCheckResult {
    root: string;
    pythonPath?: string;
    fluxloopPath?: string;
    fluxloopMcpPath?: string;
    environmentType: EnvironmentType;
    hasEnvironment: boolean;
    hasPython: boolean;
    hasFluxloop: boolean;
    hasFluxloopMcp: boolean;
    missing: string[];
    notes: string[];
}

interface EnvironmentCandidate {
    type: EnvironmentType;
    baseDir: string;
}

type ExecutionMode = 'auto' | 'workspace' | 'global' | 'custom';

interface EnvironmentConfiguration {
    executionMode: ExecutionMode;
    pythonPath?: string;
    mcpCommandPath?: string;
}

export class EnvironmentManager implements vscode.Disposable {
    private readonly cache = new Map<string, DetectedEnvironment>();
    private readonly emitter = new vscode.EventEmitter<DetectedEnvironment | undefined>();
    private readonly disposables: vscode.Disposable[] = [];
    private lastSignature: string | undefined;
    private currentEnvironment: DetectedEnvironment | undefined;
    private readonly output = OutputChannelManager.getInstance();

    constructor() {
        this.disposables.push(
            vscode.workspace.onDidChangeConfiguration(event => {
                if (
                    event.affectsConfiguration('fluxloop.targetSourceRoot') ||
                    event.affectsConfiguration('fluxloop.executionMode') ||
                    event.affectsConfiguration('fluxloop.pythonPath') ||
                    event.affectsConfiguration('fluxloop.mcpCommandPath')
                ) {
                    this.cache.clear();
                    void this.refreshActiveEnvironment();
                }
            }),
            vscode.workspace.onDidChangeWorkspaceFolders(() => {
                this.cache.clear();
                void this.refreshActiveEnvironment();
            })
        );
    }

    dispose(): void {
        this.emitter.dispose();
        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            disposable?.dispose();
        }
    }

    get onDidChangeEnvironment(): vscode.Event<DetectedEnvironment | undefined> {
        return this.emitter.event;
    }

    getActiveEnvironment(): DetectedEnvironment | undefined {
        return this.currentEnvironment;
    }

    async getResolvedEnvironment(forceRefresh = false): Promise<DetectedEnvironment | undefined> {
        if (forceRefresh || !this.currentEnvironment) {
            return await this.refreshActiveEnvironment();
        }
        return this.currentEnvironment;
    }

    async resolveCommand(command: string): Promise<{ command: string; env: NodeJS.ProcessEnv }> {
        const environment = await this.getResolvedEnvironment();
        const resolvedCommand =
            environment ? this.resolveExecutablePath(command, environment) ?? command : command;
        const env = await this.getProcessEnv();
        return { command: resolvedCommand, env };
    }

    async getProcessEnv(extra: Record<string, string | undefined> = {}): Promise<NodeJS.ProcessEnv> {
        const environment = await this.getResolvedEnvironment();
        const result: NodeJS.ProcessEnv = { ...process.env };

        if (environment) {
            const binDirs = this.collectBinDirectories(environment);
            if (binDirs.length) {
                const separator = process.platform === 'win32' ? ';' : ':';
                const existingPath = result.PATH ?? result.Path ?? '';
                const combined = [...binDirs, existingPath].filter(Boolean).join(separator);
                result.PATH = combined;
                if (process.platform === 'win32') {
                    result.Path = combined;
                }
            }
        }

        for (const [key, value] of Object.entries(extra)) {
            if (value !== undefined) {
                result[key] = value;
            }
        }

        return result;
    }

    async checkEnvironment(root: string): Promise<EnvironmentCheckResult> {
        const normalizedRoot = path.resolve(root);
        const missingSet = new Set<string>();
        let environmentType: EnvironmentType = 'unknown';
        let pythonPath: string | undefined;
        let fluxloopPath: string | undefined;
        let fluxloopMcpPath: string | undefined;
        let notes: string[] = [];
        let hasEnvironment = false;

        if (!fs.existsSync(normalizedRoot) || !fs.statSync(normalizedRoot).isDirectory()) {
            missingSet.add('Python interpreter');
            missingSet.add('FluxLoop CLI (fluxloop)');
            missingSet.add('FluxLoop MCP (fluxloop-mcp)');
            notes.push(`Directory does not exist: ${normalizedRoot}`);
        } else {
            const detected = this.detectLocalEnvironment(normalizedRoot);
            if (detected) {
                hasEnvironment = true;
                environmentType = detected.environmentType;
                pythonPath = detected.pythonPath;
                fluxloopPath = detected.fluxloopPath;
                fluxloopMcpPath = detected.fluxloopMcpPath;
                notes = detected.notes;
            } else {
                notes.push('No virtual environment found in target source root.');
            }
        }

        if (!pythonPath) {
            missingSet.add('Python interpreter');
        }
        if (!fluxloopPath) {
            missingSet.add('FluxLoop CLI (fluxloop)');
        }
        if (!fluxloopMcpPath) {
            missingSet.add('FluxLoop MCP (fluxloop-mcp)');
        }

        return {
            root: normalizedRoot,
            pythonPath,
            fluxloopPath,
            fluxloopMcpPath,
            environmentType,
            hasEnvironment,
            hasPython: !!pythonPath,
            hasFluxloop: !!fluxloopPath,
            hasFluxloopMcp: !!fluxloopMcpPath,
            missing: Array.from(missingSet),
            notes
        };
    }

    async refreshActiveEnvironment(): Promise<DetectedEnvironment | undefined> {
        const project = ProjectContext.getActiveProject();
        const root = this.resolveTargetRoot(project);

        if (!root) {
            this.currentEnvironment = undefined;
            this.logEnvironmentInfo('No FluxLoop project or source root detected.', undefined);
            this.emitter.fire(undefined);
            return undefined;
        }

        if (!fs.existsSync(root)) {
            this.currentEnvironment = undefined;
            this.logEnvironmentInfo(`Configured source root does not exist: ${root}`, undefined);
            this.emitter.fire(undefined);
            return undefined;
        }

        const configuration = this.getEnvironmentConfiguration(project);
        const cacheKey = this.buildCacheKey(root, configuration);

        const cached = this.cache.get(cacheKey);
        if (cached) {
            this.currentEnvironment = cached;
            this.logEnvironmentInfo(root, cached);
            this.emitter.fire(cached);
            return cached;
        }

        const detected = await this.detectEnvironment(root, configuration);
        this.cache.set(cacheKey, detected);
        this.currentEnvironment = detected;
        this.logEnvironmentInfo(root, detected);
        this.emitter.fire(detected);
        return detected;
    }

    private resolveTargetRoot(project: ProjectEntry | undefined): string | undefined {
        const configuration = vscode.workspace.getConfiguration('fluxloop', project ? vscode.Uri.file(project.path) : undefined);
        const configuredPath = configuration.get<string>('targetSourceRoot')?.trim();
        const projectPath = project?.path ?? ProjectContext.getActiveWorkspacePath();

        const resolvePath = (value: string): string | undefined => {
            if (!value) {
                return undefined;
            }
            const expanded = value.startsWith('~') ? path.join(os.homedir(), value.slice(1)) : value;
            if (path.isAbsolute(expanded)) {
                return path.resolve(expanded);
            }
            if (projectPath) {
                return path.resolve(projectPath, expanded);
            }
            const workspaceFolder = this.getPrimaryWorkspaceFolder();
            if (workspaceFolder) {
                return path.resolve(workspaceFolder.uri.fsPath, expanded);
            }
            return path.resolve(expanded);
        };

        if (configuredPath) {
            const resolved = resolvePath(configuredPath);
            if (resolved) {
                return resolved;
            }
        }

        if (project?.sourceRoot) {
            return path.resolve(project.path, project.sourceRoot);
        }

        if (project?.path) {
            return project.path;
        }

        const workspaceFolder = this.getPrimaryWorkspaceFolder();
        return workspaceFolder?.uri.fsPath;
    }

    private getPrimaryWorkspaceFolder(): vscode.WorkspaceFolder | undefined {
        if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
            return undefined;
        }
        return vscode.workspace.workspaceFolders[0];
    }

    private async detectEnvironment(root: string, config: EnvironmentConfiguration): Promise<DetectedEnvironment> {
        let environment: DetectedEnvironment;

        switch (config.executionMode) {
            case 'global': {
                environment = this.cloneEnvironment(await this.detectGlobalEnvironment(root));
                environment.notes.push('Execution mode set to global; workspace environments are ignored.');
                break;
            }
            case 'workspace': {
                const localEnv = this.detectLocalEnvironment(root);
                if (localEnv) {
                    environment = this.cloneEnvironment(localEnv);
                    environment.notes.push('Execution mode set to workspace.');
                } else {
                    environment = this.cloneEnvironment(await this.detectGlobalEnvironment(root));
                    environment.environmentType = 'workspace';
                    environment.notes.push('Execution mode set to workspace but no local environment was found. Using PATH fallback.');
                }
                break;
            }
            case 'custom': {
                const localEnv = this.detectLocalEnvironment(root);
                if (localEnv) {
                    environment = this.cloneEnvironment(localEnv);
                } else {
                    environment = this.cloneEnvironment(await this.detectGlobalEnvironment(root));
                }
                environment.environmentType = 'custom';
                environment.notes.push('Execution mode set to custom; applying configured overrides.');
                break;
            }
            case 'auto':
            default: {
                const localEnv = this.detectLocalEnvironment(root);
                if (localEnv) {
                    environment = this.cloneEnvironment(localEnv);
                } else {
                    environment = this.cloneEnvironment(await this.detectGlobalEnvironment(root));
                }
                break;
            }
        }

        return this.applyOverrides(environment, config);
    }

    private detectLocalEnvironment(root: string): DetectedEnvironment | undefined {
        const candidates = this.buildEnvironmentCandidates(root);
        for (const candidate of candidates) {
            const info = this.inspectCandidate(candidate);
            if (info.pythonPath || info.fluxloopPath || info.fluxloopMcpPath) {
                return info;
            }
        }
        return undefined;
    }

    private buildEnvironmentCandidates(root: string): EnvironmentCandidate[] {
        const directories: Array<{ dir: string; type: EnvironmentType }> = [
            { dir: path.join(root, '.venv'), type: 'venv' },
            { dir: path.join(root, 'venv'), type: 'venv' },
            { dir: path.join(root, 'env'), type: 'venv' },
            { dir: path.join(root, '.env'), type: 'venv' },
            { dir: path.join(root, '.conda'), type: 'conda' }
        ];

        const project = ProjectContext.getActiveProject();
        if (project?.path && project.sourceRoot) {
            const candidate = path.resolve(project.path, project.sourceRoot, '.venv');
            directories.push({ dir: candidate, type: 'venv' });
        }

        return directories
            .filter(entry => fs.existsSync(entry.dir) && fs.statSync(entry.dir).isDirectory())
            .map(entry => ({ baseDir: entry.dir, type: entry.type }));
    }

    private inspectCandidate(candidate: EnvironmentCandidate): DetectedEnvironment {
        const pythonPath = this.findExecutable(candidate.baseDir, 'python');
        const fluxloopPath = this.findExecutable(candidate.baseDir, 'fluxloop');
        const fluxloopMcpPath = this.findExecutable(candidate.baseDir, 'fluxloop-mcp');

        const notes: string[] = [];
        if (!pythonPath) {
            notes.push(`No python executable found under ${candidate.baseDir}`);
        }
        if (pythonPath && !fluxloopPath && !fluxloopMcpPath) {
            notes.push('Python detected but FluxLoop packages were not found in this environment.');
        }

        return {
            root: candidate.baseDir,
            pythonPath,
            fluxloopPath,
            fluxloopMcpPath,
            environmentType: candidate.type,
            notes
        };
    }

    private async detectGlobalEnvironment(targetRoot: string): Promise<DetectedEnvironment> {
        const notes: string[] = ['Inspecting global PATH for FluxLoop executables.'];
        let pythonPath: string | undefined;
        let fluxloopPath: string | undefined;
        let fluxloopMcpPath: string | undefined;

        try {
            pythonPath = await which('python3');
        } catch {
            try {
                pythonPath = await which('python');
            } catch {
                notes.push('Global python interpreter not found on PATH.');
            }
        }

        try {
            fluxloopPath = await which('fluxloop');
        } catch {
            notes.push('fluxloop CLI not found on PATH.');
        }

        try {
            fluxloopMcpPath = await which('fluxloop-mcp');
        } catch {
            notes.push('fluxloop-mcp CLI not found on PATH.');
        }

        return {
            root: targetRoot,
            pythonPath,
            fluxloopPath,
            fluxloopMcpPath,
            environmentType: fluxloopPath || fluxloopMcpPath ? 'global' : 'unknown',
            notes
        };
    }

    private findExecutable(baseDir: string, executableName: string): string | undefined {
        const binDir = process.platform === 'win32'
            ? path.join(baseDir, 'Scripts')
            : path.join(baseDir, 'bin');

        if (!fs.existsSync(binDir)) {
            return undefined;
        }

        for (const extension of EXECUTABLE_EXTENSIONS) {
            const candidate = path.join(binDir, `${executableName}${extension}`);
            if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
                return candidate;
            }
        }

        return undefined;
    }

    private buildCacheKey(root: string, config: EnvironmentConfiguration): string {
        return JSON.stringify({
            root,
            executionMode: config.executionMode,
            python: config.pythonPath ?? null,
            mcp: config.mcpCommandPath ?? null
        });
    }

    private getEnvironmentConfiguration(project: ProjectEntry | undefined): EnvironmentConfiguration {
        const configuration = vscode.workspace.getConfiguration(
            'fluxloop',
            project ? vscode.Uri.file(project.path) : undefined
        );

        const executionMode = (configuration.get<string>('executionMode') as ExecutionMode | undefined) ?? 'auto';
        const pythonPath = configuration.get<string>('pythonPath')?.trim();
        const mcpCommandPath = configuration.get<string>('mcpCommandPath')?.trim();

        return {
            executionMode,
            pythonPath: pythonPath && pythonPath.length > 0 ? pythonPath : undefined,
            mcpCommandPath: mcpCommandPath && mcpCommandPath.length > 0 ? mcpCommandPath : undefined
        };
    }

    private applyOverrides(environment: DetectedEnvironment, config: EnvironmentConfiguration): DetectedEnvironment {
        const notes = [...environment.notes];
        const result: DetectedEnvironment = {
            ...environment,
            notes
        };

        if (config.pythonPath) {
            result.pythonPath = config.pythonPath;
            notes.push('Python executable overridden via fluxloop.pythonPath.');
        } else if (config.executionMode === 'custom' && !result.pythonPath) {
            notes.push('Custom execution mode: Python executable is not set.');
        }

        if (config.mcpCommandPath) {
            result.fluxloopMcpPath = config.mcpCommandPath;
            notes.push('fluxloop-mcp executable overridden via fluxloop.mcpCommandPath.');
        } else if (config.executionMode === 'custom' && !result.fluxloopMcpPath) {
            notes.push('Custom execution mode: fluxloop-mcp executable is not set.');
        }

        return result;
    }

    private cloneEnvironment(environment: DetectedEnvironment): DetectedEnvironment {
        return {
            ...environment,
            notes: [...environment.notes]
        };
    }

    private resolveExecutablePath(command: string, environment: DetectedEnvironment): string | undefined {
        const base = path.basename(command).toLowerCase();
        if (base === 'python' || base === 'python3') {
            return environment.pythonPath;
        }
        if (base.startsWith('fluxloop-mcp')) {
            return environment.fluxloopMcpPath;
        }
        if (base.startsWith('fluxloop')) {
            return environment.fluxloopPath;
        }
        return undefined;
    }

    private collectBinDirectories(environment: DetectedEnvironment): string[] {
        const segments = new Set<string>();

        const push = (dir?: string) => {
            if (!dir) {
                return;
            }
            const resolved = path.resolve(dir);
            segments.add(resolved);
        };

        const binDir = process.platform === 'win32'
            ? path.join(environment.root, 'Scripts')
            : path.join(environment.root, 'bin');
        push(binDir);
        push(environment.pythonPath ? path.dirname(environment.pythonPath) : undefined);
        push(environment.fluxloopPath ? path.dirname(environment.fluxloopPath) : undefined);
        push(environment.fluxloopMcpPath ? path.dirname(environment.fluxloopMcpPath) : undefined);

        return Array.from(segments);
    }

    private logEnvironmentInfo(rootOrMessage: string, environment: DetectedEnvironment | undefined): void {
        const segments: string[] = [];

        if (!environment) {
            segments.push(`[FluxLoop Env] ${rootOrMessage}`);
        } else {
            const signature = JSON.stringify(environment);
            if (this.lastSignature === signature) {
                return;
            }
            this.lastSignature = signature;

            segments.push('[FluxLoop Env] ----------------------------------------');
            segments.push(`[FluxLoop Env] Source root: ${rootOrMessage}`);
            segments.push(`[FluxLoop Env] Environment type: ${environment.environmentType}`);
            segments.push(`[FluxLoop Env] Python: ${environment.pythonPath ?? 'not found'}`);
            segments.push(`[FluxLoop Env] fluxloop: ${environment.fluxloopPath ?? 'not found'}`);
            segments.push(`[FluxLoop Env] fluxloop-mcp: ${environment.fluxloopMcpPath ?? 'not found'}`);
            if (environment.notes.length > 0) {
                segments.push('[FluxLoop Env] Notes:');
                environment.notes.forEach(note => segments.push(`[FluxLoop Env]  • ${note}`));
            }
            segments.push('[FluxLoop Env] ----------------------------------------');
        }

        segments.forEach(line => this.output.appendLine(line));
    }
}


