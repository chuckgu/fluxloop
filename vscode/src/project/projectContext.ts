import * as vscode from 'vscode';
import * as path from 'path';
import { ProjectManager, ProjectEntry } from './projectManager';

export class ProjectContext {
    private static statusBarItem: vscode.StatusBarItem | undefined;

    static initialize(context: vscode.ExtensionContext): void {
        if (!this.statusBarItem) {
            this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
            this.statusBarItem.tooltip = 'Active FluxLoop project';
            this.statusBarItem.command = 'fluxloop.selectProject';
            context.subscriptions.push(this.statusBarItem);
        }

        const projectManager = ProjectManager.getInstance();

        const updateStatusBar = (project: ProjectEntry | undefined) => {
            if (!this.statusBarItem) {
                return;
            }

            if (project) {
                this.statusBarItem.text = `FluxLoop: ${project.name}`;
                this.statusBarItem.show();
            } else {
                this.statusBarItem.text = 'FluxLoop: No Project';
                this.statusBarItem.show();
            }
        };

        updateStatusBar(projectManager.getActiveProject());
        projectManager.onDidChangeActiveProject(updateStatusBar);
    }

    static getActiveProject(): ProjectEntry | undefined {
        return ProjectManager.getInstance().getActiveProject();
    }

    static getActiveWorkspacePath(): string | undefined {
        const project = this.getActiveProject();
        if (!project) {
            return undefined;
        }

        if (project.sourceRoot) {
            if (path.isAbsolute(project.sourceRoot)) {
                return project.sourceRoot;
            }
            return path.resolve(project.path, project.sourceRoot);
        }

        return project.path;
    }

    static ensureActiveProject(): ProjectEntry | undefined {
        const project = this.getActiveProject();
        if (!project) {
            void vscode.window.showWarningMessage('Select a FluxLoop project to continue.', 'Select Project', 'Create Project').then(selection => {
                if (selection === 'Select Project') {
                    void vscode.commands.executeCommand('fluxloop.selectProject');
                } else if (selection === 'Create Project') {
                    void vscode.commands.executeCommand('fluxloop.createProject');
                }
            });
        }

        return project;
    }
}


