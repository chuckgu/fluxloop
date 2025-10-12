import * as vscode from 'vscode';

export class WebviewsWireframe {
    private _panel: vscode.WebviewPanel | undefined;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    createOrShow() {
        if (this._panel) {
            this._panel.reveal(vscode.ViewColumn.One);
        } else {
            this._panel = vscode.window.createWebviewPanel(
                'fluxloopWebviewsWireframe',
                'FluxLoop Webviews Wireframe',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')]
                }
            );
            
            this._panel.webview.html = this.getWebviewsHtml();
            this._panel.onDidDispose(() => this._panel = undefined);
        }
    }
    
    private getWebviewsHtml(): string {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FluxLoop Webviews Wireframe</title>
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
                
                .webviews-container {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    max-width: 1400px;
                    margin: 0 auto;
                }
                
                .webview-card {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    overflow: hidden;
                    transition: transform 0.3s ease;
                }
                
                .webview-card:hover {
                    transform: translateY(-2px);
                }
                
                .webview-header {
                    background: linear-gradient(135deg, #2196f3, #1976d2);
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                
                .webview-header h2 {
                    margin: 0;
                    font-size: 18px;
                    font-weight: 300;
                }
                
                .webview-content {
                    padding: 30px;
                    height: 600px;
                    overflow-y: auto;
                }
                
                .tab-container {
                    display: flex;
                    border-bottom: 2px solid #e0e0e0;
                    margin-bottom: 20px;
                }
                
                .tab {
                    padding: 12px 20px;
                    background: #f5f5f5;
                    border: none;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    color: #666;
                    transition: all 0.3s ease;
                    border-radius: 8px 8px 0 0;
                    margin-right: 4px;
                }
                
                .tab.active {
                    background: #2196f3;
                    color: white;
                }
                
                .tab-content {
                    display: none;
                }
                
                .tab-content.active {
                    display: block;
                }
                
                .form-group {
                    margin-bottom: 20px;
                }
                
                .form-label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 500;
                    color: #333;
                }
                
                .form-input {
                    width: 100%;
                    padding: 12px 16px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: border-color 0.3s ease;
                    box-sizing: border-box;
                }
                
                .form-input:focus {
                    outline: none;
                    border-color: #2196f3;
                }
                
                .form-textarea {
                    width: 100%;
                    padding: 12px 16px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                    transition: border-color 0.3s ease;
                    box-sizing: border-box;
                    resize: vertical;
                    min-height: 100px;
                }
                
                .form-textarea:focus {
                    outline: none;
                    border-color: #2196f3;
                }
                
                .form-select {
                    width: 100%;
                    padding: 12px 16px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    background: white;
                    cursor: pointer;
                    box-sizing: border-box;
                }
                
                .btn {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin-right: 8px;
                    margin-bottom: 8px;
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
                
                .btn-danger {
                    background: #f44336;
                    color: white;
                }
                
                .btn-danger:hover {
                    background: #d32f2f;
                }
                
                .btn-success {
                    background: #4caf50;
                    color: white;
                }
                
                .btn-success:hover {
                    background: #388e3c;
                }
                
                .list-item {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 12px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
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
                
                .timeline {
                    position: relative;
                    padding-left: 30px;
                }
                
                .timeline::before {
                    content: '';
                    position: absolute;
                    left: 15px;
                    top: 0;
                    bottom: 0;
                    width: 2px;
                    background: #e0e0e0;
                }
                
                .timeline-item {
                    position: relative;
                    margin-bottom: 20px;
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .timeline-item::before {
                    content: '';
                    position: absolute;
                    left: -22px;
                    top: 20px;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #2196f3;
                    border: 3px solid white;
                }
                
                .timeline-item.success::before {
                    background: #4caf50;
                }
                
                .timeline-item.error::before {
                    background: #f44336;
                }
                
                .timeline-item.warning::before {
                    background: #ff9800;
                }
                
                .timeline-title {
                    font-weight: 500;
                    color: #333;
                    margin-bottom: 4px;
                }
                
                .timeline-time {
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 8px;
                }
                
                .timeline-content {
                    font-size: 14px;
                    color: #555;
                }
                
                .chart-container {
                    height: 200px;
                    background: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    font-style: italic;
                }
                
                .metric-card {
                    background: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 16px;
                }
                
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2196f3;
                    margin-bottom: 4px;
                }
                
                .metric-label {
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                }
                
                .help-text {
                    font-size: 12px;
                    color: #666;
                    margin-top: 4px;
                }
                
                .error-message {
                    color: #f44336;
                    font-size: 12px;
                    margin-top: 4px;
                }
                
                .success-message {
                    color: #4caf50;
                    font-size: 12px;
                    margin-top: 4px;
                }
                
                .warning-box {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    font-size: 14px;
                    color: #856404;
                }
                
                .warning-box::before {
                    content: '⚠️ ';
                    font-size: 16px;
                }
                
                .info-box {
                    background: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    font-size: 14px;
                    color: #0c5460;
                }
                
                .info-box::before {
                    content: 'ℹ️ ';
                    font-size: 16px;
                }
                
                @media (max-width: 768px) {
                    .webviews-container {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FluxLoop Webviews Wireframe</h1>
                <p>Interactive prototypes of webview panels and editors</p>
            </div>
            
            <div class="webviews-container">
                <!-- Config Editor Webview -->
                <div class="webview-card">
                    <div class="webview-header">
                        <h2>⚙️ Configuration Editor</h2>
                    </div>
                    <div class="webview-content">
                        <div class="tab-container">
                            <button class="tab active" onclick="switchTab('config-basic')">Basic</button>
                            <button class="tab" onclick="switchTab('config-personas')">Personas</button>
                            <button class="tab" onclick="switchTab('config-inputs')">Inputs</button>
                            <button class="tab" onclick="switchTab('config-variations')">Variations</button>
                            <button class="tab" onclick="switchTab('config-runner')">Runner</button>
                        </div>
                        
                        <!-- Basic Tab -->
                        <div class="tab-content active" id="config-basic">
                            <div class="form-group">
                                <label class="form-label">Experiment Name</label>
                                <input type="text" class="form-input" value="pluto_experiment">
                                <div class="help-text">Name for this experiment configuration</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Description</label>
                                <textarea class="form-textarea" placeholder="Describe what this experiment tests...">Test the pluto agent with various user personas and input variations to evaluate performance across different scenarios.</textarea>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Version</label>
                                <input type="text" class="form-input" value="1.0.0">
                                <div class="help-text">Version of this configuration</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Iterations</label>
                                <input type="number" class="form-input" value="10" min="1" max="1000">
                                <div class="help-text">Number of times to run each input variation</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Parallel Runs</label>
                                <input type="number" class="form-input" value="1" min="1" max="10">
                                <div class="help-text">Number of parallel executions</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Seed (Optional)</label>
                                <input type="number" class="form-input" value="" placeholder="Random seed for reproducible results">
                                <div class="help-text">Leave empty for random seed</div>
                            </div>
                        </div>
                        
                        <!-- Personas Tab -->
                        <div class="tab-content" id="config-personas">
                            <div class="form-group">
                                <button class="btn btn-primary" onclick="showDialog('Add Persona')">Add Persona</button>
                            </div>
                            
                            <div class="list-item">
                                <div class="list-item-content">
                                    <div class="list-item-title">novice_user</div>
                                    <div class="list-item-description">Beginner user with basic knowledge</div>
                                </div>
                                <div class="list-item-actions">
                                    <button class="btn btn-secondary btn-small" onclick="showDialog('Edit Persona')">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="showDialog('Delete Persona')">Delete</button>
                                </div>
                            </div>
                            
                            <div class="list-item">
                                <div class="list-item-content">
                                    <div class="list-item-title">expert_user</div>
                                    <div class="list-item-description">Advanced user with deep expertise</div>
                                </div>
                                <div class="list-item-actions">
                                    <button class="btn btn-secondary btn-small" onclick="showDialog('Edit Persona')">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="showDialog('Delete Persona')">Delete</button>
                                </div>
                            </div>
                            
                            <div class="list-item">
                                <div class="list-item-content">
                                    <div class="list-item-title">casual_user</div>
                                    <div class="list-item-description">Occasional user, simple requests</div>
                                </div>
                                <div class="list-item-actions">
                                    <button class="btn btn-secondary btn-small" onclick="showDialog('Edit Persona')">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="showDialog('Delete Persona')">Delete</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Inputs Tab -->
                        <div class="tab-content" id="config-inputs">
                            <div class="form-group">
                                <button class="btn btn-primary" onclick="showDialog('Add Base Input')">Add Base Input</button>
                                <button class="btn btn-secondary" onclick="showDialog('Import Inputs')">Import from File</button>
                            </div>
                            
                            <div class="list-item">
                                <div class="list-item-content">
                                    <div class="list-item-title">input_001</div>
                                    <div class="list-item-description">"Help me understand how to use this system"</div>
                                </div>
                                <div class="list-item-actions">
                                    <button class="btn btn-secondary btn-small" onclick="showDialog('Edit Input')">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="showDialog('Delete Input')">Delete</button>
                                </div>
                            </div>
                            
                            <div class="list-item">
                                <div class="list-item-content">
                                    <div class="list-item-title">input_002</div>
                                    <div class="list-item-description">"What are the main features available?"</div>
                                </div>
                                <div class="list-item-actions">
                                    <button class="btn btn-secondary btn-small" onclick="showDialog('Edit Input')">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="showDialog('Delete Input')">Delete</button>
                                </div>
                            </div>
                            
                            <div class="list-item">
                                <div class="list-item-content">
                                    <div class="list-item-title">input_003</div>
                                    <div class="list-item-description">"Can you show me an example of how to get started?"</div>
                                </div>
                                <div class="list-item-actions">
                                    <button class="btn btn-secondary btn-small" onclick="showDialog('Edit Input')">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="showDialog('Delete Input')">Delete</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Variations Tab -->
                        <div class="tab-content" id="config-variations">
                            <div class="form-group">
                                <label class="form-label">Variation Strategies</label>
                                <div class="checkbox-group">
                                    <label><input type="checkbox" checked> Rephrase</label>
                                    <label><input type="checkbox" checked> Verbose</label>
                                    <label><input type="checkbox"> Concise</label>
                                    <label><input type="checkbox"> Error Prone</label>
                                    <label><input type="checkbox"> Formal</label>
                                    <label><input type="checkbox"> Casual</label>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Variation Count</label>
                                <input type="number" class="form-input" value="5" min="1" max="20">
                                <div class="help-text">Number of variations to generate per strategy</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Custom Strategies</label>
                                <textarea class="form-textarea" placeholder="Add custom variation strategies..."></textarea>
                                <div class="help-text">One strategy per line</div>
                            </div>
                        </div>
                        
                        <!-- Runner Tab -->
                        <div class="tab-content" id="config-runner">
                            <div class="form-group">
                                <label class="form-label">Agent Module</label>
                                <input type="text" class="form-input" value="src.pluto_agent">
                                <div class="help-text">Python module path to the agent</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Function Name</label>
                                <input type="text" class="form-input" value="run">
                                <div class="help-text">Function to call in the agent module</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Environment</label>
                                <select class="form-select">
                                    <option value="local">Local Python</option>
                                    <option value="docker">Docker Container</option>
                                    <option value="devcontainer">Dev Container</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Timeout (seconds)</label>
                                <input type="number" class="form-input" value="30" min="1" max="300">
                                <div class="help-text">Maximum time per execution</div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Collector URL</label>
                                <input type="text" class="form-input" value="http://localhost:8000">
                                <div class="help-text">URL for trace collection</div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                            <button class="btn btn-primary" onclick="showDialog('Save Configuration')">Save Configuration</button>
                            <button class="btn btn-secondary" onclick="showDialog('Reset to Defaults')">Reset to Defaults</button>
                            <button class="btn btn-secondary" onclick="showDialog('Export Configuration')">Export</button>
                        </div>
                    </div>
                </div>
                
                <!-- Results Viewer Webview -->
                <div class="webview-card">
                    <div class="webview-header">
                        <h2>📊 Results Viewer</h2>
                    </div>
                    <div class="webview-content">
                        <div class="tab-container">
                            <button class="tab active" onclick="switchTab('results-overview')">Overview</button>
                            <button class="tab" onclick="switchTab('results-traces')">Traces</button>
                            <button class="tab" onclick="switchTab('results-metrics')">Metrics</button>
                            <button class="tab" onclick="switchTab('results-comparison')">Comparison</button>
                        </div>
                        
                        <!-- Overview Tab -->
                        <div class="tab-content active" id="results-overview">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                                <div class="metric-card">
                                    <div class="metric-value">50</div>
                                    <div class="metric-label">Total Runs</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">87%</div>
                                    <div class="metric-label">Success Rate</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">2.3s</div>
                                    <div class="metric-label">Avg Duration</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-value">1.95m</div>
                                    <div class="metric-label">Total Time</div>
                                </div>
                            </div>
                            
                            <div class="chart-container">
                                [Chart: Success Rate Over Time]
                            </div>
                            
                            <div class="info-box">
                                <strong>Experiment Summary:</strong><br>
                                • Started: 2024-12-01 14:30:22<br>
                                • Completed: 2024-12-01 14:32:17<br>
                                • Duration: 1 minute 55 seconds<br>
                                • Output: experiments/pluto_experiment_20241201_143022
                            </div>
                        </div>
                        
                        <!-- Traces Tab -->
                        <div class="tab-content" id="results-traces">
                            <div class="form-group">
                                <label class="form-label">Filter Traces</label>
                                <select class="form-select">
                                    <option value="all">All Traces</option>
                                    <option value="successful">Successful Only</option>
                                    <option value="failed">Failed Only</option>
                                    <option value="persona">By Persona</option>
                                </select>
                            </div>
                            
                            <div class="timeline">
                                <div class="timeline-item success">
                                    <div class="timeline-title">Trace: trace_001</div>
                                    <div class="timeline-time">14:30:25 - 14:30:27 (2.1s)</div>
                                    <div class="timeline-content">
                                        <strong>Persona:</strong> novice_user<br>
                                        <strong>Input:</strong> "Help me understand how to use this system"<br>
                                        <strong>Output:</strong> "I'd be happy to help you get started..."
                                    </div>
                                </div>
                                
                                <div class="timeline-item success">
                                    <div class="timeline-title">Trace: trace_002</div>
                                    <div class="timeline-time">14:30:28 - 14:30:30 (1.8s)</div>
                                    <div class="timeline-content">
                                        <strong>Persona:</strong> expert_user<br>
                                        <strong>Input:</strong> "What are the main features available?"<br>
                                        <strong>Output:</strong> "The system provides the following features..."
                                    </div>
                                </div>
                                
                                <div class="timeline-item error">
                                    <div class="timeline-title">Trace: trace_003</div>
                                    <div class="timeline-time">14:30:31 - 14:30:33 (2.5s)</div>
                                    <div class="timeline-content">
                                        <strong>Persona:</strong> casual_user<br>
                                        <strong>Input:</strong> "Can you show me an example?"<br>
                                        <strong>Error:</strong> Timeout exceeded
                                    </div>
                                </div>
                                
                                <div class="timeline-item warning">
                                    <div class="timeline-title">Trace: trace_004</div>
                                    <div class="timeline-time">14:30:34 - 14:30:36 (2.0s)</div>
                                    <div class="timeline-content">
                                        <strong>Persona:</strong> power_user<br>
                                        <strong>Input:</strong> "Show me advanced configuration options"<br>
                                        <strong>Output:</strong> "Here are the advanced options..."<br>
                                        <strong>Warning:</strong> Response took longer than expected
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Metrics Tab -->
                        <div class="tab-content" id="results-metrics">
                            <div class="chart-container" style="height: 150px; margin-bottom: 20px;">
                                [Chart: Response Time Distribution]
                            </div>
                            
                            <div class="chart-container" style="height: 150px; margin-bottom: 20px;">
                                [Chart: Success Rate by Persona]
                            </div>
                            
                            <div class="chart-container" style="height: 150px;">
                                [Chart: Error Rate Trends]
                            </div>
                            
                            <div class="info-box">
                                <strong>Performance Metrics:</strong><br>
                                • Fastest Response: 1.2s<br>
                                • Slowest Response: 4.1s<br>
                                • 95th Percentile: 3.2s<br>
                                • Standard Deviation: 0.8s
                            </div>
                        </div>
                        
                        <!-- Comparison Tab -->
                        <div class="tab-content" id="results-comparison">
                            <div class="form-group">
                                <label class="form-label">Compare With</label>
                                <select class="form-select">
                                    <option value="">Select experiment to compare</option>
                                    <option value="experiment_20241130">pluto_experiment_20241130</option>
                                    <option value="experiment_20241129">pluto_experiment_20241129</option>
                                </select>
                            </div>
                            
                            <div class="chart-container" style="height: 200px; margin-bottom: 20px;">
                                [Chart: A/B Comparison - Success Rates]
                            </div>
                            
                            <div class="chart-container" style="height: 200px;">
                                [Chart: A/B Comparison - Response Times]
                            </div>
                            
                            <div class="info-box">
                                <strong>Comparison Summary:</strong><br>
                                • Current: 87% success rate, 2.3s avg<br>
                                • Previous: 82% success rate, 2.8s avg<br>
                                • Improvement: +5% success, -0.5s faster
                            </div>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                            <button class="btn btn-primary" onclick="showDialog('Export Results')">Export Results</button>
                            <button class="btn btn-secondary" onclick="showDialog('Generate Report')">Generate Report</button>
                            <button class="btn btn-secondary" onclick="showDialog('Share Results')">Share</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                function switchTab(tabId) {
                    // Hide all tab contents
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                    
                    // Remove active class from all tabs
                    document.querySelectorAll('.tab').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    
                    // Show selected tab content
                    document.getElementById(tabId).classList.add('active');
                    
                    // Add active class to clicked tab
                    event.target.classList.add('active');
                }
                
                function showDialog(action) {
                    const messages = {
                        'Add Persona': 'This would open a persona editor dialog',
                        'Edit Persona': 'This would open the persona editor with pre-filled data',
                        'Delete Persona': 'This would show a confirmation dialog',
                        'Add Base Input': 'This would open a base input editor dialog',
                        'Import Inputs': 'This would open a file picker for importing inputs',
                        'Edit Input': 'This would open the input editor with pre-filled data',
                        'Delete Input': 'This would show a confirmation dialog',
                        'Save Configuration': 'This would save the configuration to setting.yaml',
                        'Reset to Defaults': 'This would reset all fields to default values',
                        'Export Configuration': 'This would download the configuration as a file',
                        'Export Results': 'This would export results as CSV/JSON',
                        'Generate Report': 'This would generate a comprehensive report',
                        'Share Results': 'This would create a shareable link'
                    };
                    
                    alert('Wireframe Action: ' + action + '\\n\\n' + (messages[action] || 'This feature will be implemented in the actual extension.'));
                }
                
                // Initialize first tab as active
                document.addEventListener('DOMContentLoaded', function() {
                    // Tabs are already initialized in HTML
                });
            </script>
        </body>
        </html>
        `;
    }
}
