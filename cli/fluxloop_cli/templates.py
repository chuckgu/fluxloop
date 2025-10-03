"""
Templates for generating configuration and code files.
"""


def create_experiment_config(project_name: str) -> str:
    """Create a default experiment configuration."""
    return f"""# FluxLoop Experiment Configuration
name: {project_name}_experiment
description: AI agent simulation experiment
version: 1.0.0

# Simulation settings
iterations: 10
parallel_runs: 1
seed: 42
run_delay_seconds: 0

# User personas for simulation
personas:
  - name: novice_user
    description: A user new to the system
    characteristics:
      - Asks basic questions
      - May use incorrect terminology
      - Needs detailed explanations
    language: en
    expertise_level: novice
    goals:
      - Understand how the system works
      - Complete simple tasks

  - name: expert_user
    description: An experienced power user
    characteristics:
      - Uses technical terminology
      - Asks complex questions
      - Expects efficient responses
    language: en
    expertise_level: expert
    goals:
      - Optimize workflows
      - Access advanced features

# Base inputs for reference (generate inputs from these)
base_inputs:
  - input: "How do I get started?"
    expected_intent: help
  - input: "What can you do?"
    expected_intent: capabilities
  - input: "Show me an example"
    expected_intent: demo

# Agent runner configuration
runner:
  target: "examples.simple_agent:run"  # module:function or module:Class.method
  working_directory: .  # IMPORTANT: Set this to your project's root directory
  timeout_seconds: 30
  max_retries: 3

# Recorded argument replay (optional)
replay_args:
  enabled: false
  recording_file: recordings/args_recording.jsonl
  callable_providers:
    send_message_callback: "builtin:collector.send"
    send_error_callback: "builtin:collector.error"
  override_param_path: data.content

# Input generation configuration
input_generation:
  mode: llm
  llm:
    enabled: true
    provider: openai
    model: gpt-5
  strategies:
    - type: rephrase
    - type: verbose
    - type: error_prone
  variation_count: 2

# Evaluation methods
evaluators:
  - name: success_checker
    type: rule_based
    enabled: true
    rules:
      - check: output_not_empty
        weight: 1.0

  - name: response_quality
    type: llm_judge
    enabled: false
    model: gpt-5
    prompt_template: |
      Rate the quality of this response on a scale of 1-10:
      Input: {{input}}
      Output: {{output}}
      
      Consider: relevance, completeness, clarity
      Score:

# Output configuration
output_directory: experiments
save_traces: true
save_aggregated_metrics: true

# Inputs must be generated before running experiments
inputs_file: inputs/generated.yaml

# Collector settings (optional)
# collector_url: http://localhost:8000
# collector_api_key: your-api-key

# Tags and metadata
tags:
  - simulation
  - testing
metadata:
  team: development
  environment: local
"""


def create_sample_agent() -> str:
    """Create a sample agent implementation."""
    return '''"""
Sample agent implementation for FluxLoop testing.
"""

import random
import time
from typing import Any, Dict

import fluxloop 


@fluxloop.agent(name="SimpleAgent")
def run(input_text: str) -> str:
    """
    Main agent entry point.
    
    Args:
        input_text: Input from the user
        
    Returns:
        Agent response
    """
    # Process the input
    processed = process_input(input_text)
    
    # Generate response
    response = generate_response(processed)
    
    # Simulate some work
    time.sleep(random.uniform(0.1, 0.5))
    
    return response


@fluxloop.prompt(model="simple-model")
def generate_response(processed_input: Dict[str, Any]) -> str:
    """
    Generate a response based on processed input.
    """
    intent = processed_input.get("intent", "unknown")
    
    responses = {
        "greeting": "Hello! How can I help you today?",
        "help": "I can assist you with various tasks. What would you like to know?",
        "capabilities": "I can answer questions, provide information, and help with tasks.",
        "demo": "Here's an example: You can ask me about any topic and I'll try to help.",
        "unknown": "I'm not sure I understand. Could you please rephrase?",
    }
    
    return responses.get(intent, responses["unknown"])


@fluxloop.tool(description="Process and analyze input text")
def process_input(text: str) -> Dict[str, Any]:
    """
    Process the input text to extract intent and entities.
    """
    # Simple intent detection
    text_lower = text.lower()
    
    intent = "unknown"
    if any(word in text_lower for word in ["hello", "hi", "hey"]):
        intent = "greeting"
    elif any(word in text_lower for word in ["help", "start", "begin"]):
        intent = "help"
    elif any(word in text_lower for word in ["can you", "what can", "capabilities"]):
        intent = "capabilities"
    elif "example" in text_lower or "demo" in text_lower:
        intent = "demo"
    
    return {
        "original": text,
        "intent": intent,
        "word_count": len(text.split()),
        "has_question": "?" in text,
    }


if __name__ == "__main__":
    # Test the agent locally
    with fluxloop.instrument("test_run"):
        result = run("Hello, what can you help me with?")
        print(f"Result: {result}")
'''


def create_gitignore() -> str:
    """Create a .gitignore file."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv/

# FluxLoop
traces/
*.trace
*.log

# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
*.coverage
"""


def create_env_file() -> str:
    """Create a .env template file."""
    return """# FluxLoop Configuration
FLUXLOOP_COLLECTOR_URL=http://localhost:8000
FLUXLOOP_API_KEY=your-api-key-here
FLUXLOOP_ENABLED=true
FLUXLOOP_DEBUG=false
FLUXLOOP_SAMPLE_RATE=1.0
# Argument Recording (global toggle)
FLUXLOOP_RECORD_ARGS=false
FLUXLOOP_RECORDING_FILE=recordings/args_recording.jsonl

# Service Configuration
FLUXLOOP_SERVICE_NAME=my-agent
FLUXLOOP_ENVIRONMENT=development

# LLM API Keys (if needed)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Other Configuration
# Add your custom environment variables here
"""
