import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as yaml from 'yaml';
import { ProjectManager, ProjectEntry } from '../project/projectManager';
import { ProjectContext } from '../project/projectContext';
import { CLIManager } from '../cli/cliManager';
import { EnvironmentManager, EnvironmentCheckResult } from '../environment/environmentManager';
import { OutputChannelManager } from '../utils/outputChannel';

type PreparedEnvironment =
    | { mode: 'workspace'; root: string }
    | { mode: 'global' };

export class ProjectCommands {
    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly cliManager: CLIManager,
        private readonly environmentManager: EnvironmentManager
    ) {}

    register(): vscode.Disposable[] {
        return [
            vscode.commands.registerCommand('fluxloop.createProject', () => this.createProject()),
            vscode.commands.registerCommand('fluxloop.addProject', () => this.addExistingProject()),
            vscode.commands.registerCommand('fluxloop.selectProject', (projectId?: string) => this.selectProject(projectId)),
            vscode.commands.registerCommand('fluxloop.switchProject', () => this.showProjectQuickPick()),
            vscode.commands.registerCommand('fluxloop.removeProject', (projectId?: string) => this.removeProject(projectId)),
            vscode.commands.registerCommand('fluxloop.openProject', (uri: vscode.Uri, preview?: boolean) => this.openProject(uri, preview ?? false))
        ];
    }

    private async createProject(): Promise<void> {
        const projectFolder = await vscode.window.showOpenDialog({
            canSelectFolders: true,
            canSelectFiles: false,
            canSelectMany: false,
            openLabel: 'Select FluxLoop root folder (new project will be created inside)'
        });

        if (!projectFolder || projectFolder.length === 0) {
            return;
        }

        const selectedPath = projectFolder[0].fsPath;
        if (this.looksLikeFluxloopProject(selectedPath)) {
            void vscode.window.showErrorMessage('Selected folder already contains a FluxLoop project. Use "Add Existing Project" instead.');
            return;
        }

        const rootBaseName = path.basename(selectedPath);

        const projectName = await vscode.window.showInputBox({
            prompt: 'Project name',
            placeHolder: 'Enter a new project folder name (will be created inside selected folder)',
            validateInput: value => {
                if (!value || !value.trim()) {
                    return 'Project name is required';
                }
                if (value.trim() === rootBaseName) {
                    return 'Project name must be different from the selected folder name';
                }
                return undefined;
            }
        });

        if (!projectName) {
            return;
        }

        const includeExample = await vscode.window.showQuickPick(['Include example agent', 'Skip example agent'], {
            placeHolder: 'Would you like to include the example agent?'
        });

        const { rootDir, projectRoot } = this.resolvePathsForNewProject(selectedPath, projectName);

        const environmentChoice = await this.prepareProjectEnvironment(projectRoot, projectName);
        if (!environmentChoice) {
            return;
        }

        const args = ['init', 'project', rootDir, '--name', projectName];
        if (includeExample === 'Skip example agent') {
            args.push('--no-example');
        }

        await this.cliManager.runCommand(args, rootDir);
        await this.waitForProjectConfig(projectRoot, 30000);

        if (!this.looksLikeFluxloopProject(projectRoot)) {
            void vscode.window.showWarningMessage('Project initialized, but expected FluxLoop config files were not found. Please check the CLI output.');
        }

        await this.applyEnvironmentSettings(projectRoot, environmentChoice);

        const manager = ProjectManager.getInstance();
        manager.addProject({ name: projectName, path: projectRoot, setActive: true });
        await this.environmentManager.refreshActiveEnvironment();

        const openAction = await vscode.window.showQuickPick(['Open in current window', 'Open in new window', 'Stay in current workspace'], {
            placeHolder: 'How would you like to work with this project?'
        });

        const projectRootUri = vscode.Uri.file(projectRoot);
        if (openAction === 'Open in current window') {
            await vscode.commands.executeCommand('vscode.openFolder', projectRootUri, false);
        } else if (openAction === 'Open in new window') {
            await vscode.commands.executeCommand('vscode.openFolder', projectRootUri, true);
        }

        ProjectContext.ensureActiveProject();
    }

    private async prepareProjectEnvironment(projectRoot: string, projectName: string): Promise<PreparedEnvironment | undefined> {
        let selectedRoot: string | undefined;

        let shouldContinue = true;
        while (shouldContinue) {
            if (!selectedRoot) {
                const choice = await this.promptEnvironmentChoice(projectRoot, projectName);
                if (!choice) {
                    return undefined;
                }

                if (choice.mode === 'global') {
                    if (await this.confirmGlobalUsage()) {
                        return { mode: 'global' };
                    }
                    continue;
                }

                selectedRoot = choice.root;
            }

            const status = await this.environmentManager.checkEnvironment(selectedRoot);
            if (status.hasPython && status.hasFluxloop && status.hasFluxloopMcp) {
                this.showEnvironmentConfirmation(status);
                return { mode: 'workspace', root: selectedRoot };
            }

            const resolution = await this.promptEnvironmentResolution(status, selectedRoot);
            if (resolution === 'retry') {
                continue;
            }
            if (resolution === 'select') {
                selectedRoot = undefined;
                continue;
            }
            if (resolution === 'global') {
                if (await this.confirmGlobalUsage()) {
                    return { mode: 'global' };
                }
                selectedRoot = undefined;
                continue;
            }
            shouldContinue = false;
        }
        return undefined;
    }

    private async promptEnvironmentChoice(projectRoot: string, projectName: string): Promise<{ mode: 'workspace'; root: string } | { mode: 'global' } | undefined> {
        const items: Array<vscode.QuickPickItem & { type: 'project' | 'browse' | 'global' }> = [
            {
                label: `Use project folder (${projectName})`,
                description: this.formatShortPath(projectRoot),
                detail: 'Create and use a virtual environment inside the new project folder.',
                type: 'project'
            },
            {
                label: 'Choose another folder…',
                description: 'Select an existing virtual environment.',
                type: 'browse'
            },
            {
                label: 'Use Global PATH',
                description: 'Use the fluxloop CLI available on the current PATH (not recommended).',
                type: 'global'
            }
        ];

        const pick = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select the Python environment that already has FluxLoop packages installed.'
        });

        if (!pick) {
            return undefined;
        }

        if (pick.type === 'global') {
            return { mode: 'global' };
        }

        if (pick.type === 'browse') {
            const folder = await vscode.window.showOpenDialog({
                canSelectFolders: true,
                canSelectFiles: false,
                canSelectMany: false,
                openLabel: 'Select Python environment root'
            });

            if (!folder || folder.length === 0) {
                return undefined;
            }

            return { mode: 'workspace', root: folder[0].fsPath };
        }

        return { mode: 'workspace', root: projectRoot };
    }

    private async promptEnvironmentResolution(status: EnvironmentCheckResult, root: string): Promise<'retry' | 'select' | 'global' | 'cancel'> {
        const missing = status.missing.length ? status.missing.join(', ') : 'None';
        const location = this.formatShortPath(root);
        const baseMessage = status.hasEnvironment
            ? `The selected environment (${location}) is missing: ${missing}.`
            : `No virtual environment detected at (${location}).`;
        const noteLines = status.notes.length ? `\n• ${status.notes.join('\n• ')}` : '';
        this.log(`[Project Init] Environment issues for ${location}: missing -> ${missing}${noteLines ? ` | notes -> ${status.notes.join(' | ')}` : ''}`);

        const action = await vscode.window.showWarningMessage(
            `${baseMessage}${noteLines}\nPrepare the environment and choose "Retry".`,
            'Retry',
            'Run Setup Script',
            'Open Terminal',
            'Select Different Folder',
            'Use Global PATH'
        );

        if (action === 'Retry') {
            return 'retry';
        }

        if (action === 'Run Setup Script') {
            const launched = await this.runSetupScript(root);
            return launched ? 'retry' : 'retry';
        }

        if (action === 'Open Terminal') {
            await this.openSetupTerminal(root);
            return 'retry';
        }

        if (action === 'Select Different Folder') {
            return 'select';
        }

        if (action === 'Use Global PATH') {
            return 'global';
        }

        return 'cancel';
    }

    private async openSetupTerminal(root: string): Promise<void> {
        try {
            await fs.promises.mkdir(root, { recursive: true });
        } catch {
            // ignore directory creation errors
        }

        const terminal = vscode.window.createTerminal({
            name: 'FluxLoop Environment Setup',
            cwd: root
        });

        terminal.show();
        terminal.sendText('# If you do not have an environment, install FluxLoop packages with the commands below.');
        terminal.sendText('python -m venv .venv');
        if (process.platform === 'win32') {
            terminal.sendText('.\\\\.venv\\\\Scripts\\\\activate');
        } else {
            terminal.sendText('source .venv/bin/activate');
        }
        terminal.sendText('pip install fluxloop-cli fluxloop fluxloop-mcp');
        terminal.sendText('# After the installation completes, return to VS Code and choose Retry.');
        this.log(`[Project Init] Opened manual setup terminal at ${this.formatShortPath(root)}.`);
    }

    private showEnvironmentConfirmation(status: EnvironmentCheckResult): void {
        const python = status.pythonPath ? this.formatShortPath(status.pythonPath) : 'unknown';
        const fluxloop = status.fluxloopPath ? this.formatShortPath(status.fluxloopPath) : 'unknown';
        const mcp = status.fluxloopMcpPath ? this.formatShortPath(status.fluxloopMcpPath) : 'unknown';

        void vscode.window.showInformationMessage(
            `Environment ready: Python ${python}, fluxloop ${fluxloop}, fluxloop-mcp ${mcp}.`
        );
        this.log(`[Project Init] Environment confirmed: python=${python}, fluxloop=${fluxloop}, fluxloop-mcp=${mcp}`);
    }

    private async confirmGlobalUsage(): Promise<boolean> {
        const answer = await vscode.window.showWarningMessage(
            'Using the global PATH keeps FluxLoop CLI separate from this project environment. Continue?',
            { modal: true },
            'Continue',
            'Cancel'
        );
        if (answer === 'Continue') {
            this.log('[Project Init] User opted to proceed with global PATH.');
        }
        return answer === 'Continue';
    }

    private async applyEnvironmentSettings(projectRoot: string, choice: PreparedEnvironment): Promise<void> {
        const configUri = vscode.Uri.file(projectRoot);
        const configuration = vscode.workspace.getConfiguration('fluxloop', configUri);

        const applyWorkspaceSettings = async () => {
            if (choice.mode === 'workspace') {
                const targetSourceRoot = this.computeTargetSourceRoot(projectRoot, choice.root);
                await configuration.update('targetSourceRoot', targetSourceRoot, vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('executionMode', 'workspace', vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('pythonPath', undefined, vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('mcpCommandPath', undefined, vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('defaultEnvironment', 'Local Python', vscode.ConfigurationTarget.WorkspaceFolder);
                this.log(`[Project Init] Saved workspace environment settings (targetSourceRoot=${targetSourceRoot}).`);
                await this.updateProjectConfigSourceRoot(projectRoot, targetSourceRoot);
            } else {
                await configuration.update('targetSourceRoot', '', vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('executionMode', 'global', vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('defaultEnvironment', 'Global PATH', vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('pythonPath', undefined, vscode.ConfigurationTarget.WorkspaceFolder);
                await configuration.update('mcpCommandPath', undefined, vscode.ConfigurationTarget.WorkspaceFolder);
                this.log('[Project Init] Saved global execution mode for project.');
                await this.updateProjectConfigSourceRoot(projectRoot, '');
            }
        };

        try {
            await applyWorkspaceSettings();
        } catch (error) {
            this.log(`[Project Init] Workspace settings update failed, writing fallback file. ${String(error)}`);
            await this.writeSettingsFallback(projectRoot, choice);
        }
    }

    private computeTargetSourceRoot(projectRoot: string, environmentRoot: string): string {
        const normalizedProject = path.resolve(projectRoot);
        const normalizedEnvironment = path.resolve(environmentRoot);

        if (normalizedProject === normalizedEnvironment) {
            return '.';
        }

        if (normalizedEnvironment.startsWith(`${normalizedProject}${path.sep}`)) {
            const relative = path.relative(normalizedProject, normalizedEnvironment);
            return relative || '.';
        }

        return normalizedEnvironment;
    }

    private formatShortPath(targetPath: string): string {
        const normalized = path.resolve(targetPath);
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspaceFolder && normalized.startsWith(workspaceFolder)) {
            const relative = path.relative(workspaceFolder, normalized);
            return relative || '.';
        }
        return normalized;
    }

    private async runSetupScript(root: string): Promise<boolean> {
        if (process.platform === 'win32') {
            const proceed = await vscode.window.showInformationMessage(
                'The setup script is a Bash script. Make sure you have a Bash shell available (e.g. Git Bash). Continue?',
                'Continue',
                'Cancel'
            );
            if (proceed !== 'Continue') {
                return false;
            }
        }

        const scriptPath = this.findSetupScript(root);
        if (!scriptPath) {
            void vscode.window.showWarningMessage(
                'Could not locate setup_fluxloop_env.sh in this workspace. Please install the FluxLoop packages manually.'
            );
            this.log('[Project Init] setup_fluxloop_env.sh not found in workspace.');
            return false;
        }

        const targetArg = this.quotePath(root);
        const command = `bash ${this.quotePath(scriptPath)} --target-source-root ${targetArg}`;
        const terminal = vscode.window.createTerminal({
            name: 'FluxLoop Setup Script',
            cwd: path.dirname(scriptPath)
        });
        terminal.show();
        terminal.sendText(command);
        this.log(`[Project Init] Running setup script: ${command}`);

        void vscode.window.showInformationMessage('FluxLoop setup script started in a terminal. When it finishes, choose Retry to re-check the environment.');
        return true;
    }

    private findSetupScript(environmentRoot: string): string | undefined {
        const candidates = new Set<string>();
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspaceRoot) {
            candidates.add(path.join(workspaceRoot, 'packages', 'cli', 'scripts', 'setup_fluxloop_env.sh'));
            candidates.add(path.join(workspaceRoot, 'scripts', 'setup_fluxloop_env.sh'));
        }
        candidates.add(path.join(environmentRoot, 'scripts', 'setup_fluxloop_env.sh'));

        for (const candidate of candidates) {
            if (fs.existsSync(candidate)) {
                return candidate;
            }
        }
        return undefined;
    }

    private quotePath(value: string): string {
        if (value.includes(' ')) {
            return `"${value.replace(/"/g, '\\"')}"`;
        }
        return value;
    }

    private log(message: string): void {
        OutputChannelManager.getInstance().appendLine(message);
    }

    private async addExistingProject(): Promise<void> {
        const projectFolder = await vscode.window.showOpenDialog({
            canSelectFolders: true,
            canSelectFiles: false,
            canSelectMany: false,
            openLabel: 'Select FluxLoop Project Folder'
        });

        if (!projectFolder || projectFolder.length === 0) {
            return;
        }

        const projectPath = projectFolder[0].fsPath;

        if (!this.looksLikeFluxloopProject(projectPath)) {
            void vscode.window.showErrorMessage('Selected folder does not appear to be a FluxLoop project (configs/ missing).');
            return;
        }

        const inferredName = this.readProjectName(projectPath) ?? path.basename(projectPath);

        const projectName = await vscode.window.showInputBox({
            prompt: 'Project name',
            value: inferredName,
            validateInput: value => value ? undefined : 'Project name is required'
        });

        if (!projectName) {
            return;
        }

        ProjectManager.getInstance().addProject({ name: projectName, path: projectPath, setActive: true });
        vscode.window.showInformationMessage(`FluxLoop project "${projectName}" added.`);
    }

    private async selectProject(projectId?: string): Promise<void> {
        const manager = ProjectManager.getInstance();

        if (!projectId) {
            await this.showProjectQuickPick();
            return;
        }

        manager.setActiveProject(projectId);

        const project = manager.getProjectById(projectId);
        if (project) {
            vscode.window.showInformationMessage(`Active FluxLoop project set to ${project.name}`);
        }
    }

    private async showProjectQuickPick(): Promise<void> {
        const manager = ProjectManager.getInstance();
        const project = await this.pickProject('Select FluxLoop project');

        if (project) {
            manager.setActiveProject(project.id);
            vscode.window.showInformationMessage(`Active FluxLoop project set to ${project.name}`);
        }
    }

    private async removeProject(projectId?: string): Promise<void> {
        const manager = ProjectManager.getInstance();

        const targetProject = projectId
            ? manager.getProjectById(projectId)
            : await this.pickProject('Select a project to remove');

        if (!targetProject) {
            return;
        }

        const confirmation = await vscode.window.showWarningMessage(
            `Remove ${targetProject.name} from FluxLoop projects list?`,
            { modal: true },
            'Remove'
        );

        if (confirmation === 'Remove') {
            await manager.removeProject(targetProject.id);
        }
    }

    private async openProject(uri: vscode.Uri, newWindow: boolean): Promise<void> {
        await vscode.commands.executeCommand('vscode.openFolder', uri, newWindow);
    }

    private looksLikeFluxloopProject(projectPath: string): boolean {
        const configDir = path.join(projectPath, 'configs');
        const requiredFiles = ['project.yaml', 'input.yaml', 'simulation.yaml'];
        if (!fs.existsSync(configDir) || !fs.statSync(configDir).isDirectory()) {
            return false;
        }

        return requiredFiles.every(file => fs.existsSync(path.join(configDir, file)));
    }

    private resolvePathsForNewProject(selectedPath: string, projectName: string): { rootDir: string; projectRoot: string } {
        const normalized = path.resolve(selectedPath);
        // Always create the project inside the selected folder
        return {
            rootDir: normalized,
            projectRoot: path.join(normalized, projectName)
        };
    }

    private readProjectName(projectPath: string): string | undefined {
        try {
            const configPath = path.join(projectPath, 'configs', 'project.yaml');
            if (!fs.existsSync(configPath)) {
                return undefined;
            }

            const content = fs.readFileSync(configPath, 'utf-8');
            const data = yaml.parse(content) as { name?: string } | undefined;
            return data?.name;
        } catch (error) {
            console.warn('Failed to read project.yaml', error);
            return undefined;
        }
    }

    private async pickProject(placeHolder: string): Promise<ProjectEntry | undefined> {
        const manager = ProjectManager.getInstance();
        const projects = manager.getProjects();

        if (projects.length === 0) {
            const create = await vscode.window.showInformationMessage('No FluxLoop projects registered. Create one now?', 'Create Project', 'Add Existing');
            if (create === 'Create Project') {
                await this.createProject();
            } else if (create === 'Add Existing') {
                await this.addExistingProject();
            }
            return;
        }

        const activeProject = manager.getActiveProject();

        const pick = await vscode.window.showQuickPick(
            projects.map(project => ({
                label: project.name,
                description: project.path,
                detail: project.hasConfig ? undefined : 'Configs missing',
                picked: project.id === activeProject?.id,
                project
            })),
            {
                placeHolder
            }
        );

        return pick?.project;
    }

    private async writeSettingsFallback(projectRoot: string, choice: PreparedEnvironment): Promise<void> {
        try {
            const settingsDir = path.join(projectRoot, '.vscode');
            const settingsPath = path.join(settingsDir, 'settings.json');

            await fs.promises.mkdir(settingsDir, { recursive: true });

            let data: Record<string, unknown> = {};
            if (fs.existsSync(settingsPath)) {
                try {
                    const raw = await fs.promises.readFile(settingsPath, 'utf-8');
                    data = JSON.parse(raw) as Record<string, unknown>;
                } catch {
                    data = {};
                }
            }

            if (choice.mode === 'workspace') {
                const targetSourceRoot = this.computeTargetSourceRoot(projectRoot, choice.root);
                data['fluxloop.targetSourceRoot'] = targetSourceRoot;
                data['fluxloop.executionMode'] = 'workspace';
                delete data['fluxloop.pythonPath'];
                delete data['fluxloop.mcpCommandPath'];
                data['fluxloop.defaultEnvironment'] = 'Local Python';
                this.log(`[Project Init] Wrote fallback settings with targetSourceRoot=${targetSourceRoot}.`);
                await this.updateProjectConfigSourceRoot(projectRoot, targetSourceRoot);
            } else {
                data['fluxloop.targetSourceRoot'] = '';
                data['fluxloop.executionMode'] = 'global';
                delete data['fluxloop.pythonPath'];
                delete data['fluxloop.mcpCommandPath'];
                data['fluxloop.defaultEnvironment'] = 'Global PATH';
                this.log('[Project Init] Wrote fallback settings for global execution mode.');
                await this.updateProjectConfigSourceRoot(projectRoot, '');
            }

            await fs.promises.writeFile(settingsPath, `${JSON.stringify(data, null, 2)}\n`, 'utf-8');
        } catch (fallbackError) {
            this.log(`[Project Init] Failed to write fallback settings file: ${String(fallbackError)}`);
        }
    }

    private async updateProjectConfigSourceRoot(projectRoot: string, targetSourceRoot: string): Promise<void> {
        try {
            const configPath = path.join(projectRoot, 'configs', 'project.yaml');
            if (!fs.existsSync(configPath)) {
                return;
            }

            let normalized = targetSourceRoot;
            if (!normalized || normalized === '') {
                normalized = '.';
            } else if (path.isAbsolute(normalized)) {
                normalized = this.computeRelativeIfInside(projectRoot, normalized);
            }

            const raw = await fs.promises.readFile(configPath, 'utf-8');

            const normalizedValue = normalized.replace(/\\/g, '/');
            let updated: string;
            const sourcePattern = /^(\s*)source_root\s*:.*/m;
            if (sourcePattern.test(raw)) {
                updated = raw.replace(sourcePattern, (_match, indent = '') => `${indent}source_root: "${normalizedValue}"`);
            } else {
                const namePattern = /^(\s*name\s*:.*)$/m;
                if (namePattern.test(raw)) {
                    updated = raw.replace(namePattern, (line: string) => {
                        const indentMatch = line.match(/^(\s*)/);
                        const indent = indentMatch ? indentMatch[1] : '';
                        return `${line}\n${indent}source_root: "${normalizedValue}"`;
                    });
                } else {
                    updated = `${raw.trimEnd()}\nsource_root: "${normalizedValue}"\n`;
                }
            }

            if (!updated.endsWith('\n')) {
                updated += '\n';
            }

            await fs.promises.writeFile(configPath, updated, 'utf-8');
            this.log(`[Project Init] Updated configs/project.yaml source_root="${normalizedValue}".`);
        } catch (error) {
            this.log(`[Project Init] Failed to update project.yaml source_root: ${String(error)}`);
        }
    }

    private computeRelativeIfInside(projectRoot: string, targetPath: string): string {
        const normalizedProject = path.resolve(projectRoot);
        const normalizedTarget = path.resolve(targetPath);

        if (normalizedTarget.startsWith(`${normalizedProject}${path.sep}`) || normalizedTarget === normalizedProject) {
            const relative = path.relative(normalizedProject, normalizedTarget);
            return relative.length > 0 ? relative : '.';
        }
        return targetPath;
    }

    private async waitForProjectConfig(projectRoot: string, timeoutMs: number): Promise<void> {
        const configPath = path.join(projectRoot, 'configs', 'project.yaml');
        const start = Date.now();

        while (Date.now() - start < timeoutMs) {
            if (fs.existsSync(configPath)) {
                return;
            }
            await new Promise(resolve => setTimeout(resolve, 250));
        }

        this.log(`[Project Init] Timeout waiting for project.yaml at ${configPath}.`);
    }
}
