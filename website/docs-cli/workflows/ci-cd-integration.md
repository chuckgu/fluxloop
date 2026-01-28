---
sidebar_position: 3
---

# CI/CD Integration

Integrate FluxLoop into CI/CD pipelines for automated agent testing and regression detection.

## Overview

FluxLoop can be integrated into CI/CD pipelines to:

- **Automate regression testing** after code changes
- **Validate agent quality** before deployment
- **Track performance trends** over time

- **Generate test reports** for stakeholders

This guide covers GitHub Actions, GitLab CI, and generic CI/CD setup.

---

## Quick Setup

### Prerequisites

1. FluxLoop project with configuration in `configs/`
2. Agent code instrumented with FluxLoop SDK
3. Base inputs defined in `configs/input.yaml`

5. API keys (OpenAI, Anthropic, etc.) stored as secrets

### Key Principles

**For CI/CD environments:**

1. **Use deterministic mode** for input generation (or commit pre-generated inputs)
2. **Set fixed seed** in `configs/simulation.yaml` for reproducibility
3. **Cache dependencies** (Python packages, MCP index)
4. **Store API keys as secrets**, not in code
5. **Generate artifacts** (reports, traces) for review


---

## GitHub Actions

### Basic Workflow

Create `.github/workflows/fluxloop-test.yml`:

```yaml
name: FluxLoop Agent Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-agent:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install fluxloop-cli fluxloop
          pip install -r requirements.txt
      
      - name: Verify setup
        run: fluxloop doctor
      
      - name: Generate inputs (deterministic)
        run: |
          cd fluxloop/my-agent
          fluxloop generate inputs --limit 20 --mode deterministic
      
      - name: Run agent tests
        env:
          FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
        run: |
          cd my-agent
          fluxloop sync pull
          fluxloop test
      
      - name: Parse results
        run: |
          cd fluxloop/my-agent
          LATEST_EXP=$(ls -td results/*/ | head -1)
          fluxloop parse experiment "$LATEST_EXP"
      
      - name: Evaluate results
        run: |
          cd fluxloop/my-agent
          LATEST_EXP=$(ls -td results/*/ | head -1)
      
      - name: Check evaluation threshold
        run: |
          cd fluxloop/my-agent
          LATEST_EXP=$(ls -td results/*/ | head -1)
          python3 << 'EOF'
          import json
          import sys
          
              summary = json.load(f)
          
          score = summary.get("overall_score", 0)
          threshold = 0.7
          
          print(f"Score: {score:.2f}, Threshold: {threshold}")
          
          if score < threshold:
              print(f"FAIL: Score {score:.2f} below threshold {threshold}")
              sys.exit(1)
          else:
              print(f"PASS: Score {score:.2f} meets threshold {threshold}")
          EOF
      
      - name: Upload test artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: fluxloop-results
          path: |
            fluxloop/my-agent/results/
            fluxloop/my-agent/inputs/
          retention-days: 30
      
      - name: Comment on PR (if PR)
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const expDir = 'fluxloop/my-agent/results/';
            const latest = fs.readdirSync(expDir)
              .filter(f => fs.statSync(expDir + f).isDirectory())
              .sort()
              .reverse()[0];
            
            const summary = JSON.parse(
            );
            
            const body = `
            ## FluxLoop Evaluation Results
            
            **Overall Score:** ${summary.overall_score.toFixed(2)} / 1.00
            **Status:** ${summary.pass_fail_status}
            **Traces:** ${summary.total_traces}
            
            ### Evaluator Scores
            ${Object.entries(summary.by_evaluator || {}).map(([name, data]) => 
              `- **${name}**: ${data.score.toFixed(2)}`
            ).join('\n')}
            
            [View Full Report](../actions/runs/${context.runId})
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### Advanced: Comparison with Baseline

Compare results against a baseline:

```yaml
      - name: Download baseline results
        uses: dawidd6/action-download-artifact@v3
        with:
          workflow: fluxloop-test.yml
          branch: main
          name: baseline-summary
          path: baseline/
        continue-on-error: true
      
      - name: Compare with baseline
        run: |
          cd fluxloop/my-agent
          LATEST_EXP=$(ls -td results/*/ | head -1)
          
          if [ -f "baseline/summary.json" ]; then
              --baseline baseline/summary.json
          fi
      
      - name: Save new baseline (on main)
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: baseline-summary
```

### Scheduled Regression Testing

Run tests on a schedule:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:      # Manual trigger
```

---

## GitLab CI

### Basic Pipeline

Create `.gitlab-ci.yml`:

```yaml
image: python:3.11

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

stages:
  - setup
  - test
  
  - report

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install fluxloop-cli fluxloop
  - pip install -r requirements.txt

setup:
  stage: setup
  script:
    - cd fluxloop/my-agent
    - fluxloop doctor
    - fluxloop config validate
  artifacts:
    reports:
      dotenv: build.env

generate_inputs:
  stage: setup
  script:
    - cd fluxloop/my-agent
    - fluxloop generate inputs --limit 20 --mode deterministic
  artifacts:
    paths:
      - fluxloop/my-agent/inputs/
    expire_in: 1 week

run_experiment:
  stage: test
  dependencies:
    - generate_inputs
  script:
    - cd fluxloop/my-agent
    - fluxloop test --iterations 1
  artifacts:
    paths:
      - fluxloop/my-agent/results/
    expire_in: 1 month

parse_results:
  dependencies:
    - run_experiment
  script:
    - cd fluxloop/my-agent
    - LATEST_EXP=$(ls -td results/*/ | head -1)
    - fluxloop parse experiment "$LATEST_EXP"
  artifacts:
    paths:
      - fluxloop/my-agent/results/*/per_trace_analysis/
    expire_in: 1 month

generate_report:
  stage: report
  dependencies:
    _results
  script:
    - cd fluxloop/my-agent
    - LATEST_EXP=$(ls -td results/*/ | head -1)
  artifacts:
    paths:
      - public
  only:
    - main
```

---

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
        FLUXLOOP_ENABLED = 'true'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install fluxloop-cli fluxloop
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Verify') {
            steps {
                sh '''
                    . venv/bin/activate
                    cd fluxloop/my-agent
                    fluxloop doctor
                    fluxloop config validate
                '''
            }
        }
        
        stage('Generate Inputs') {
            steps {
                sh '''
                    . venv/bin/activate
                    cd fluxloop/my-agent
                    fluxloop generate inputs --limit 20 --mode deterministic
                '''
            }
        }
        
        stage('Run Experiment') {
            steps {
                sh '''
                    . venv/bin/activate
                    cd fluxloop/my-agent
                    fluxloop test --iterations 1
                '''
            }
        }
        
        stage('Evaluate') {
            steps {
                sh '''
                    . venv/bin/activate
                    cd fluxloop/my-agent
                    LATEST_EXP=$(ls -td results/*/ | head -1)
                    fluxloop parse experiment "$LATEST_EXP"
                '''
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    def score = summary.overall_score
                    
                    if (score < 0.7) {
                        error("Quality gate failed: score ${score} below 0.7")
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'fluxloop/my-agent/results/**/*', 
                             allowEmptyArchive: true
            
            publishHTML([
                reportDir: 'fluxloop/my-agent/results/*/evaluation/',
                reportFiles: 'report.html',
                reportName: 'FluxLoop Evaluation Report'
            ])
        }
    }
}
```

---

## Docker Integration

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fluxloop-cli \
    fluxloop \
    -r requirements.txt

# Copy project
COPY . .

# Set up FluxLoop
RUN cd fluxloop/my-agent && \
    fluxloop doctor

# Default command
CMD ["bash", "-c", "cd fluxloop/my-agent && fluxloop test"]
```

### Docker Compose for Testing

```yaml
version: '3.8'

services:
  fluxloop-test:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLUXLOOP_ENABLED=true
    volumes:
      - ./fluxloop:/app/fluxloop
      - test-results:/app/fluxloop/my-agent/experiments
    command: |
      bash -c "
        cd fluxloop/my-agent &&
        fluxloop generate inputs --limit 20 --mode deterministic &&
        fluxloop test --iterations 1 &&
        fluxloop parse experiment results/*/ &&
      "

volumes:
  test-results:
```

Run tests:

```bash
docker-compose run fluxloop-test
```

---

## Best Practices

### 1. Use Deterministic Mode in CI

```yaml
# configs/input.yaml (for CI)
input_generation:
  mode: deterministic  # or commit pre-generated inputs

# configs/simulation.yaml
seed: 42  # Fixed seed for reproducibility
```

### 2. Separate Test Configs from Production

```bash
fluxloop/my-agent/
├── configs/              # Production configs
│   ├── project.yaml
│   ├── input.yaml
│   ├── simulation.yaml
│   └── evaluation.yaml
└── configs-ci/           # CI-specific configs
    ├── input.yaml        # Deterministic, fewer inputs
    ├── simulation.yaml   # Lower iterations, fixed seed
    └── evaluation.yaml   # Stricter thresholds
```

Run with CI configs:

```bash
# Override config directory
cp -r configs-ci/* configs/
fluxloop test
```

### 3. Cache Wisely

**Cache these:**
- Python packages (`pip cache`)
- Generated inputs (if deterministic)
- MCP index (`~/.fluxloop/mcp/index/`)

**Don't cache:**
- Experiment outputs
- Traces
- Evaluation results

### 4. Store Secrets Securely

**GitHub Actions:**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**GitLab CI:**
```yaml
variables:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**Jenkins:**
```groovy
environment {
    OPENAI_API_KEY = credentials('openai-api-key')
}
```

### 5. Set Quality Gates

```python
# check_quality.py
import json
import sys

    summary = json.load(f)

score = summary["overall_score"]
threshold = 0.7

# Can also check individual evaluators
intent_score = summary["by_evaluator"]["intent_recognition"]["score"]
latency_score = summary["by_evaluator"]["token_budget"]["score"]

if score < threshold:
    print(f"❌ FAIL: Overall score {score:.2f} < {threshold}")
    sys.exit(1)

if intent_score < 0.8:
    print(f"❌ FAIL: Intent recognition {intent_score:.2f} < 0.8")
    sys.exit(1)

print(f"✅ PASS: All quality gates passed")
```

---

## Monitoring and Reporting

### Track Metrics Over Time

Store evaluation results in a time-series database:

```python
# upload_metrics.py
import json
import requests
from datetime import datetime

    summary = json.load(f)

# Send to monitoring system
requests.post("https://metrics.example.com/fluxloop", json={
    "timestamp": datetime.now().isoformat(),
    "project": "my-agent",
    "branch": os.getenv("CI_COMMIT_BRANCH"),
    "overall_score": summary["overall_score"],
    "by_evaluator": summary["by_evaluator"],
    "total_traces": summary["total_traces"],
})
```

### Generate Trend Reports

```bash
# Compare last N runs
python3 << 'EOF'
import json
import glob


for exp in experiments:
    with open(exp) as f:
        summary = json.load(f)
    print(f"{exp}: {summary['overall_score']:.2f}")
EOF
```

---

## Troubleshooting CI/CD

### Tests Pass Locally but Fail in CI

**Common causes:**

1. **Missing environment variables**
   ```bash
   # Check what's set
   fluxloop config env
   ```

2. **Different Python version**
   ```yaml
   # Pin Python version
   python-version: '3.11'
   ```

3. **Non-deterministic inputs**
   ```yaml
   # Use fixed seed
   seed: 42
   mode: deterministic
   ```

### Slow CI Runs

**Optimizations:**

1. **Reduce test scope**
   ```bash
   # Fewer inputs
   fluxloop generate inputs --limit 10
   
   # Single iteration
   fluxloop test --iterations 1
   ```

2. **Sample LLM evaluations**
   ```yaml
   # configs/evaluation.yaml
   limits:
     sample_rate: 0.2  # Only 20% of traces
     max_llm_calls: 10
   ```

3. **Cache dependencies**
   ```yaml
   - uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
   ```

---

## Example: Full GitHub Actions Workflow

Comprehensive example with all best practices:

```yaml
name: FluxLoop CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Cache MCP index
        uses: actions/cache@v4
        with:
          path: ~/.fluxloop/mcp/index
          key: mcp-index-v1
      
      - name: Install dependencies
        run: |
          pip install fluxloop-cli fluxloop fluxloop-mcp
          pip install -r requirements.txt
      
      - name: Verify installation
        run: fluxloop doctor
      
      - name: Prepare test environment
        run: |
          cd fluxloop/my-agent
          cp -r configs-ci/* configs/
          fluxloop config validate
      
      - name: Run tests
        env:
          FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
        run: |
          cd my-agent
          fluxloop sync pull
          fluxloop test
      
      - name: Quality gate
        run: |
          cd fluxloop/my-agent
          python3 scripts/check_quality.py
      
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: results-py${{ matrix.python-version }}
          path: fluxloop/my-agent/results/
      
      - name: Report to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            // ... (PR comment script from earlier)
```

---

## See Also

- [Basic Workflow](/cli/workflows/basic-workflow) - Standard FluxLoop workflow
- [Multi-Turn Workflow](/cli/workflows/multi-turn-workflow) - Dynamic conversations
- [Commands Reference](/cli/commands/test) - CLI command documentation
