import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as vscode from 'vscode';
import which from 'which';

export type EnvironmentSource =
    | 'pythonExtension'
    | 'workspace'
    | 'searchPath'
    | 'configuration'
    | 'global';

export type EnvironmentKind = 'venv' | 'conda' | 'poetry' | 'pyenv' | 'global' | 'unknown';

export interface EnvironmentCandidate {
    readonly path: string;
    readonly pythonPath?: string;
    readonly source: EnvironmentSource;
    readonly kind: EnvironmentKind;
    readonly label: string;
    readonly detail?: string;
    readonly description?: string;
    readonly priority: number;
    readonly confidence: 'high' | 'medium' | 'low';
}

export interface DiscoverEnvironmentOptions {
    /**
     * Optional list of paths to prioritise when scanning for environments.
     * They will be searched in the order provided.
     */
    readonly searchPaths?: readonly string[];
    /**
     * Whether to include the currently active interpreter from the Python extension.
     * Defaults to true.
     */
    readonly includePythonExtension?: boolean;
    /**
     * Whether to include global PATH python as a fallback candidate.
     * Defaults to true.
     */
    readonly includeGlobal?: boolean;
    /**
     * Override workspace folders used for automatic discovery when searchPaths is not provided.
     */
    readonly workspaceFolders?: readonly vscode.WorkspaceFolder[];
}

interface CandidateAccumulator {
    add(candidate: EnvironmentCandidate): void;
    values(): EnvironmentCandidate[];
}

const DEFAULT_ENV_NAMES = new Set([
    '.venv',
    'venv',
    '.env',
    'env',
    '.virtualenv',
    '.python',
    '.envs'
]);

const PYTHON_EXECUTABLE_VARIANTS = process.platform === 'win32'
    ? ['python.exe', 'python']
    : ['python', 'python3'];

const PYTHON_EXTENSION_COMMANDS = [
    'python.environments.getActiveEnvironmentPath',
    'python.Environments.getActiveEnvironmentPath'
];

export async function discoverEnvironmentCandidates(
    options: DiscoverEnvironmentOptions = {}
): Promise<EnvironmentCandidate[]> {
    const accumulator = createAccumulator();
    const includePythonExtension = options.includePythonExtension !== false;
    const includeGlobal = options.includeGlobal !== false;

    if (includePythonExtension) {
        const pythonCandidate = await detectFromPythonExtension();
        if (pythonCandidate) {
            accumulator.add(pythonCandidate);
        }
    }

    const searchRoots = resolveSearchRoots(options);
    for (const root of searchRoots) {
        const rootCandidates = await scanSearchRoot(root);
        for (const candidate of rootCandidates) {
            accumulator.add(candidate);
        }
    }

    const configurationCandidate = await detectFromConfiguration();
    if (configurationCandidate) {
        accumulator.add(configurationCandidate);
    }

    if (includeGlobal) {
        const globalCandidate = await detectFromGlobalPython();
        if (globalCandidate) {
            accumulator.add(globalCandidate);
        }
    }

    return dedupeAndSort(accumulator.values());
}

function createAccumulator(): CandidateAccumulator {
    const map = new Map<string, EnvironmentCandidate>();
    return {
        add(candidate: EnvironmentCandidate) {
            const key = normalizePath(candidate.path);
            const existing = map.get(key);
            if (!existing || candidate.priority < existing.priority) {
                map.set(key, { ...candidate, path: key });
            }
        },
        values() {
            return Array.from(map.values());
        }
    };
}

function resolveSearchRoots(options: DiscoverEnvironmentOptions): string[] {
    const roots = new Set<string>();
    const searchPaths = options.searchPaths ?? [];
    for (const value of searchPaths) {
        if (value) {
            roots.add(normalizePath(value));
        }
    }

    if (roots.size === 0) {
        const folders = options.workspaceFolders ?? vscode.workspace.workspaceFolders ?? [];
        for (const folder of folders) {
            roots.add(folder.uri.fsPath);
        }
    }

    return Array.from(roots);
}

async function scanSearchRoot(root: string): Promise<EnvironmentCandidate[]> {
    const stats = await safeStat(root);
    if (!stats?.isDirectory()) {
        return [];
    }

    const candidates: EnvironmentCandidate[] = [];
    const directCandidate = await inspectEnvironment(root, {
        kindHint: 'venv',
        description: 'Detected workspace environment',
        source: 'workspace',
        priority: 15
    });
    if (directCandidate) {
        candidates.push(directCandidate);
    }

    let entries: fs.Dirent[];
    try {
        entries = await fs.promises.readdir(root, { withFileTypes: true });
    } catch {
        return candidates;
    }

    for (const entry of entries) {
        if (!entry.isDirectory()) {
            continue;
        }

        const entryName = entry.name;
        if (!DEFAULT_ENV_NAMES.has(entryName) && !entryName.endsWith('.venv')) {
            continue;
        }

        const envRoot = path.join(root, entryName);
        const envCandidate = await inspectEnvironment(envRoot, {
            kindHint: entryName.includes('conda') ? 'conda' : 'venv',
            description: `Detected at ${entryName}`,
            source: 'workspace',
            priority: 10
        });

        if (envCandidate) {
            candidates.push(envCandidate);
        }
    }

    const pyenvCandidate = await detectPyenv(root);
    if (pyenvCandidate) {
        candidates.push(pyenvCandidate);
    }

    return candidates;
}

async function detectFromPythonExtension(): Promise<EnvironmentCandidate | undefined> {
    for (const command of PYTHON_EXTENSION_COMMANDS) {
        try {
            const result = await vscode.commands.executeCommand<unknown>(command);
            const interpreted = interpretPythonExtensionResult(result);
            if (interpreted) {
                const envCandidate = await inspectEnvironment(interpreted, {
                    kindHint: 'venv',
                    description: 'Active interpreter from Python extension',
                    source: 'pythonExtension',
                    priority: 0
                });
                if (envCandidate) {
                    return envCandidate;
                }
            }
        } catch {
            // Ignore missing command errors.
        }
    }
    return undefined;
}

function interpretPythonExtensionResult(result: unknown): string | undefined {
    if (!result) {
        return undefined;
    }

    if (typeof result === 'string' && result.trim()) {
        return result;
    }

    if (typeof result === 'object') {
        const candidate = result as { path?: string; id?: string; uri?: { fsPath?: string } };
        if (candidate.path && typeof candidate.path === 'string') {
            return candidate.path;
        }
        if (candidate.uri?.fsPath) {
            return candidate.uri.fsPath;
        }
        if (candidate.id && typeof candidate.id === 'string' && candidate.id.includes(path.sep)) {
            return candidate.id;
        }
    }

    return undefined;
}

async function detectFromConfiguration(): Promise<EnvironmentCandidate | undefined> {
    const configuration = vscode.workspace.getConfiguration('fluxloop');
    const pythonPath = configuration.get<string>('pythonPath')?.trim();
    if (!pythonPath) {
        return undefined;
    }

    const envRoot = deriveEnvironmentRoot(pythonPath);
    const candidate = await inspectEnvironment(envRoot, {
        kindHint: 'venv',
        description: 'Configured Python path for FluxLoop',
        source: 'configuration',
        priority: 5
    });

    return candidate;
}

async function detectFromGlobalPython(): Promise<EnvironmentCandidate | undefined> {
    try {
        const pythonExecutable = process.platform === 'win32' ? 'python.exe' : 'python3';
        let pythonPath: string;
        try {
            pythonPath = await which(pythonExecutable);
        } catch {
            pythonPath = await which(process.platform === 'win32' ? 'python' : 'python');
        }
        const envRoot = deriveEnvironmentRoot(pythonPath);
        return {
            path: envRoot,
            pythonPath,
            source: 'global',
            kind: 'global',
            label: describeEnvironmentRoot(envRoot),
            detail: pythonPath,
            description: 'Python found on PATH (global)',
            priority: 50,
            confidence: 'low'
        };
    } catch {
        return undefined;
    }
}

async function detectPyenv(root: string): Promise<EnvironmentCandidate | undefined> {
    const pyenvVersionFile = path.join(root, '.python-version');
    const exists = await pathExists(pyenvVersionFile);
    if (!exists) {
        return undefined;
    }

    const version = (await fs.promises.readFile(pyenvVersionFile, 'utf8')).trim();
    if (!version) {
        return undefined;
    }

    const pyenvRoot = process.env.PYENV_ROOT
        ? normalizePath(process.env.PYENV_ROOT)
        : path.join(os.homedir(), '.pyenv');
    const envRoot = path.join(pyenvRoot, 'versions', version);
    const candidate = await inspectEnvironment(envRoot, {
        kindHint: 'pyenv',
        description: `pyenv environment (${version})`,
        source: 'workspace',
        priority: 12
    });

    return candidate;
}

async function inspectEnvironment(
    envRoot: string,
    context: {
        kindHint: EnvironmentKind;
        description: string;
        source: EnvironmentSource;
        priority: number;
    }
): Promise<EnvironmentCandidate | undefined> {
    const normalized = normalizePath(envRoot);
    const stats = await safeStat(normalized);
    if (!stats?.isDirectory()) {
        return undefined;
    }

    const pythonPath = await findPythonExecutable(normalized);
    if (!pythonPath) {
        return undefined;
    }

    const kind = classifyEnvironment(normalized, context.kindHint);
    const label = describeEnvironmentRoot(normalized);

    return {
        path: normalized,
        pythonPath,
        source: context.source,
        kind,
        label,
        detail: pythonPath,
        description: context.description,
        priority: context.priority,
        confidence: kind === 'venv' || kind === 'conda' || kind === 'pyenv' ? 'high' : 'medium'
    };
}

function classifyEnvironment(envRoot: string, hint: EnvironmentKind): EnvironmentKind {
    if (hint === 'global') {
        return 'global';
    }

    if (fs.existsSync(path.join(envRoot, 'conda-meta'))) {
        return 'conda';
    }
    if (fs.existsSync(path.join(envRoot, 'pyvenv.cfg'))) {
        return 'venv';
    }
    if (fs.existsSync(path.join(envRoot, 'poetry.lock'))) {
        return 'poetry';
    }

    return hint;
}

async function findPythonExecutable(envRoot: string): Promise<string | undefined> {
    for (const variant of PYTHON_EXECUTABLE_VARIANTS) {
        const locations = buildInterpreterCandidates(envRoot, variant);
        for (const location of locations) {
            if (await pathExists(location)) {
                return location;
            }
        }
    }
    return undefined;
}

function buildInterpreterCandidates(envRoot: string, executableName: string): string[] {
    if (process.platform === 'win32') {
        return [
            path.join(envRoot, 'Scripts', executableName),
            path.join(envRoot, executableName)
        ];
    }
    return [
        path.join(envRoot, 'bin', executableName),
        path.join(envRoot, executableName)
    ];
}

function deriveEnvironmentRoot(pythonPath: string): string {
    const normalized = normalizePath(pythonPath);
    const segments = normalized.split(path.sep);

    if (segments.length >= 2) {
        const parent = segments.slice(0, -1).join(path.sep);
        if (segments[segments.length - 2] === 'bin' || segments[segments.length - 2] === 'Scripts') {
            return segments.slice(0, -2).join(path.sep) || parent;
        }
        return parent;
    }

    return normalized;
}

function describeEnvironmentRoot(envRoot: string): string {
    const expandedHome = expandHome(envRoot);
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (workspaceFolder && expandedHome.startsWith(workspaceFolder)) {
        const relative = path.relative(workspaceFolder, expandedHome);
        return relative ? `./${relative}` : '.';
    }
    if (expandedHome.startsWith(os.homedir())) {
        const relative = path.relative(os.homedir(), expandedHome);
        return `~/${relative}`;
    }
    return expandedHome;
}

function dedupeAndSort(candidates: EnvironmentCandidate[]): EnvironmentCandidate[] {
    return candidates
        .sort((a, b) => {
            if (a.priority !== b.priority) {
                return a.priority - b.priority;
            }
            if (a.source !== b.source) {
                return a.source.localeCompare(b.source);
            }
            return a.path.localeCompare(b.path);
        })
        .filter((candidate, index, array) => {
            if (index === 0) {
                return true;
            }
            const previous = array[index - 1];
            return candidate.path !== previous.path || candidate.source !== previous.source;
        });
}

function normalizePath(target: string): string {
    if (target.startsWith('~')) {
        return path.resolve(os.homedir(), target.slice(1));
    }
    return path.resolve(target);
}

function expandHome(target: string): string {
    if (target.startsWith(os.homedir())) {
        return target;
    }
    const relative = path.relative(os.homedir(), target);
    if (!relative.startsWith('..')) {
        return path.join(os.homedir(), relative);
    }
    return target;
}

async function pathExists(target: string): Promise<boolean> {
    try {
        await fs.promises.access(target, fs.constants.F_OK);
        return true;
    } catch {
        return false;
    }
}

async function safeStat(target: string): Promise<fs.Stats | undefined> {
    try {
        return await fs.promises.stat(target);
    } catch {
        return undefined;
    }
}

