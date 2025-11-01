import * as vscode from 'vscode';
import * as path from 'path';
import { ProjectEntry, ProjectManager } from '../project/projectManager';

export class ProjectsProvider implements vscode.TreeDataProvider<ProjectTreeItem> {
    private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor() {
        const projectManager = ProjectManager.getInstance();
        projectManager.onDidChangeProjects(() => this.refresh());
        projectManager.onDidChangeActiveProject(() => this.refresh());
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ProjectTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ProjectTreeItem): vscode.ProviderResult<ProjectTreeItem[]> {
        if (element) {
            return this.getProjectChildren(element);
        }

        const projectManager = ProjectManager.getInstance();
        const projects = projectManager.getProjects();

        if (projects.length === 0) {
            return this.getEmptyStateItems();
        }

        const activeProject = projectManager.getActiveProject();

        const createItem = new CommandTreeItem('Create New Project…', 'Create a new FluxLoop project', '$(add)', {
            command: 'fluxloop.createProject',
            title: 'Create FluxLoop Project'
        });
        const addItem = new CommandTreeItem('Add Existing Project…', 'Add an existing FluxLoop project folder', '$(folder-opened)', {
            command: 'fluxloop.addProject',
            title: 'Add Existing FluxLoop Project'
        });

        const projectItems = projects.map(project => this.toProjectItem(project, project.id === activeProject?.id));

        return [createItem, addItem, ...projectItems];
    }

    private getProjectChildren(element: ProjectTreeItem): vscode.ProviderResult<ProjectTreeItem[]> {
        if (!element.project) {
            return [];
        }

        const project = element.project;
        const projectUri = vscode.Uri.file(project.path);

        return [
            new CommandTreeItem('Open in Current Window', undefined, '$(folder)', {
                command: 'fluxloop.openProject',
                title: 'Open Project in Current Window',
                arguments: [projectUri, false]
            }),
            new CommandTreeItem('Open in New Window', undefined, '$(window)', {
                command: 'fluxloop.openProject',
                title: 'Open Project in New Window',
                arguments: [projectUri, true]
            }),
            new CommandTreeItem('Set Active Project', undefined, '$(check)', {
                command: 'fluxloop.selectProject',
                title: 'Set Active FluxLoop Project',
                arguments: [project.id]
            }),
            new CommandTreeItem('Configure Project', undefined, '$(gear)', {
                command: 'fluxloop.openConfig',
                title: 'Open FluxLoop Configuration',
                arguments: [project.id]
            }),
            new CommandTreeItem('Run Experiment', undefined, '$(beaker)', {
                command: 'fluxloop.runExperiment',
                title: 'Run FluxLoop Experiment'
            }),
            new CommandTreeItem('Remove from List', undefined, '$(trash)', {
                command: 'fluxloop.removeProject',
                title: 'Remove FluxLoop Project',
                arguments: [project.id]
            })
        ];
    }

    private getEmptyStateItems(): ProjectTreeItem[] {
        const emptyItem = new ProjectTreeItem(
            'No projects found',
            'Create or add a FluxLoop project to get started',
            { type: 'info' }
        );
        emptyItem.iconPath = new vscode.ThemeIcon('info');

        const createItem = new CommandTreeItem('Create Project…', undefined, '$(add)', {
            command: 'fluxloop.createProject',
            title: 'Create FluxLoop Project'
        });

        const addItem = new CommandTreeItem('Add Existing Project…', undefined, '$(folder-opened)', {
            command: 'fluxloop.addProject',
            title: 'Add Existing FluxLoop Project'
        });

        return [emptyItem, createItem, addItem];
    }

    private toProjectItem(project: ProjectEntry, isActive: boolean): ProjectTreeItem {
        const descriptionParts = [path.basename(project.path)];

        if (!project.hasConfig) {
            descriptionParts.push('Configs missing');
        }

        const item = new ProjectTreeItem(
            isActive ? `${project.name} (active)` : project.name,
            descriptionParts.join(' • '),
            { project }
        );

        item.iconPath = new vscode.ThemeIcon(isActive ? 'verified' : 'folder');
        item.contextValue = `project${isActive ? '.active' : ''}`;

        item.command = {
            command: 'fluxloop.selectProject',
            title: 'Select Project',
            arguments: [project.id]
        };

        return item;
    }
}

class ProjectTreeItem extends vscode.TreeItem {
    constructor(
        label: string,
        description?: string,
        options?: { project?: ProjectEntry; type?: 'info' }
    ) {
        super(label, options?.project ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None);

        this.description = description;
        this.project = options?.project;
    }

    project?: ProjectEntry;
}

class CommandTreeItem extends ProjectTreeItem {
    constructor(
        label: string,
        description: string | undefined,
        iconId: string,
        command: vscode.Command
    ) {
        super(label, description);
        this.iconPath = new vscode.ThemeIcon(iconId.replace(/\$\(|\)$/g, ''));
        this.command = command;
    }
}


