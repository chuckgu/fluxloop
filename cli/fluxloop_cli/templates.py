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
          service_context: ""
          # Describe the overall service scenario (used by multi-turn supervisor)
          # Add any custom fields used by dashboards or automation tools.
        """
    ).strip() + "\n"


def create_input_config() -> str:
    """Create default input configuration content."""

    return dedent(
        """
        # ===================================================================
        # Quick Configuration
        # - Define What would you ask to your agent? -
        # ===================================================================
        # Quick start: Fill in 1. BASE USER INPUT (required)
        # Optional fields use defaults if not specified
        # ===================================================================


        # -------------------------------------------------------------------
        # 1. BASE USER INPUT (REQUIRED)
        # -------------------------------------------------------------------
        # Start here: Write the main questions your users would ask.
        # This is your baseline - variations will be generated from this.
        # Example: "How do I get started?" or "Reset my password"

        base_inputs:
          - input: "How do I get started?"
            expected_intent: help


        # -------------------------------------------------------------------
        # 2. INPUT VARIATION STRATEGIES (OPTIONAL)
        # -------------------------------------------------------------------
        # How should the base input be transformed?
        # - rephrase: Same intent, different wording
        # - verbose: More detailed, longer questions
        # - typo: Common spelling mistakes
        # - concise: Shorter, more direct
        # Tip: Mix strategies to cover realistic user behavior patterns.

        variation_strategies:
          - rephrase
          - verbose
          - error_prone

        variation_count: 2           # How many variations per strategy
        variation_temperature: 0.7   # 0.0 = consistent, 1.0 = creative


        # -------------------------------------------------------------------
        # 3. PERSONA SETTING (OPTIONAL)
        # -------------------------------------------------------------------
        # 

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

        # ------------------------------------------------------------
        # Input generation settings
        # ------------------------------------------------------------

        inputs_file: inputs/generated.yaml

        input_generation:
          mode: llm
          llm:
            enabled: true
            provider: openai
            model: gpt-5-mini
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

        iterations: 1           # Number of times to cycle through inputs/personas
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

        multi_turn:
          enabled: false              # Enable to drive conversations via supervisor
          max_turns: 8                # Safety cap on total turns per conversation
          auto_approve_tools: true    # Automatically approve tool calls when supported
          persona_override: null      # Force a specific persona id (optional)
          supervisor:
            provider: openai          # openai (LLM generated) | mock (scripted playback)
            model: gpt-5-mini
            system_prompt: |
              You supervise an AI assistant supporting customers.
              Review the entire transcript and decide whether to continue.
              When continuing, craft the next user message consistent with the persona.
              When terminating, explain the reason and provide any closing notes.
            metadata:
              scripted_questions: []  # Array of user utterances for sequential playback (e.g., ["First question", "Second question", ...])
              mock_decision: terminate        # Fallback when no scripted questions remain
              mock_reason: script_complete    # Termination reason for scripted runs
              mock_closing: "Thanks for the help. I have no further questions."

        output_directory: experiments
        save_traces: true
        save_aggregated_metrics: true
        """
    ).strip() + "\n"


def create_evaluation_config() -> str:
    """Create default evaluation configuration content."""

    return dedent(
        """
        # ===================================================================
        # Evaluation Configuration
        # - Define how to evaluate your agent's performance -
        # ===================================================================
        # Quick start: Fill in sections marked (REQUIRED)
        # Optional sections use defaults if not specified
        # ===================================================================


        # -------------------------------------------------------------------
        # 1. EVALUATION GOAL (REQUIRED)
        # -------------------------------------------------------------------
        # What are you trying to evaluate? Write a clear, concise goal.
        # This helps the LLM judge understand the context of your evaluation.
        # Example: "Check if the agent provides accurate flight information"

        evaluation_goal:
          text: "Verify that the agent provides clear, persona-aware responses while meeting latency and accuracy targets."


        # -------------------------------------------------------------------
        # 2. METRICS TO EVALUATE (OPTIONAL)
        # -------------------------------------------------------------------
        # All metrics enabled by default with thresholds shown below.
        # Only specify if you want to disable or customize thresholds.

        metrics:

          # Task Completion Rate
          # Formula: (PASS count / total traces) × 100%
          # Default: ✅ ≥80% Good | ⚠️ 60-80% Fair | ❌ <60% Poor
          task_completion:
            enabled: true
            thresholds:
              good: 80       # ≥80%
              fair: 60       # ≥60%

          # Hallucination Rate
          # Formula: (grounding failure traces / total traces) × 100%
          # Default: ✅ ≤5% Good | ⚠️ 5-15% Fair | ❌ >15% Critical (ship blocker)
          hallucination:
            enabled: true
            thresholds:
              good: 5        # ≤5%
              fair: 15       # ≤15%

          # Relevance Rate
          # Formula: (PASS count / total traces) × 100%
          # Default: ✅ ≥90% Good | ⚠️ 80-90% Fair | ❌ <80% Poor
          relevance:
            enabled: true
            thresholds:
              good: 90       # ≥90%
              fair: 80       # ≥80%

          # Tool Usage Appropriateness
          # Formula: (APPROPRIATE count / total traces) × 100%
          # Default: ✅ ≥90% Good | ⚠️ 80-90% Fair | ❌ <80% Poor
          tool_usage_appropriateness:
            enabled: true
            thresholds:
              good: 90       # ≥90%
              fair: 80       # ≥80%

          # User Satisfaction
          # Formula: (GOOD count / total traces) × 100%
          # Default: ✅ ≥70% Good | ⚠️ 50-70% Fair | ❌ <50% Poor
          user_satisfaction:
            enabled: true
            thresholds:
              good: 70       # ≥70%
              fair: 50       # ≥50%

          # Response Clarity
          # Formula: (PASS count / total traces) × 100%
          # Default: ✅ ≥90% Good | ⚠️ 80-90% Fair | ❌ <80% Poor
          clarity:
            enabled: true
            thresholds:
              good: 90       # ≥90%
              fair: 80       # ≥80%

          # Persona Consistency
          # Formula: (PASS count / total traces) × 100%
          # Default: ✅ ≥85% Good | ⚠️ 70-85% Fair | ❌ <70% Poor
          persona_consistency:
            enabled: true
            thresholds:
              good: 85       # ≥85%
              fair: 70       # ≥70%


        # -------------------------------------------------------------------
        # EFFICIENCY METRICS (OPTIONAL)
        # -------------------------------------------------------------------
        # Statistical metrics - auto-computed from trace data.
        # Choose outlier detection mode: "statistical" or "absolute"

        efficiency:

          # Average Output Tokens
          # Outlier: statistical (Mean + n×Std exceeded) or absolute (>threshold)
          output_tokens:
            enabled: true
            outlier_mode: statistical    # "statistical" (default) or "absolute"
            std_multiplier: 2            # 1, 2, 3... (used if mode = statistical)
            # absolute_threshold: 2000   # tokens (used if mode = absolute)

          # Conversation Depth
          # Outlier: statistical (Mean + n×Std exceeded) or absolute (>threshold)
          conversation_depth:
            enabled: true
            outlier_mode: statistical    # "statistical" (default) or "absolute"
            std_multiplier: 2            # 1, 2, 3... (used if mode = statistical)
            # absolute_threshold: 6      # turns (used if mode = absolute)

          # Average Latency
          # Outlier: statistical (Mean + n×Std exceeded) or absolute (>threshold)
          latency:
            enabled: true
            outlier_mode: statistical    # "statistical" (default) or "absolute"
            std_multiplier: 2            # 1, 2, 3... (used if mode = statistical)
            # absolute_threshold: 60     # seconds (used if mode = absolute)

          # Persona Performance Gap
          # Compares efficiency metrics across different personas
          persona_gap:
            enabled: true


        # ===================================================================
        #                     OPTIONAL CONFIGURATION
        # ===================================================================
        # Everything below is optional. Defaults work for most use cases.
        # Only modify if you need custom behavior.
        # ===================================================================


        # -------------------------------------------------------------------
        # 3. OUTPUT SETTINGS (OPTIONAL)
        # -------------------------------------------------------------------
        # Configure where and how reports are generated.

        output:
          language: "en"                 # Report language: "en" (default), "ko", etc.
          summary_file: "summary.md"
          deep_analysis_file: "deep_analysis.md"
          templates:
            summary: "template.txt"
            deep_analysis: "template.txt"


        # -------------------------------------------------------------------
        # 4. ADVANCED SETTINGS (OPTIONAL)
        # -------------------------------------------------------------------
        # Fine-tune evaluation behavior. Most users can skip this section.
        # Tip: Only modify if you have specific requirements.

        advanced:
          # LLM judge configuration
          llm_judge:
            model: "gpt-5.1"
            temperature: 0.0
            # max_tokens: 1024

          # Concurrency & retry controls for LLM evaluations
          llm_concurrency: 4          # Max concurrent LLM calls (1-16)
          llm_retries: 3              # Number of retry attempts per trace before failing

          # Filter which traces to evaluate
          filters:
            personas: []                   # Empty = all personas
            include_trace_ids: []          # Empty = all traces
            exclude_trace_ids: []

          # Overall success calculation rules
          overall_success:
            use_default_rules: true
            # custom_rules: []             # Only for custom logic
        """
    ).strip() + "\n"


def create_pytest_bridge_template(config_relative_path: str) -> str:
    """Return a ready-to-run pytest smoke test referencing the bridge fixtures."""

    return dedent(
        f"""
        \"\"\"FluxLoop Pytest smoke test generated via `fluxloop init pytest-template`.\"\"\"

        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        SIMULATION_CONFIG = PROJECT_ROOT / "{config_relative_path}"


        def test_fluxloop_smoke(fluxloop_runner):
            result = fluxloop_runner(
                project_root=PROJECT_ROOT,
                simulation_config=SIMULATION_CONFIG,
                env={{"PYTHONPATH": str(PROJECT_ROOT)}},
            )
            result.require_success(label="fluxloop smoke")
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
        FLUXLOOP_RECORDING_FILE=
        # Example: recordings/args_recording.jsonl (project-relative) or absolute path

        # Service Configuration
        FLUXLOOP_SERVICE_NAME=my-agent
        FLUXLOOP_ENVIRONMENT=development

        # LLM API Keys (required for LLM evaluations)
        OPENAI_API_KEY=
        ANTHROPIC_API_KEY=
        GEMINI_API_KEY=
        """
    ).strip() + "\n"