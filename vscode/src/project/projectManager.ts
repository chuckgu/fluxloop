import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface ProjectEntry {
    id: string;
    name: string;
    path: string;
    lastOpened: number;
    hasConfig: boolean;
}

const PROJECTS_KEY = 'fluxloop.projects';
const ACTIVE_PROJECT_KEY = 'fluxloop.activeProjectId';

export class ProjectManager {
    private static instance: ProjectManager | undefined;

    private projects: ProjectEntry[] = [];
    private activeProjectId: string | undefined;

    private readonly _onDidChangeProjects = new vscode.EventEmitter<void>();
    private readonly _onDidChangeActiveProject = new vscode.EventEmitter<ProjectEntry | undefined>();

    private constructor(private readonly context: vscode.ExtensionContext) {
        this.loadState();
    }

    static initialize(context: vscode.ExtensionContext): ProjectManager {
        if (!this.instance) {
            this.instance = new ProjectManager(context);
        }

        return this.instance;
    }

    static getInstance(): ProjectManager {
        if (!this.instance) {
            throw new Error('ProjectManager has not been initialized');
        }

        return this.instance;
    }

    get onDidChangeProjects(): vscode.Event<void> {
        return this._onDidChangeProjects.event;
    }

    get onDidChangeActiveProject(): vscode.Event<ProjectEntry | undefined> {
        return this._onDidChangeActiveProject.event;
    }

    getProjects(): ProjectEntry[] {
        this.refreshProjectMetadata();

        return [...this.projects].sort((a, b) => {
            if (a.lastOpened === b.lastOpened) {
                return a.name.localeCompare(b.name);
            }
            return b.lastOpened - a.lastOpened;
        });
    }

    getProjectById(id: string): ProjectEntry | undefined {
        return this.projects.find(project => project.id === id);
    }

    getProjectByPath(projectPath: string): ProjectEntry | undefined {
        const normalized = path.resolve(projectPath);
        return this.projects.find(project => path.resolve(project.path) === normalized);
    }

    getActiveProject(): ProjectEntry | undefined {
        if (!this.activeProjectId) {
            return undefined;
        }

        return this.getProjectById(this.activeProjectId);
    }

    addProject(options: { name: string; path: string; setActive?: boolean }): ProjectEntry {
        const normalizedPath = path.resolve(options.path);
        const existing = this.getProjectByPath(normalizedPath);
        const setActive = options.setActive ?? true;
        const now = Date.now();
        let entry: ProjectEntry;

        if (existing) {
            entry = {
                ...existing,
                name: options.name,
                path: normalizedPath,
                lastOpened: now,
                hasConfig: this.computeHasConfig(normalizedPath)
            };

            const index = this.projects.findIndex(project => project.id === existing.id);
            this.projects[index] = entry;
        } else {
            entry = {
                id: this.generateId(),
                name: options.name,
                path: normalizedPath,
                lastOpened: now,
                hasConfig: this.computeHasConfig(normalizedPath)
            };

            this.projects.push(entry);
        }

        if (setActive) {
            this.setActiveProject(entry.id);
        } else {
            void this.persistState();
            this._onDidChangeProjects.fire();
        }

        return entry;
    }

    async removeProject(projectId: string): Promise<void> {
        const index = this.projects.findIndex(project => project.id === projectId);
        if (index === -1) {
            return;
        }

        this.projects.splice(index, 1);

        if (this.activeProjectId === projectId) {
            this.activeProjectId = this.projects[0]?.id;
            this._onDidChangeActiveProject.fire(this.getActiveProject());
        }

        await this.persistState();
        this._onDidChangeProjects.fire();
    }

    setActiveProject(projectId: string | undefined): void {
        if (projectId === this.activeProjectId) {
            return;
        }

        this.activeProjectId = projectId;

        if (projectId) {
            const project = this.getProjectById(projectId);
            if (project) {
                project.lastOpened = Date.now();
                project.hasConfig = this.computeHasConfig(project.path);
            }
        }

        void this.persistState();
        this._onDidChangeActiveProject.fire(this.getActiveProject());
        this._onDidChangeProjects.fire();
    }

    refreshProjectById(projectId: string): void {
        const project = this.getProjectById(projectId);
        if (!project) {
            return;
        }

        const hasConfig = this.computeHasConfig(project.path);
        if (project.hasConfig !== hasConfig) {
            project.hasConfig = hasConfig;
            void this.persistState();
            this._onDidChangeProjects.fire();
        }
    }

    private loadState(): void {
        const storedProjects = this.context.globalState.get<ProjectEntry[]>(PROJECTS_KEY, []);
        const storedActiveProject = this.context.globalState.get<string | undefined>(ACTIVE_PROJECT_KEY);

        this.projects = storedProjects.map(project => ({
            ...project,
            lastOpened: project.lastOpened ?? Date.now(),
            hasConfig: this.computeHasConfig(project.path)
        }));

        this.activeProjectId = storedActiveProject;
    }

    private async persistState(): Promise<void> {
        await this.context.globalState.update(PROJECTS_KEY, this.projects);
        await this.context.globalState.update(ACTIVE_PROJECT_KEY, this.activeProjectId);
    }

    private refreshProjectMetadata(): void {
        let hasChanges = false;

        this.projects = this.projects.map(project => {
            const hasConfig = this.computeHasConfig(project.path);
            if (hasConfig !== project.hasConfig) {
                hasChanges = true;
                return { ...project, hasConfig };
            }
            return project;
        });

        if (hasChanges) {
            void this.persistState();
        }
    }

    private computeHasConfig(projectPath: string): boolean {
        const configDir = path.join(projectPath, 'configs');
        const requiredConfigFiles = ['project.yaml', 'input.yaml', 'simulation.yaml'];

        if (fs.existsSync(configDir) && fs.statSync(configDir).isDirectory()) {
            const hasRequired = requiredConfigFiles.every(file =>
                fs.existsSync(path.join(configDir, file))
            );

            if (hasRequired) {
                return true;
            }
        }

        return false;
    }

    private generateId(): string {
        return `project-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }
}


