import * as vscode from 'vscode';

export class DialogsWireframe {
    private _panel: vscode.WebviewPanel | undefined;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    createOrShow() {
        if (this._panel) {
            this._panel.reveal(vscode.ViewColumn.One);
        } else {
            this._panel = vscode.window.createWebviewPanel(
                'fluxloopDialogsWireframe',
                'FluxLoop Dialogs Wireframe',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')]
                }
            );
            
            this._panel.webview.html = this.getDialogsHtml();
            this._panel.onDidDispose(() => this._panel = undefined);
        }
    }
    
    private getDialogsHtml(): string {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FluxLoop Dialogs Wireframe</title>
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
                
                .dialogs-container {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .dialog-card {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    overflow: hidden;
                    transition: transform 0.3s ease;
                }
                
                .dialog-card:hover {
                    transform: translateY(-2px);
                }
                
                .dialog-header {
                    background: linear-gradient(135deg, #2196f3, #1976d2);
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                
                .dialog-header h2 {
                    margin: 0;
                    font-size: 18px;
                    font-weight: 300;
                }
                
                .dialog-content {
                    padding: 30px;
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
                
                .checkbox-group {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                
                .checkbox-item {
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .checkbox-item:hover {
                    border-color: #2196f3;
                    background: #f0f8ff;
                }
                
                .checkbox-item.selected {
                    border-color: #2196f3;
                    background: #e3f2fd;
                }
                
                .checkbox-item input[type="checkbox"] {
                    margin-right: 8px;
                }
                
                .checkbox-label {
                    font-size: 14px;
                    color: #333;
                }
                
                .checkbox-description {
                    font-size: 12px;
                    color: #666;
                    margin-top: 4px;
                }
                
                .dialog-actions {
                    display: flex;
                    justify-content: flex-end;
                    gap: 12px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }
                
                .btn {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .btn-secondary {
                    background: #f5f5f5;
                    color: #666;
                }
                
                .btn-secondary:hover {
                    background: #e0e0e0;
                }
                
                .btn-primary {
                    background: #2196f3;
                    color: white;
                }
                
                .btn-primary:hover {
                    background: #1976d2;
                }
                
                .btn-danger {
                    background: #f44336;
                    color: white;
                }
                
                .btn-danger:hover {
                    background: #d32f2f;
                }
                
                .help-text {
                    font-size: 12px;
                    color: #666;
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
                
                .success-box {
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    font-size: 14px;
                    color: #155724;
                }
                
                .success-box::before {
                    content: '✅ ';
                    font-size: 16px;
                }
                
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background: #e0e0e0;
                    border-radius: 4px;
                    overflow: hidden;
                    margin: 20px 0;
                }
                
                .progress-fill {
                    height: 100%;
                    background: #2196f3;
                    transition: width 0.3s ease;
                }
                
                .status-item {
                    display: flex;
                    align-items: center;
                    padding: 8px 0;
                    font-size: 14px;
                    color: #555;
                }
                
                .status-item::before {
                    content: '●';
                    margin-right: 8px;
                    font-size: 12px;
                }
                
                .status-item.success::before {
                    color: #4caf50;
                }
                
                .status-item.error::before {
                    color: #f44336;
                }
                
                .status-item.warning::before {
                    color: #ff9800;
                }
                
                .status-item.info::before {
                    color: #2196f3;
                }
                
                @media (max-width: 768px) {
                    .dialogs-container {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FluxLoop Dialogs Wireframe</h1>
                <p>Interactive prototypes of key dialogs and workflows</p>
            </div>
            
            <div class="dialogs-container">
                <!-- Init Project Dialog -->
                <div class="dialog-card">
                    <div class="dialog-header">
                        <h2>🚀 Initialize Project</h2>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label class="form-label">Project Folder</label>
                            <input type="text" class="form-input" value="/Users/user/fluxloop-project" readonly>
                            <div class="help-text">Selected folder for the new project</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Project Name</label>
                            <input type="text" class="form-input" value="my-fluxloop-project" placeholder="Enter project name">
                            <div class="help-text">Name for your FluxLoop project</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Include Example Agent</label>
                            <select class="form-select">
                                <option value="true">Yes - Include example agent</option>
                                <option value="false">No - Start with empty project</option>
                            </select>
                            <div class="help-text">Add a sample agent to get started quickly</div>
                        </div>
                        
                        <div class="info-box">
                            This will create a new FluxLoop project with:
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>configs/project.yaml configuration file</li>
                                <li>src/ directory for your agents</li>
                                <li>inputs/ directory for test data</li>
                                <li>experiments/ directory for results</li>
                            </ul>
                        </div>
                        
                        <div class="dialog-actions">
                            <button class="btn btn-secondary" onclick="showDialog('Cancel')">Cancel</button>
                            <button class="btn btn-primary" onclick="showDialog('Initialize Project')">Initialize Project</button>
                        </div>
                    </div>
                </div>
                
                <!-- Run Experiment Options Dialog -->
                <div class="dialog-card">
                    <div class="dialog-header">
                        <h2>⚡ Run Experiment Options</h2>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label class="form-label">Iterations</label>
                            <input type="number" class="form-input" value="10" min="1" max="1000">
                            <div class="help-text">Number of times to run each input variation</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Personas</label>
                            <div class="checkbox-group">
                                <div class="checkbox-item selected">
                                    <input type="checkbox" checked>
                                    <div>
                                        <div class="checkbox-label">All Personas</div>
                                        <div class="checkbox-description">Use all configured personas</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">novice_user</div>
                                        <div class="checkbox-description">Beginner user</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">expert_user</div>
                                        <div class="checkbox-description">Advanced user</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Execution Options</label>
                            <div class="checkbox-group">
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">Dry Run</div>
                                        <div class="checkbox-description">Show what would be run without executing</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">No Collector</div>
                                        <div class="checkbox-description">Run without sending data to collector</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Output Directory</label>
                            <input type="text" class="form-input" value="experiments/" placeholder="Leave empty for default">
                            <div class="help-text">Directory to save experiment results</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Execution Environment</label>
                            <select class="form-select">
                                <option value="local">Local Python</option>
                                <option value="docker">Docker Container</option>
                                <option value="devcontainer">Dev Container</option>
                            </select>
                            <div class="help-text">Environment to run the experiment</div>
                        </div>
                        
                        <div class="warning-box">
                            This will execute <strong>50 runs</strong> (10 iterations × 5 personas). 
                            This may take a while and incur API costs.
                        </div>
                        
                        <div class="dialog-actions">
                            <button class="btn btn-secondary" onclick="showDialog('Cancel')">Cancel</button>
                            <button class="btn btn-primary" onclick="showDialog('Run Experiment')">Run Experiment</button>
                        </div>
                    </div>
                </div>
                
                <!-- Parse Results Dialog -->
                <div class="dialog-card">
                    <div class="dialog-header">
                        <h2>📊 Parse Results</h2>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label class="form-label">Experiment Directory</label>
                            <input type="text" class="form-input" value="experiments/pluto_experiment_20241201_143022" readonly>
                            <div class="help-text">Directory containing experiment results</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Output Directory</label>
                            <input type="text" class="form-input" value="per_trace_analysis" placeholder="per_trace_analysis">
                            <div class="help-text">Directory name for parsed results (relative to experiment dir)</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Output Format</label>
                            <select class="form-select">
                                <option value="md">Markdown (.md)</option>
                                <option value="html">HTML (.html)</option>
                                <option value="json">JSON (.json)</option>
                            </select>
                            <div class="help-text">Format for the parsed results</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Overwrite Existing</label>
                            <select class="form-select">
                                <option value="false">No - Skip existing files</option>
                                <option value="true">Yes - Replace existing files</option>
                            </select>
                            <div class="help-text">What to do if output directory already exists</div>
                        </div>
                        
                        <div class="info-box">
                            This will parse the experiment results into human-readable files:
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>One file per trace with detailed analysis</li>
                                <li>Timeline visualization of agent execution</li>
                                <li>Input/output comparison</li>
                                <li>Performance metrics</li>
                            </ul>
                        </div>
                        
                        <div class="dialog-actions">
                            <button class="btn btn-secondary" onclick="showDialog('Cancel')">Cancel</button>
                            <button class="btn btn-primary" onclick="showDialog('Parse Results')">Parse Results</button>
                        </div>
                    </div>
                </div>
                
                <!-- Progress Dialog -->
                <div class="dialog-card">
                    <div class="dialog-header">
                        <h2>⏳ Running Experiment</h2>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label class="form-label">Experiment: pluto_experiment_20241201</label>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 45%;"></div>
                            </div>
                            <div class="help-text">45% complete (23 of 50 runs)</div>
                        </div>
                        
                        <div class="status-item success">Experiment started successfully</div>
                        <div class="status-item success">Configuration loaded</div>
                        <div class="status-item success">Inputs generated (50 variations)</div>
                        <div class="status-item info">Running iteration 23/50</div>
                        <div class="status-item warning">3 runs failed (13% failure rate)</div>
                        
                        <div class="info-box">
                            <strong>Current Status:</strong> Running persona "expert_user" with input variation #23
                            <br><strong>Estimated Time Remaining:</strong> 2 minutes 30 seconds
                            <br><strong>Success Rate:</strong> 87% (20/23 successful)
                        </div>
                        
                        <div class="dialog-actions">
                            <button class="btn btn-danger" onclick="showDialog('Cancel Experiment')">Cancel</button>
                            <button class="btn btn-secondary" onclick="showDialog('View Logs')">View Logs</button>
                        </div>
                    </div>
                </div>
                
                <!-- Error Dialog -->
                <div class="dialog-card">
                    <div class="dialog-header">
                        <h2>❌ Error Occurred</h2>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label class="form-label">Error Type</label>
                            <input type="text" class="form-input" value="Configuration Error" readonly>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Error Message</label>
                            <textarea class="form-input" rows="4" readonly>Failed to load experiment configuration from configs/input.yaml:
- Missing required field: 'name'
- Invalid persona configuration: 'expert_user' has no description
- Base inputs file not found: inputs/base_inputs.yaml</textarea>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Suggested Actions</label>
                            <div class="checkbox-group">
                                <div class="checkbox-item selected">
                                    <input type="checkbox" checked>
                                    <div>
                                        <div class="checkbox-label">Open Configuration File</div>
                                        <div class="checkbox-description">Edit configs/input.yaml to fix the issues</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">Show CLI Command</div>
                                        <div class="checkbox-description">Display the command that failed</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">View Documentation</div>
                                        <div class="checkbox-description">Open help documentation</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="warning-box">
                            <strong>Troubleshooting:</strong> Check the Output Channel for detailed error logs and CLI output.
                        </div>
                        
                        <div class="dialog-actions">
                            <button class="btn btn-secondary" onclick="showDialog('Close')">Close</button>
                            <button class="btn btn-primary" onclick="showDialog('Fix Configuration')">Fix Configuration</button>
                        </div>
                    </div>
                </div>
                
                <!-- Success Dialog -->
                <div class="dialog-card">
                    <div class="dialog-header">
                        <h2>✅ Experiment Complete</h2>
                    </div>
                    <div class="dialog-content">
                        <div class="success-box">
                            <strong>Experiment completed successfully!</strong>
                            <br>All 50 runs finished without errors.
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Results Summary</label>
                            <div class="status-item success">Total Runs: 50</div>
                            <div class="status-item success">Successful: 50 (100%)</div>
                            <div class="status-item success">Failed: 0 (0%)</div>
                            <div class="status-item success">Average Duration: 2.3 seconds</div>
                            <div class="status-item success">Total Time: 1 minute 55 seconds</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Output Location</label>
                            <input type="text" class="form-input" value="experiments/pluto_experiment_20241201_143022" readonly>
                            <div class="help-text">Results saved to this directory</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Next Steps</label>
                            <div class="checkbox-group">
                                <div class="checkbox-item selected">
                                    <input type="checkbox" checked>
                                    <div>
                                        <div class="checkbox-label">Parse Results</div>
                                        <div class="checkbox-description">Convert to human-readable format</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">View Traces</div>
                                        <div class="checkbox-description">Open trace analysis</div>
                                    </div>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox">
                                    <div>
                                        <div class="checkbox-label">Export Results</div>
                                        <div class="checkbox-description">Download results as CSV/JSON</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dialog-actions">
                            <button class="btn btn-secondary" onclick="showDialog('Close')">Close</button>
                            <button class="btn btn-primary" onclick="showDialog('Parse Results')">Parse Results</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                function showDialog(action) {
                    const messages = {
                        'Initialize Project': 'This would execute: fluxloop init project /Users/user/fluxloop-project --name my-fluxloop-project',
                        'Run Experiment': 'This would execute: fluxloop run experiment --iterations 10 --personas all --output experiments/',
                        'Parse Results': 'This would execute: fluxloop parse experiment experiments/pluto_experiment_20241201_143022 --output per_trace_analysis',
                        'Cancel Experiment': 'This would send SIGTERM to the running process',
                        'View Logs': 'This would open the Output Channel with experiment logs',
                        'Fix Configuration': 'This would open configs/input.yaml in the editor',
                        'Close': 'This would close the dialog'
                    };
                    
                    alert('Wireframe Action: ' + action + '\\n\\n' + (messages[action] || 'This feature will be implemented in the actual extension.'));
                }
                
                // Checkbox item click handlers
                document.querySelectorAll('.checkbox-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const checkbox = this.querySelector('input[type="checkbox"]');
                        checkbox.checked = !checkbox.checked;
                        this.classList.toggle('selected', checkbox.checked);
                    });
                });
                
                // Simulate progress bar animation
                function animateProgress() {
                    const progressFill = document.querySelector('.progress-fill');
                    if (progressFill) {
                        let width = 0;
                        const interval = setInterval(() => {
                            width += 1;
                            progressFill.style.width = width + '%';
                            if (width >= 100) {
                                clearInterval(interval);
                            }
                        }, 100);
                    }
                }
                
                // Start animation after page load
                setTimeout(animateProgress, 1000);
            </script>
        </body>
        </html>
        `;
    }
}
