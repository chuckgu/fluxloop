"""
Templates for generating configuration and code files.
"""

from textwrap import dedent, indent

from fluxloop_cli.evaluation.prompts import get_prompt_bundle


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
        f"""
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

    intent_prompt = indent(get_prompt_bundle("intent_recognition").with_header(), "              ")
    consistency_prompt = indent(get_prompt_bundle("response_consistency").with_header(), "              ")
    clarity_prompt = indent(get_prompt_bundle("response_clarity").with_header(), "              ")
    completeness_prompt = indent(get_prompt_bundle("information_completeness").with_header(), "              ")

    intent_sample = get_prompt_bundle("intent_recognition").sample_response
    consistency_sample = get_prompt_bundle("response_consistency").sample_response
    clarity_sample = get_prompt_bundle("response_clarity").sample_response
    completeness_sample = get_prompt_bundle("information_completeness").sample_response

    sample_indent = "                "
    intent_sample_block = indent(intent_sample.strip(), sample_indent)
    consistency_sample_block = indent(consistency_sample.strip(), sample_indent)
    clarity_sample_block = indent(clarity_sample.strip(), sample_indent)
    completeness_sample_block = indent(completeness_sample.strip(), sample_indent)

    return dedent(
        f"""
        # FluxLoop Evaluation Configuration
        # ------------------------------------------------------------
        # Controls how experiment results are evaluated.
        # - evaluators: rule-based or LLM judges that score each trace
        # - aggregate: how scores combine into a final pass/fail decision
        # - limits: cost-control knobs for LLM-based evaluators
        # - success_criteria / additional_analysis / report / advanced: Phase 2 features
        # Fill in or adjust the notes below to match your project.

        # ------------------------------------------------------------
        # Evaluation Goal (Phase 2)
        # Appears in reports / dashboards; describe desired outcome.
        evaluation_goal:
          text: |
            Verify that the agent provides clear, persona-aware responses
            while meeting latency and accuracy targets.

        # ------------------------------------------------------------
        # Evaluators (Phase 1 compatible)
        # Add/remove evaluators as needed. Rule-based examples below.
        evaluators:
          - name: not_empty
            type: rule_based
            enabled: true
            weight: 0.2
            rules:
              - check: output_not_empty

          - name: latency_budget
            type: rule_based
            enabled: true
            weight: 0.2
            rules:
              - check: latency_under
                budget_ms: 1500

          - name: keyword_quality
            type: rule_based
            enabled: true
            weight: 0.1
            rules:
              - check: contains
                target: output
                keywords: ["help", "assist"]
              - check: not_contains
                target: output
                keywords: ["error", "sorry"]

          - name: similarity_to_expected
            type: rule_based
            enabled: true
            weight: 0.1
            rules:
              - check: similarity
                target: output
                expected_path: metadata.expected
                method: difflib

          - name: intent_recognition
            type: llm_judge
            enabled: true
            weight: 0.25
            model: gpt-5-mini
            model_parameters:
              reasoning:
                effort: medium
              text:
                verbosity: medium
            prompt_template: |
{intent_prompt}
            max_score: 10
            parser: first_number_1_10
            metadata:
              sample_response: |
{intent_sample_block}

          - name: response_consistency
            type: llm_judge
            enabled: true
            weight: 0.25
            model: gpt-5-mini
            model_parameters:
              reasoning:
                effort: medium
              text:
                verbosity: medium
            prompt_template: |
{consistency_prompt}
            max_score: 10
            parser: first_number_1_10
            metadata:
              sample_response: |
{consistency_sample_block}

          - name: response_clarity
            type: llm_judge
            enabled: true
            weight: 0.2
            model: gpt-5-mini
            model_parameters:
              reasoning:
                effort: medium
              text:
                verbosity: medium
            prompt_template: |
{clarity_prompt}
            max_score: 10
            parser: first_number_1_10
            metadata:
              sample_response: |
{clarity_sample_block}

          - name: information_completeness
            type: llm_judge
            enabled: false
            weight: 0.1
            model: gpt-5-mini
            model_parameters:
              reasoning:
                effort: medium
              text:
                verbosity: medium
            prompt_template: |
{completeness_prompt}
            max_score: 10
            parser: first_number_1_10
            metadata:
              sample_response: |
{completeness_sample_block}

        # ------------------------------------------------------------
        # Aggregation Settings
        aggregate:
          method: weighted_sum      # or "average"
          threshold: 0.7            # pass/fail threshold
          by_persona: true          # group stats per persona

        # ------------------------------------------------------------
        # Limits (LLM cost controls)
        limits:
          sample_rate: 1.0          # evaluate 100% of traces with LLM
          max_llm_calls: 50         # cap total LLM API calls
          timeout_seconds: 60
          cache: evaluation_cache.jsonl

        # ------------------------------------------------------------
        # Success Criteria (Phase 2)
        # Leave disabled fields as false/None if you do not need them.
        success_criteria:
          performance:
            all_traces_successful: true
            avg_response_time:
              enabled: true
              threshold_ms: 2000
            max_response_time:
              enabled: false
              threshold_ms: 5000
            error_rate:
              enabled: false
              threshold_percent: 5

          quality:
            intent_recognition: true
            response_consistency: true
            response_clarity: true
            information_completeness: false

          functionality:
            tool_calling:
              enabled: false
              all_calls_successful: false
              appropriate_selection: false
              correct_parameters: false
              proper_timing: false
              handles_failures: false

        # ------------------------------------------------------------
        # Additional Analysis (Phase 2)
        additional_analysis:
          persona:
            enabled: false
            focus_personas: []      # e.g., ["expert_user", "novice_user"]

          performance:
            detect_outliers: false
            trend_analysis: false

          failures:
            enabled: false
            categorize_causes: false

          comparison:
            enabled: false
            baseline_path: ""      # path to baseline summary.json

        # ------------------------------------------------------------
        # Report Configuration (Phase 2)
        report:
          style: standard           # quick | standard | detailed

          sections:
            executive_summary: true
            key_metrics: true
            detailed_results: true
            statistical_analysis: false
            failure_cases: true
            success_examples: false
            recommendations: true
            action_items: true

          visualizations:
            charts_and_graphs: true
            tables: true
            interactive: true       # generate HTML with charts

          tone: balanced            # technical | executive | balanced
          output: both              # md | html | both
          template_path: null       # override with custom HTML template

        # ------------------------------------------------------------
        # Advanced Settings (Phase 2+)
        advanced:
          statistical_tests:
            enabled: false
            significance_level: 0.05
            confidence_interval: 0.95

          outliers:
            detection: true
            handling: analyze_separately   # remove | analyze_separately | include

          alerts:
            enabled: false
            conditions:
              - metric: "error_rate"
                threshold: 10
                operator: ">"
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

        # LLM API Keys (if needed)
        OPENAI_API_KEY=
        # ANTHROPIC_API_KEY=

        # Other Configuration
        # Add your custom environment variables here
        """
    ).strip() + "\n"
