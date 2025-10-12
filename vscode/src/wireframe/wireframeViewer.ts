import * as vscode from 'vscode';

export class WireframeViewer {
    private _panel: vscode.WebviewPanel | undefined;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    createOrShow() {
        if (this._panel) {
            this._panel.reveal(vscode.ViewColumn.One);
        } else {
            this._panel = vscode.window.createWebviewPanel(
                'fluxloopWireframe',
                'FluxLoop Wireframe',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')]
                }
            );
            
            this._panel.webview.html = this.getWireframeHtml();
            this._panel.onDidDispose(() => this._panel = undefined);
        }
    }
    
    private getWireframeHtml(): string {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FluxLoop Wireframe</title>
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
                
                .wireframe-container {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .panel {
                    background: white;
                    border: 2px dashed #ccc;
                    margin: 10px 0;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                }
                
                .panel:hover {
                    border-color: #2196f3;
                    box-shadow: 0 4px 8px rgba(33, 150, 243, 0.1);
                }
                
                .panel-title {
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 16px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .panel-title::before {
                    content: attr(data-icon);
                    font-size: 18px;
                }
                
                .tree-item {
                    padding: 8px 0;
                    border-left: 2px solid #e0e0e0;
                    padding-left: 20px;
                    margin: 3px 0;
                    font-size: 14px;
                    color: #555;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .tree-item:hover {
                    background: #f0f8ff;
                    border-left-color: #2196f3;
                    padding-left: 25px;
                }
                
                .tree-item.expandable::before {
                    content: '▶';
                    margin-right: 8px;
                    font-size: 12px;
                    color: #999;
                }
                
                .tree-item.expanded::before {
                    content: '▼';
                }
                
                .button-placeholder {
                    background: #2196f3;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    margin: 10px 0;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    display: inline-block;
                }
                
                .button-placeholder:hover {
                    background: #1976d2;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
                }
                
                .status-item {
                    padding: 8px 0;
                    font-size: 14px;
                    color: #555;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .status-item::before {
                    content: '●';
                    color: #4caf50;
                    font-size: 12px;
                }
                
                .status-item.error::before {
                    color: #f44336;
                }
                
                .status-item.warning::before {
                    color: #ff9800;
                }
                
                .section-divider {
                    height: 1px;
                    background: #e0e0e0;
                    margin: 20px 0;
                    border: none;
                }
                
                .note {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                    font-size: 14px;
                    color: #856404;
                }
                
                .note::before {
                    content: '💡 ';
                    font-size: 16px;
                }
                
                @media (max-width: 768px) {
                    .wireframe-container {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FluxLoop VSCode Extension Wireframe</h1>
                <p>Interactive prototype showing the planned UI structure and user flows</p>
            </div>
            
            <div class="wireframe-container">
                <!-- Experiments Panel -->
                <div class="panel">
                    <div class="panel-title" data-icon="🧪">Experiments</div>
                    <div class="tree-item expandable">Current Experiment (setting.yaml)</div>
                    <div class="tree-item">├── Configuration</div>
                    <div class="tree-item">├── Personas (2)</div>
                    <div class="tree-item">├── Base Inputs (3)</div>
                    <div class="tree-item">├── Variation Strategies</div>
                    <div class="tree-item">└── Run Experiment</div>
                    <div class="section-divider"></div>
                    <div class="tree-item expandable">Results (완료된 실험들)</div>
                    <div class="tree-item">├── experiment_20241201_143022</div>
                    <div class="tree-item">│   ├── summary.json</div>
                    <div class="tree-item">│   ├── traces.jsonl</div>
                    <div class="tree-item">│   └── Parse Results</div>
                    <div class="tree-item">└── experiment_20241202_091530</div>
                    <div class="tree-item">    ├── summary.json</div>
                    <div class="tree-item">    └── traces.jsonl</div>
                </div>
                
                <!-- Inputs Panel -->
                <div class="panel">
                    <div class="panel-title" data-icon="📝">Inputs</div>
                    <div class="tree-item expandable">Base Inputs</div>
                    <div class="tree-item">├── input_001.yaml</div>
                    <div class="tree-item">├── input_002.yaml</div>
                    <div class="tree-item">└── input_003.yaml</div>
                    <div class="section-divider"></div>
                    <div class="tree-item expandable">Generated Inputs</div>
                    <div class="tree-item">├── generated_20241201.yaml</div>
                    <div class="tree-item">└── generated_20241202.yaml</div>
                    <div class="section-divider"></div>
                    <div class="tree-item expandable">Recordings</div>
                    <div class="tree-item">├── recording_001.jsonl</div>
                    <div class="tree-item">└── recording_002.jsonl</div>
                    <div class="section-divider"></div>
                    <button class="button-placeholder" onclick="showDialog('Generate New Inputs')">Generate New Inputs</button>
                </div>
                
                <!-- Personas Panel -->
                <div class="panel">
                    <div class="panel-title" data-icon="👥">Personas</div>
                    <div class="tree-item">novice_user</div>
                    <div class="tree-item">├── Description: Beginner user with basic knowledge</div>
                    <div class="tree-item">├── Characteristics: Cautious, asks many questions</div>
                    <div class="tree-item">└── Goals: Learn and understand the system</div>
                    <div class="section-divider"></div>
                    <div class="tree-item">expert_user</div>
                    <div class="tree-item">├── Description: Advanced user with deep expertise</div>
                    <div class="tree-item">├── Characteristics: Efficient, direct communication</div>
                    <div class="tree-item">└── Goals: Optimize performance and results</div>
                    <div class="section-divider"></div>
                    <button class="button-placeholder" onclick="showDialog('Add Persona')">Add Persona</button>
                </div>
                
                <!-- Results Panel -->
                <div class="panel">
                    <div class="panel-title" data-icon="📊">Results</div>
                    <div class="tree-item expandable">Live Results</div>
                    <div class="tree-item">├── Current Run: 45% complete</div>
                    <div class="tree-item">├── Success Rate: 87%</div>
                    <div class="tree-item">└── Avg Duration: 2.3s</div>
                    <div class="section-divider"></div>
                    <div class="tree-item expandable">Trace Analysis</div>
                    <div class="tree-item">├── Trace Timeline</div>
                    <div class="tree-item">├── Performance Metrics</div>
                    <div class="tree-item">└── Error Analysis</div>
                    <div class="section-divider"></div>
                    <div class="tree-item expandable">Performance Metrics</div>
                    <div class="tree-item">├── Success Rate Chart</div>
                    <div class="tree-item">├── Response Time Distribution</div>
                    <div class="tree-item">└── Error Rate Trends</div>
                </div>
                
                <!-- Status Panel -->
                <div class="panel">
                    <div class="panel-title" data-icon="ℹ️">Status</div>
                    <div class="status-item">CLI: Installed (v1.2.3)</div>
                    <div class="status-item">SDK: Check in terminal</div>
                    <div class="status-item">Collector: http://localhost:8000</div>
                    <div class="status-item">Config: setting.yaml found</div>
                    <div class="section-divider"></div>
                    <div class="status-item">Python: 3.11.0</div>
                    <div class="status-item">Environment: Local</div>
                    <div class="status-item">Workspace: /Users/user/fluxloop-project</div>
                    <div class="section-divider"></div>
                    <div class="status-item warning">Docker: Not available</div>
                    <div class="status-item">Dev Container: Not detected</div>
                </div>
                
                <!-- Evaluate Panel (Future) -->
                <div class="panel">
                    <div class="panel-title" data-icon="📈">Evaluate (Coming Soon)</div>
                    <div class="note">
                        This panel will contain advanced evaluation features including:
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Performance comparison charts</li>
                            <li>A/B testing results</li>
                            <li>Statistical analysis</li>
                            <li>Export capabilities</li>
                        </ul>
                    </div>
                    <button class="button-placeholder" onclick="showDialog('Request Features')">Request Features</button>
                </div>
            </div>
            
            <div class="note">
                <strong>Wireframe Notes:</strong> This is an interactive prototype. Click on elements to see planned functionality. 
                The actual implementation will follow VSCode's native UI patterns and accessibility guidelines.
            </div>
            
            <script>
                function showDialog(action) {
                    const messages = {
                        'Generate New Inputs': 'This will open the Input Generation Wizard with options for:\n• Mode selection (Deterministic/LLM)\n• Persona selection\n• Variation strategies\n• Output settings',
                        'Add Persona': 'This will open the Persona Editor with fields for:\n• Name and description\n• Characteristics\n• Expertise level\n• Goals and preferences',
                        'Request Features': 'This will open a feedback form to request:\n• New evaluation metrics\n• Additional analysis tools\n• Integration features\n• UI/UX improvements'
                    };
                    
                    alert('Wireframe Action: ' + action + '\\n\\n' + (messages[action] || 'This feature will be implemented in the actual extension.'));
                }
                
                // Add click handlers for tree items
                document.querySelectorAll('.tree-item').forEach(item => {
                    item.addEventListener('click', function() {
                        if (this.classList.contains('expandable')) {
                            this.classList.toggle('expanded');
                        }
                    });
                });
            </script>
        </body>
        </html>
        `;
    }
}
