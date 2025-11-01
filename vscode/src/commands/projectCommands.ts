import * as vscode from 'vscode';
import * as path from 'path';
import { ProjectManager } from '../project/projectManager';
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
            openLabel: 'Select Project Folder'
        });

        if (!projectFolder || projectFolder.length === 0) {
            return;
        }

        const projectPath = projectFolder[0].fsPath;
        const defaultName = path.basename(projectPath);

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

        const args = ['init', 'project', projectPath, '--name', projectName];
        if (includeExample === 'Skip example agent') {
            args.push('--no-example');
        }

        await this.cliManager.runCommand(args, projectPath);

        const manager = ProjectManager.getInstance();
        const projectRoot = path.join(projectPath, projectName);
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
        const projectName = await vscode.window.showInputBox({
            prompt: 'Project name',
            value: path.basename(projectPath),
            validateInput: value => value ? undefined : 'Project name is required'
        });

        if (!projectName) {
            return;
        }

        ProjectManager.getInstance().addProject({ name: projectName, path: projectPath, setActive: true });
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
                detail: project.hasConfig ? undefined : 'No setting.yaml detected',
                picked: project.id === activeProject?.id,
                projectId: project.id
            })),
            {
                placeHolder: 'Select FluxLoop project'
            }
        );

        if (pick?.projectId) {
            manager.setActiveProject(pick.projectId);
        }
    }

    private async removeProject(projectId?: string): Promise<void> {
        const manager = ProjectManager.getInstance();
        const targetProject = projectId ? manager.getProjectById(projectId) : undefined;

        if (!targetProject) {
            await this.showProjectQuickPick();
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
}


