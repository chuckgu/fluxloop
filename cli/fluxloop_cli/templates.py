"""
Templates for generating configuration and code files.
"""

from textwrap import dedent


def create_project_config(project_name: str) -> str:
    """Create default project-level configuration content."""

    return dedent(
        f"""
        # FluxLoop Project Configuration
        # ------------------------------------------------------------
        # Describes global metadata and defaults shared across the project.
        # Update name/description/tags to suit your workspace.
        name: {project_name}
        description: AI agent simulation project
        version: 1.0.0

        # FluxLoop VSCode extension will prompt to set this path
        source_root: ""

        # Optional collector settings (leave null if using offline mode only)
        collector_url: null
        collector_api_key: null

        # Tags and metadata help downstream tooling categorize experiments
        tags:
          - simulation
          - testing

        metadata:
          team: development
          environment: local
          # Add any custom fields used by dashboards or automation tools.
        """
    ).strip() + "\n"


def create_input_config() -> str:
    """Create default input configuration content."""

    return dedent(
        """
        # FluxLoop Input Configuration
        # ------------------------------------------------------------
        # Defines personas, base inputs, and generation modes.
        # Adjust personas/goals/strategies based on your target scenarios.
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
            # Tip: Add persona-specific context that can be injected into prompts.

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
            # Tip: Include any tone/style expectations in characteristics.

        base_inputs:
          - input: "How do I get started?"
            expected_intent: help
            # Provide optional 'metadata' or 'expected' fields to guide evaluation.

        # ------------------------------------------------------------
        # Input generation settings
        # - variation_strategies: transformations applied when synthesizing inputs.
        # - variation_count / temperature: tune diversity of generated samples.
        # - inputs_file: location where generated inputs will be saved/loaded.
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
            # Replace provider/model/api_key according to your LLM setup.
        """
    ).strip() + "\n"


def create_simulation_config(project_name: str) -> str:
    """Create default simulation configuration content."""

    return dedent(
        f"""
        # FluxLoop Simulation Configuration
        # ------------------------------------------------------------
        # Controls how experiments execute (iterations, runner target, output paths).
        # Adjust runner module/function to point at your agent entry point.
        name: {project_name}_experiment
        description: AI agent simulation experiment

        iterations: 10           # Number of times to cycle through inputs/personas
        parallel_runs: 1          # Increase for concurrent execution (ensure thread safety)
        run_delay_seconds: 0      # Optional delay between runs to avoid rate limits
        seed: 42                  # Set for reproducibility; remove for randomness

        runner:
          module_path: "examples.simple_agent"
          function_name: "run"
          target: "examples.simple_agent:run"
          working_directory: .    # Relative to project root; adjust if agent lives elsewhere
          python_path:            # Optional custom PYTHONPATH entries
          timeout_seconds: 120   # Abort long-running traces
          max_retries: 3         # Automatic retry attempts on error

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
        # ------------------------------------------------------------
        # This file controls how experiment results are evaluated.
        # - evaluators: define individual checks (rule-based or LLM).
        # - aggregate: sets how evaluator scores combine into a final score.
        # - limits: cost-control knobs for LLM-based evaluators.
        # Fill in or adjust notes below to match your project.
        evaluators:
          # ----------------------------------------------------------
          # Rule-based evaluator: ensures outputs are not empty.
          # Adjust keywords/fields if your traces structure differs.
          - name: not_empty
            type: rule_based
            enabled: true
            weight: 0.2
            rules:
              - check: output_not_empty

          # ----------------------------------------------------------
          # Rule-based evaluator: checks for required/forbidden keywords.
          # Update keywords/target fields based on your success criteria.
          - name: keyword_quality
            type: rule_based
            enabled: true
            weight: 0.2
            rules:
              - check: contains
                target: output
                keywords: ["help", "assist"]
              - check: not_contains
                target: output
                keywords: ["sorry", "cannot"]

          # ----------------------------------------------------------
          # Rule-based evaluator: compares output to expected text (if available).
          # Provide expected outputs in metadata when generating inputs.
          - name: similarity_to_expected
            type: rule_based
            enabled: true
            weight: 0.2
            rules:
              - check: similarity
                target: output
                expected_path: metadata.expected     # path inside trace metadata
                method: difflib

          # ----------------------------------------------------------
          # Rule-based evaluator: enforces latency budgets per trace.
          # Adjust budget_ms to your SLA and supply duration_ms in summaries.
          - name: latency_budget
            type: rule_based
            enabled: true
            weight: 0.2
            rules:
              - check: latency_under
                budget_ms: 1000

          # ----------------------------------------------------------
          # LLM evaluator: optional semantic quality scoring.
          # Enable after setting valid LLM credentials and adjusting prompt/model.
          - name: llm_response_quality
            type: llm_judge
            enabled: false
            weight: 0.2
            model: gpt-5-mini
            prompt_template: |
              You are an expert judge. Score the assistant's response from 1-10.
              Input: {input}
              Output: {output}
              Consider relevance, completeness, clarity.
              Answer with: "Score: <number>" and a one-line reason.
            max_score: 10
            parser: first_number_1_10

        aggregate:
          # ----------------------------------------------------------
          # Weighted sum: combines evaluator scores based on provided weights.
          # Adjust threshold to tune pass criteria. by_persona groups stats.
          method: weighted_sum
          threshold: 0.7
          by_persona: true

        limits:
          # ----------------------------------------------------------
          # Sample/call limits safeguard LLM usage.
          # Lower sample_rate or max_llm_calls to reduce cost for large runs.
          sample_rate: 0.3
          max_llm_calls: 50
          timeout_seconds: 60
          cache: evaluation_cache.jsonl
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
