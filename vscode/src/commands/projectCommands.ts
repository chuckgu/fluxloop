import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as yaml from 'yaml';
import { ProjectManager, ProjectEntry } from '../project/projectManager';
import { ProjectContext } from '../project/projectContext';
import { CLIManager } from '../cli/cliManager';

export class ProjectCommands {
    constructor(
        private readonly context: vscode.ExtensionContext,
        private readonly cliManager: CLIManager
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

        const defaultName = path.basename(selectedPath);

        const projectName = await vscode.window.showInputBox({
            prompt: 'Project name',
            value: defaultName,
            validateInput: value => value ? undefined : 'Project name is required'
        });

        if (!projectName) {
            return;
        }

        const includeExample = await vscode.window.showQuickPick(['Include example agent', 'Skip example agent'], {
            placeHolder: 'Would you like to include the example agent?'
        });

        const { rootDir, projectRoot } = this.resolvePathsForNewProject(selectedPath, projectName);

        const args = ['init', 'project', rootDir, '--name', projectName];
        if (includeExample === 'Skip example agent') {
            args.push('--no-example');
        }

        await this.cliManager.runCommand(args, rootDir);

        if (!this.looksLikeFluxloopProject(projectRoot)) {
            void vscode.window.showWarningMessage('Project initialized, but expected FluxLoop config files were not found. Please check the CLI output.');
        }

        const manager = ProjectManager.getInstance();
        manager.addProject({ name: projectName, path: projectRoot, setActive: true });

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
        const baseName = path.basename(normalized);

        if (baseName === projectName) {
            const parentDir = path.dirname(normalized);
            return {
                rootDir: parentDir,
                projectRoot: normalized
            };
        }

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
}


