import * as vscode from 'vscode';

export class InteractiveWireframe {
    private _panel: vscode.WebviewPanel | undefined;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    createOrShow() {
        if (this._panel) {
            this._panel.reveal(vscode.ViewColumn.One);
        } else {
            this._panel = vscode.window.createWebviewPanel(
                'fluxloopInteractiveWireframe',
                'FluxLoop Interactive Wireframe',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')]
                }
            );
            
            this._panel.webview.html = this.getInteractiveHtml();
            this._panel.onDidDispose(() => this._panel = undefined);
        }
    }
    
    private getInteractiveHtml(): string {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FluxLoop Interactive Wireframe</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                    color: #333;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .header h1 {
                    margin: 0;
                    color: #2196f3;
                    font-size: 24px;
                }
                
                .header p {
                    margin: 10px 0 0 0;
                    color: #666;
                    font-size: 14px;
                }
                
                .interactive-container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                
                .sidebar {
                    width: 300px;
                    background: #f8f9fa;
                    border-right: 1px solid #e0e0e0;
                    height: 600px;
                    overflow-y: auto;
                    float: left;
                }
                
                .main-content {
                    margin-left: 300px;
                    padding: 20px;
                    height: 600px;
                    overflow-y: auto;
                }
                
                .panel-header {
                    background: #2196f3;
                    color: white;
                    padding: 15px 20px;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .panel-item {
                    padding: 12px 20px;
                    border-bottom: 1px solid #e0e0e0;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .panel-item:hover {
                    background: #e3f2fd;
                }
                
                .panel-item.active {
                    background: #bbdefb;
                    border-left: 4px solid #2196f3;
                }
                
                .panel-item-icon {
                    font-size: 16px;
                    margin-right: 8px;
                }
                
                .panel-item-label {
                    flex: 1;
                    font-size: 14px;
                }
                
                .panel-item-count {
                    background: #e0e0e0;
                    color: #666;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                }
                
                .panel-item.active .panel-item-count {
                    background: #2196f3;
                    color: white;
                }
                
                .content-area {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .content-title {
                    font-size: 18px;
                    font-weight: 500;
                    color: #333;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .content-description {
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 20px;
                    line-height: 1.5;
                }
                
                .action-buttons {
                    display: flex;
                    gap: 12px;
                    margin-bottom: 20px;
                }
                
                .btn {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .btn-primary {
                    background: #2196f3;
                    color: white;
                }
                
                .btn-primary:hover {
                    background: #1976d2;
                }
                
                .btn-secondary {
                    background: #f5f5f5;
                    color: #666;
                }
                
                .btn-secondary:hover {
                    background: #e0e0e0;
                }
                
                .btn-success {
                    background: #4caf50;
                    color: white;
                }
                
                .btn-success:hover {
                    background: #388e3c;
                }
                
                .btn-warning {
                    background: #ff9800;
                    color: white;
                }
                
                .btn-warning:hover {
                    background: #f57c00;
                }
                
                .status-indicator {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 12px;
                    border-radius: 16px;
                    font-size: 12px;
                    font-weight: 500;
                }
                
                .status-success {
                    background: #e8f5e8;
                    color: #2e7d32;
                }
                
                .status-error {
                    background: #ffebee;
                    color: #c62828;
                }
                
                .status-warning {
                    background: #fff3e0;
                    color: #ef6c00;
                }
                
                .status-info {
                    background: #e3f2fd;
                    color: #1565c0;
                }
                
                .status-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                }
                
                .status-success .status-dot {
                    background: #4caf50;
                }
                
                .status-error .status-dot {
                    background: #f44336;
                }
                
                .status-warning .status-dot {
                    background: #ff9800;
                }
                
                .status-info .status-dot {
                    background: #2196f3;
                }
                
                .progress-container {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background: #e0e0e0;
                    border-radius: 4px;
                    overflow: hidden;
                    margin: 10px 0;
                }
                
                .progress-fill {
                    height: 100%;
                    background: #2196f3;
                    transition: width 0.3s ease;
                }
                
                .progress-text {
                    font-size: 14px;
                    color: #666;
                    text-align: center;
                }
                
                .list-item {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 12px;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    margin-bottom: 8px;
                    transition: all 0.3s ease;
                }
                
                .list-item:hover {
                    border-color: #2196f3;
                    background: #f0f8ff;
                }
                
                .list-item-content {
                    flex: 1;
                }
                
                .list-item-title {
                    font-weight: 500;
                    color: #333;
                    margin-bottom: 4px;
                }
                
                .list-item-description {
                    font-size: 12px;
                    color: #666;
                }
                
                .list-item-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .btn-small {
                    padding: 6px 12px;
                    font-size: 12px;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 40px 20px;
                    color: #666;
                }
                
                .empty-state-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                    opacity: 0.5;
                }
                
                .empty-state-title {
                    font-size: 18px;
                    font-weight: 500;
                    margin-bottom: 8px;
                    color: #333;
                }
                
                .empty-state-description {
                    font-size: 14px;
                    margin-bottom: 20px;
                }
                
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 16px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    z-index: 1000;
                    transform: translateX(400px);
                    transition: transform 0.3s ease;
                }
                
                .notification.show {
                    transform: translateX(0);
                }
                
                .notification-header {
                    font-weight: 500;
                    margin-bottom: 8px;
                    color: #333;
                }
                
                .notification-message {
                    font-size: 14px;
                    color: #666;
                }
                
                .clearfix::after {
                    content: "";
                    display: table;
                    clear: both;
                }
                
                @media (max-width: 768px) {
                    .sidebar {
                        width: 100%;
                        height: auto;
                        float: none;
                    }
                    
                    .main-content {
                        margin-left: 0;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FluxLoop Interactive Wireframe</h1>
                <p>Fully interactive prototype with realistic UI behavior and state management</p>
            </div>
            
            <div class="interactive-container clearfix">
                <div class="sidebar">
                    <div class="panel-header">
                        <span>🧪</span>
                        <span>FluxLoop</span>
                    </div>
                    
                    <div class="panel-item active" data-panel="experiments">
                        <div>
                            <span class="panel-item-icon">🧪</span>
                            <span class="panel-item-label">Experiments</span>
                        </div>
                        <span class="panel-item-count">1</span>
                    </div>
                    
                    <div class="panel-item" data-panel="inputs">
                        <div>
                            <span class="panel-item-icon">📝</span>
                            <span class="panel-item-label">Inputs</span>
                        </div>
                        <span class="panel-item-count">3</span>
                    </div>
                    
                    <div class="panel-item" data-panel="personas">
                        <div>
                            <span class="panel-item-icon">👥</span>
                            <span class="panel-item-label">Personas</span>
                        </div>
                        <span class="panel-item-count">2</span>
                    </div>
                    
                    <div class="panel-item" data-panel="results">
                        <div>
                            <span class="panel-item-icon">📊</span>
                            <span class="panel-item-label">Results</span>
                        </div>
                        <span class="panel-item-count">1</span>
                    </div>
                    
                    <div class="panel-item" data-panel="status">
                        <div>
                            <span class="panel-item-icon">ℹ️</span>
                            <span class="panel-item-label">Status</span>
                        </div>
                        <span class="panel-item-count">4</span>
                    </div>
                </div>
                
                <div class="main-content">
                    <!-- Experiments Panel -->
                    <div class="content-area" id="experiments-content">
                        <div class="content-title">
                            <span>🧪</span>
                            <span>Experiments</span>
                        </div>
                        <div class="content-description">
                            Manage your AI agent experiments and configurations
                        </div>
                        
                        <div class="action-buttons">
                            <button class="btn btn-primary" onclick="showNotification('Initialize Project', 'Opening project initialization dialog...')">Initialize Project</button>
                            <button class="btn btn-secondary" onclick="showNotification('Open Config', 'Opening configs/simulation.yaml in editor...')">Open Config</button>
                            <button class="btn btn-success" onclick="startExperiment()">Run Experiment</button>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">pluto_experiment</div>
                                <div class="list-item-description">Current experiment configuration</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('Edit Config', 'Opening configuration editor...')">Edit</button>
                                <button class="btn btn-success btn-small" onclick="startExperiment()">Run</button>
                            </div>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">Results History</div>
                                <div class="list-item-description">experiment_20241201_143022</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('View Results', 'Opening results viewer...')">View</button>
                                <button class="btn btn-warning btn-small" onclick="showNotification('Parse Results', 'Converting to markdown...')">Parse</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Inputs Panel -->
                    <div class="content-area" id="inputs-content" style="display: none;">
                        <div class="content-title">
                            <span>📝</span>
                            <span>Inputs</span>
                        </div>
                        <div class="content-description">
                            Manage base inputs and generated variations
                        </div>
                        
                        <div class="action-buttons">
                            <button class="btn btn-primary" onclick="showNotification('Generate Inputs', 'Opening input generation wizard...')">Generate Inputs</button>
                            <button class="btn btn-secondary" onclick="showNotification('Import Inputs', 'Opening file picker...')">Import</button>
                            <button class="btn btn-success" onclick="showNotification('Record Session', 'Starting recording...')">Record</button>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">Base Inputs</div>
                                <div class="list-item-description">3 base input files</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('Edit Inputs', 'Opening input editor...')">Edit</button>
                                <button class="btn btn-primary btn-small" onclick="showNotification('Add Input', 'Opening input form...')">Add</button>
                            </div>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">Generated Inputs</div>
                                <div class="list-item-description">generated_20241201.yaml</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('View Generated', 'Opening generated inputs...')">View</button>
                                <button class="btn btn-warning btn-small" onclick="showNotification('Regenerate', 'Regenerating inputs...')">Regenerate</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Personas Panel -->
                    <div class="content-area" id="personas-content" style="display: none;">
                        <div class="content-title">
                            <span>👥</span>
                            <span>Personas</span>
                        </div>
                        <div class="content-description">
                            Define user personas for input generation
                        </div>
                        
                        <div class="action-buttons">
                            <button class="btn btn-primary" onclick="showNotification('Add Persona', 'Opening persona editor...')">Add Persona</button>
                            <button class="btn btn-secondary" onclick="showNotification('Import Personas', 'Opening file picker...')">Import</button>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">novice_user</div>
                                <div class="list-item-description">Beginner user with basic knowledge</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('Edit Persona', 'Opening persona editor...')">Edit</button>
                                <button class="btn btn-warning btn-small" onclick="showNotification('Test Persona', 'Running test with this persona...')">Test</button>
                            </div>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">expert_user</div>
                                <div class="list-item-description">Advanced user with deep expertise</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('Edit Persona', 'Opening persona editor...')">Edit</button>
                                <button class="btn btn-warning btn-small" onclick="showNotification('Test Persona', 'Running test with this persona...')">Test</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Results Panel -->
                    <div class="content-area" id="results-content" style="display: none;">
                        <div class="content-title">
                            <span>📊</span>
                            <span>Results</span>
                        </div>
                        <div class="content-description">
                            View and analyze experiment results
                        </div>
                        
                        <div class="action-buttons">
                            <button class="btn btn-primary" onclick="showNotification('Open Results', 'Opening results viewer...')">Open Results</button>
                            <button class="btn btn-secondary" onclick="showNotification('Export Results', 'Exporting to CSV...')">Export</button>
                            <button class="btn btn-success" onclick="showNotification('Compare Results', 'Opening comparison view...')">Compare</button>
                        </div>
                        
                        <div class="list-item">
                            <div class="list-item-content">
                                <div class="list-item-title">pluto_experiment_20241201_143022</div>
                                <div class="list-item-description">50 runs, 87% success rate, 2.3s avg duration</div>
                            </div>
                            <div class="list-item-actions">
                                <button class="btn btn-secondary btn-small" onclick="showNotification('View Details', 'Opening detailed results...')">View</button>
                                <button class="btn btn-warning btn-small" onclick="showNotification('Parse Results', 'Converting to markdown...')">Parse</button>
                            </div>
                        </div>
                        
                        <div class="status-indicator status-success">
                            <div class="status-dot"></div>
                            <span>Experiment completed successfully</span>
                        </div>
                    </div>
                    
                    <!-- Status Panel -->
                    <div class="content-area" id="status-content" style="display: none;">
                        <div class="content-title">
                            <span>ℹ️</span>
                            <span>Status</span>
                        </div>
                        <div class="content-description">
                            System status and configuration
                        </div>
                        
                        <div class="status-indicator status-success">
                            <div class="status-dot"></div>
                            <span>CLI: Installed (v1.2.3)</span>
                        </div>
                        
                        <div class="status-indicator status-info">
                            <div class="status-dot"></div>
                            <span>SDK: Check in terminal</span>
                        </div>
                        
                        <div class="status-indicator status-success">
                            <div class="status-dot"></div>
                            <span>Collector: http://localhost:8000</span>
                        </div>
                        
                        <div class="status-indicator status-success">
                            <div class="status-dot"></div>
                            <span>Config: configs/simulation.yaml found</span>
                        </div>
                        
                        <div class="status-indicator status-warning">
                            <div class="status-dot"></div>
                            <span>Docker: Not available</span>
                        </div>
                        
                        <div class="action-buttons">
                            <button class="btn btn-primary" onclick="showNotification('Check Status', 'Checking system status...')">Check Status</button>
                            <button class="btn btn-secondary" onclick="showNotification('View Logs', 'Opening system logs...')">View Logs</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Notification -->
            <div class="notification" id="notification">
                <div class="notification-header" id="notification-header">Notification</div>
                <div class="notification-message" id="notification-message">This is a notification message</div>
            </div>
            
            <script>
                let currentPanel = 'experiments';
                let experimentRunning = false;
                
                // Panel switching
                document.querySelectorAll('.panel-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const panel = this.dataset.panel;
                        switchPanel(panel);
                    });
                });
                
                function switchPanel(panel) {
                    // Update active panel item
                    document.querySelectorAll('.panel-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    document.querySelector(\`[data-panel="\${panel}"]\`).classList.add('active');
                    
                    // Update content
                    document.querySelectorAll('.content-area').forEach(content => {
                        content.style.display = 'none';
                    });
                    document.getElementById(\`\${panel}-content\`).style.display = 'block';
                    
                    currentPanel = panel;
                }
                
                // Notification system
                function showNotification(title, message) {
                    const notification = document.getElementById('notification');
                    const header = document.getElementById('notification-header');
                    const messageEl = document.getElementById('notification-message');
                    
                    header.textContent = title;
                    messageEl.textContent = message;
                    
                    notification.classList.add('show');
                    
                    setTimeout(() => {
                        notification.classList.remove('show');
                    }, 3000);
                }
                
                // Experiment simulation
                function startExperiment() {
                    if (experimentRunning) {
                        showNotification('Experiment Running', 'An experiment is already running');
                        return;
                    }
                    
                    experimentRunning = true;
                    showNotification('Starting Experiment', 'Initializing experiment...');
                    
                    // Simulate experiment progress
                    setTimeout(() => {
                        showNotification('Experiment Started', 'Running 50 iterations...');
                        simulateProgress();
                    }, 1000);
                }
                
                function simulateProgress() {
                    let progress = 0;
                    const interval = setInterval(() => {
                        progress += Math.random() * 10;
                        if (progress >= 100) {
                            progress = 100;
                            clearInterval(interval);
                            experimentRunning = false;
                            showNotification('Experiment Complete', 'All 50 runs completed successfully');
                            
                            // Update results count
                            const resultsCount = document.querySelector('[data-panel="results"] .panel-item-count');
                            resultsCount.textContent = '2';
                        } else {
                            showNotification('Experiment Progress', \`\${Math.round(progress)}% complete\`);
                        }
                    }, 2000);
                }
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    showNotification('Welcome', 'Interactive wireframe loaded successfully');
                });
            </script>
        </body>
        </html>
        `;
    }
}
