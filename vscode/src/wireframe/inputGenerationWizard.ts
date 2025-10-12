import * as vscode from 'vscode';

export class InputGenerationWizard {
    private _panel: vscode.WebviewPanel | undefined;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    createOrShow() {
        if (this._panel) {
            this._panel.reveal(vscode.ViewColumn.One);
        } else {
            this._panel = vscode.window.createWebviewPanel(
                'fluxloopInputWizard',
                'FluxLoop Input Generation Wizard',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [vscode.Uri.joinPath(this.context.extensionUri, 'media')]
                }
            );
            
            this._panel.webview.html = this.getWizardHtml();
            this._panel.onDidDispose(() => this._panel = undefined);
        }
    }
    
    private getWizardHtml(): string {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Input Generation Wizard</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                    color: #333;
                }
                
                .wizard-container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                
                .wizard-header {
                    background: linear-gradient(135deg, #2196f3, #1976d2);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                
                .wizard-header h1 {
                    margin: 0;
                    font-size: 28px;
                    font-weight: 300;
                }
                
                .wizard-header p {
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }
                
                .wizard-content {
                    padding: 40px;
                }
                
                .step-indicator {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 40px;
                }
                
                .step {
                    display: flex;
                    align-items: center;
                    margin: 0 10px;
                }
                
                .step-number {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: #e0e0e0;
                    color: #666;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    margin-right: 8px;
                    transition: all 0.3s ease;
                }
                
                .step.active .step-number {
                    background: #2196f3;
                    color: white;
                }
                
                .step.completed .step-number {
                    background: #4caf50;
                    color: white;
                }
                
                .step-label {
                    font-size: 14px;
                    color: #666;
                }
                
                .step.active .step-label {
                    color: #2196f3;
                    font-weight: 500;
                }
                
                .step-content {
                    display: none;
                }
                
                .step-content.active {
                    display: block;
                }
                
                .form-group {
                    margin-bottom: 24px;
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
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 12px;
                    margin-top: 12px;
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
                
                .wizard-actions {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 40px;
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
                
                .btn-primary:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }
                
                .preview-section {
                    background: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }
                
                .preview-title {
                    font-weight: 500;
                    margin-bottom: 12px;
                    color: #333;
                }
                
                .preview-content {
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    background: white;
                    padding: 12px;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                    max-height: 200px;
                    overflow-y: auto;
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
            </style>
        </head>
        <body>
            <div class="wizard-container">
                <div class="wizard-header">
                    <h1>🎯 Input Generation Wizard</h1>
                    <p>Generate diverse input variations for your AI agent experiments</p>
                </div>
                
                <div class="wizard-content">
                    <div class="step-indicator">
                        <div class="step active" data-step="1">
                            <div class="step-number">1</div>
                            <div class="step-label">Mode</div>
                        </div>
                        <div class="step" data-step="2">
                            <div class="step-number">2</div>
                            <div class="step-label">Personas</div>
                        </div>
                        <div class="step" data-step="3">
                            <div class="step-number">3</div>
                            <div class="step-label">Strategies</div>
                        </div>
                        <div class="step" data-step="4">
                            <div class="step-number">4</div>
                            <div class="step-label">Settings</div>
                        </div>
                        <div class="step" data-step="5">
                            <div class="step-number">5</div>
                            <div class="step-label">Preview</div>
                        </div>
                    </div>
                    
                    <!-- Step 1: Mode Selection -->
                    <div class="step-content active" data-step="1">
                        <h2>Select Generation Mode</h2>
                        <p>Choose how you want to generate input variations:</p>
                        
                        <div class="form-group">
                            <label class="form-label">Generation Mode</label>
                            <select class="form-select" id="generationMode">
                                <option value="deterministic">Deterministic</option>
                                <option value="llm">LLM-based</option>
                            </select>
                            <div class="help-text">Deterministic uses predefined rules, LLM uses AI to generate variations</div>
                        </div>
                        
                        <div id="llmSettings" style="display: none;">
                            <div class="form-group">
                                <label class="form-label">LLM Provider</label>
                                <select class="form-select" id="llmProvider">
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                    <option value="google">Google</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">Model</label>
                                <select class="form-select" id="llmModel">
                                    <option value="gpt-4">GPT-4</option>
                                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    <option value="claude-3">Claude 3</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">API Key</label>
                                <input type="password" class="form-input" id="apiKey" placeholder="Enter your API key">
                                <div class="help-text">Your API key will be stored securely</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Step 2: Persona Selection -->
                    <div class="step-content" data-step="2">
                        <h2>Select Personas</h2>
                        <p>Choose which user personas to use for input generation:</p>
                        
                        <div class="checkbox-group">
                            <div class="checkbox-item" data-persona="novice_user">
                                <input type="checkbox" id="persona_novice">
                                <div>
                                    <div class="checkbox-label">Novice User</div>
                                    <div class="checkbox-description">Beginner with basic knowledge</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-persona="expert_user">
                                <input type="checkbox" id="persona_expert">
                                <div>
                                    <div class="checkbox-label">Expert User</div>
                                    <div class="checkbox-description">Advanced user with deep expertise</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-persona="casual_user">
                                <input type="checkbox" id="persona_casual">
                                <div>
                                    <div class="checkbox-label">Casual User</div>
                                    <div class="checkbox-description">Occasional user, simple requests</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-persona="power_user">
                                <input type="checkbox" id="persona_power">
                                <div>
                                    <div class="checkbox-label">Power User</div>
                                    <div class="checkbox-description">Heavy user, complex requirements</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Step 3: Variation Strategies -->
                    <div class="step-content" data-step="3">
                        <h2>Select Variation Strategies</h2>
                        <p>Choose how to vary the input text:</p>
                        
                        <div class="checkbox-group">
                            <div class="checkbox-item" data-strategy="rephrase">
                                <input type="checkbox" id="strategy_rephrase">
                                <div>
                                    <div class="checkbox-label">Rephrase</div>
                                    <div class="checkbox-description">Express the same meaning differently</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-strategy="verbose">
                                <input type="checkbox" id="strategy_verbose">
                                <div>
                                    <div class="checkbox-label">Verbose</div>
                                    <div class="checkbox-description">Add more detail and explanation</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-strategy="concise">
                                <input type="checkbox" id="strategy_concise">
                                <div>
                                    <div class="checkbox-label">Concise</div>
                                    <div class="checkbox-description">Make the request shorter and direct</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-strategy="error_prone">
                                <input type="checkbox" id="strategy_error_prone">
                                <div>
                                    <div class="checkbox-label">Error Prone</div>
                                    <div class="checkbox-description">Include common mistakes and typos</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-strategy="formal">
                                <input type="checkbox" id="strategy_formal">
                                <div>
                                    <div class="checkbox-label">Formal</div>
                                    <div class="checkbox-description">Use formal language and tone</div>
                                </div>
                            </div>
                            
                            <div class="checkbox-item" data-strategy="casual">
                                <input type="checkbox" id="strategy_casual">
                                <div>
                                    <div class="checkbox-label">Casual</div>
                                    <div class="checkbox-description">Use informal, conversational tone</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Step 4: Settings -->
                    <div class="step-content" data-step="4">
                        <h2>Generation Settings</h2>
                        <p>Configure the generation parameters:</p>
                        
                        <div class="form-group">
                            <label class="form-label">Number of Variations</label>
                            <input type="number" class="form-input" id="variationCount" value="10" min="1" max="100">
                            <div class="help-text">How many variations to generate per base input</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Output File</label>
                            <input type="text" class="form-input" id="outputFile" value="inputs/generated.yaml">
                            <div class="help-text">Path where generated inputs will be saved</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">From Recording (Optional)</label>
                            <input type="text" class="form-input" id="fromRecording" placeholder="path/to/recording.jsonl">
                            <div class="help-text">Use a recorded session as template for generation</div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Overwrite Existing File</label>
                            <select class="form-select" id="overwrite">
                                <option value="false">No (append to existing)</option>
                                <option value="true">Yes (replace existing)</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Step 5: Preview -->
                    <div class="step-content" data-step="5">
                        <h2>Preview & Generate</h2>
                        <p>Review your settings and generate the inputs:</p>
                        
                        <div class="preview-section">
                            <div class="preview-title">CLI Command Preview</div>
                            <div class="preview-content" id="commandPreview">
                                fluxloop generate inputs --mode deterministic --personas novice_user,expert_user --strategy rephrase,verbose --limit 10 --output inputs/generated.yaml
                            </div>
                        </div>
                        
                        <div class="preview-section">
                            <div class="preview-title">Expected Output</div>
                            <div class="preview-content" id="outputPreview">
                                • 10 variations per base input
                                • 2 personas selected
                                • 2 strategies applied
                                • Estimated total: 20 generated inputs
                                • Output file: inputs/generated.yaml
                            </div>
                        </div>
                    </div>
                    
                    <div class="wizard-actions">
                        <button class="btn btn-secondary" id="prevBtn" onclick="previousStep()" disabled>Previous</button>
                        <button class="btn btn-primary" id="nextBtn" onclick="nextStep()">Next</button>
                        <button class="btn btn-primary" id="generateBtn" onclick="generateInputs()" style="display: none;">Generate Inputs</button>
                    </div>
                </div>
            </div>
            
            <script>
                let currentStep = 1;
                const totalSteps = 5;
                
                function updateStepIndicator() {
                    document.querySelectorAll('.step').forEach((step, index) => {
                        step.classList.remove('active', 'completed');
                        if (index + 1 < currentStep) {
                            step.classList.add('completed');
                        } else if (index + 1 === currentStep) {
                            step.classList.add('active');
                        }
                    });
                    
                    document.querySelectorAll('.step-content').forEach((content, index) => {
                        content.classList.remove('active');
                        if (index + 1 === currentStep) {
                            content.classList.add('active');
                        }
                    });
                    
                    // Update buttons
                    const prevBtn = document.getElementById('prevBtn');
                    const nextBtn = document.getElementById('nextBtn');
                    const generateBtn = document.getElementById('generateBtn');
                    
                    prevBtn.disabled = currentStep === 1;
                    
                    if (currentStep === totalSteps) {
                        nextBtn.style.display = 'none';
                        generateBtn.style.display = 'inline-block';
                    } else {
                        nextBtn.style.display = 'inline-block';
                        generateBtn.style.display = 'none';
                    }
                }
                
                function nextStep() {
                    if (currentStep < totalSteps) {
                        currentStep++;
                        updateStepIndicator();
                        updatePreview();
                    }
                }
                
                function previousStep() {
                    if (currentStep > 1) {
                        currentStep--;
                        updateStepIndicator();
                    }
                }
                
                function updatePreview() {
                    if (currentStep === 5) {
                        const mode = document.getElementById('generationMode').value;
                        const personas = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                            .map(cb => cb.id.replace('persona_', '').replace('_', '-'));
                        const strategies = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                            .map(cb => cb.id.replace('strategy_', '').replace('_', '-'));
                        const count = document.getElementById('variationCount').value;
                        const output = document.getElementById('outputFile').value;
                        
                        const command = \`fluxloop generate inputs --mode \${mode} --personas \${personas.join(',')} --strategy \${strategies.join(',')} --limit \${count} --output \${output}\`;
                        document.getElementById('commandPreview').textContent = command;
                        
                        const totalInputs = personas.length * strategies.length * count;
                        document.getElementById('outputPreview').innerHTML = \`
                            • \${count} variations per base input
                            • \${personas.length} personas selected
                            • \${strategies.length} strategies applied
                            • Estimated total: \${totalInputs} generated inputs
                            • Output file: \${output}
                        \`;
                    }
                }
                
                function generateInputs() {
                    alert('Wireframe Action: Generate Inputs\\n\\nThis would execute the CLI command and show progress in the Output Channel.\\n\\nIn the actual implementation, this would:\\n1. Execute the fluxloop generate inputs command\\n2. Show progress in Output Channel\\n3. Update the Inputs panel with new files\\n4. Open the generated file for review');
                }
                
                // Event listeners
                document.getElementById('generationMode').addEventListener('change', function() {
                    const llmSettings = document.getElementById('llmSettings');
                    if (this.value === 'llm') {
                        llmSettings.style.display = 'block';
                    } else {
                        llmSettings.style.display = 'none';
                    }
                });
                
                // Checkbox item click handlers
                document.querySelectorAll('.checkbox-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const checkbox = this.querySelector('input[type="checkbox"]');
                        checkbox.checked = !checkbox.checked;
                        this.classList.toggle('selected', checkbox.checked);
                    });
                });
                
                // Initialize
                updateStepIndicator();
            </script>
        </body>
        </html>
        `;
    }
}
