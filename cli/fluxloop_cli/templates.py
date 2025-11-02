"""
Templates for generating configuration and code files.
"""

from textwrap import dedent


def create_project_config(project_name: str) -> str:
    """Create default project-level configuration content."""

    return dedent(
        f"""
        # FluxLoop Project Configuration
        name: {project_name}
        description: AI agent simulation project
        version: 1.0.0

        collector_url: null
        collector_api_key: null

        tags:
          - simulation
          - testing

        metadata:
          team: development
          environment: local
        """
    ).strip() + "\n"


def create_input_config() -> str:
    """Create default input configuration content."""

    return dedent(
        """
        # FluxLoop Input Configuration
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
              - Understand system capabilities
              - Complete basic tasks

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

        base_inputs:
          - input: "How do I get started?"
            expected_intent: help
          - input: "What can you do?"
            expected_intent: capabilities
          - input: "Show me an example"
            expected_intent: demo

        variation_strategies:
          - rephrase
          - verbose
          - error_prone

        variation_count: 2
        variation_temperature: 0.7

        inputs_file: inputs/generated.yaml

        input_generation:
          mode: llm
          llm:
            enabled: true
            provider: openai
            model: gpt-4o-mini
            api_key: null
        """
    ).strip() + "\n"


def create_simulation_config(project_name: str) -> str:
    """Create default simulation configuration content."""

    return dedent(
        f"""
        # FluxLoop Simulation Configuration
        name: {project_name}_experiment
        description: AI agent simulation experiment

        iterations: 10
        parallel_runs: 1
        run_delay_seconds: 0
        seed: 42

        runner:
          module_path: "examples.simple_agent"
          function_name: "run"
          target: "examples.simple_agent:run"
          working_directory: .
          python_path:
          timeout_seconds: 120
          max_retries: 3

        replay_args:
          enabled: false
          recording_file: recordings/args_recording.jsonl
          override_param_path: data.content

        output_directory: experiments
        save_traces: true
        save_aggregated_metrics: true
        """
    ).strip() + "\n"


def create_evaluation_config() -> str:
    """Create default evaluation configuration content."""

    return dedent(
        """
        # FluxLoop Evaluation Configuration
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
            model: gpt-4o-mini
            prompt_template: |
              Rate the quality of this response on a scale of 1-10:
              Input: {input}
              Output: {output}

              Consider: relevance, completeness, clarity
              Score:
        """
    ).strip() + "\n"


def create_sample_agent() -> str:
    """Create a sample agent implementation."""

    return dedent(
        '''
        """Sample agent implementation for FluxLoop testing."""

        import random
        import time
        from typing import Any, Dict

        import fluxloop


        @fluxloop.agent(name="SimpleAgent")
        def run(input_text: str) -> str:
            """Main agent entry point."""
            processed = process_input(input_text)
            response = generate_response(processed)
            time.sleep(random.uniform(0.1, 0.5))
            return response


        @fluxloop.prompt(model="simple-model")
        def generate_response(processed_input: Dict[str, Any]) -> str:
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
            with fluxloop.instrument("test_run"):
                result = run("Hello, what can you help me with?")
                print(f"Result: {result}")
        '''
    ).strip() + "\n"


def create_gitignore() -> str:
    """Create a .gitignore file."""

    return dedent(
        """
        # Python
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
    ).strip() + "\n"


def create_env_file() -> str:
    """Create a .env template file."""

    return dedent(
        """
        # FluxLoop Configuration
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
    ).strip() + "\n"
"""
Templates for generating configuration and code files.
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
