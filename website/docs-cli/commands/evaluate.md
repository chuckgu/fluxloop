---
sidebar_position: 5
---

# evaluate Command

`fluxloop evaluate experiment` 소비자는 파싱된 트레이스를 종합해서 **단일 HTML 대시보드**로 만들어 줍니다. 내부적으로 다음 다섯 단계를 자동으로 실행합니다:

1. **LLM-PT (Per-Trace)** – GPT-5가 각 트레이스를 7개 메트릭(완수, 환각, 관련성, 도구 사용, 만족도, 명확성, 페르소나)으로 채점하고 이슈 타임라인/퀵픽스를 작성합니다.
2. **Rule Aggregation** – 통계/패스율/성능 카드/페르소나 격차를 계산하고 FAIL・PARTIAL・REVIEW 케이스를 분류합니다.
3. **LLM-OV (Overall)** – 집계 데이터를 다시 GPT-5에 전달하여 임원 요약, Response Quality 관찰, 우선순위 권장사항을 생성합니다.
4. **Data Preparation** – `configs/project.yaml`, `configs/input.yaml`, `configs/evaluation.yaml`, `summary.json` 등을 하나의 페이로드로 합칩니다.
5. **HTML Rendering** – `evaluation_report/report.html` (기본값)을 생성합니다. 이 파일 하나만 브라우저로 열면 모든 지표를 볼 수 있습니다.

> `fluxloop evaluate` 를 실행하기 전에 **반드시** `fluxloop parse experiment <experiment_dir>` 로 `per_trace_analysis/per_trace.jsonl`을 만들어 두세요. 파일을 옮겼다면 `--per-trace` 로 경로를 지정하십시오.

## Prerequisites

1. `fluxloop run experiment`
2. `fluxloop parse experiment <experiment_dir>`

## Basic Usage

```bash
# Parse → Evaluate
fluxloop parse experiment experiments/demo_run_20231215_123456
fluxloop evaluate experiment experiments/demo_run_20231215_123456

# 사용자 정의 evaluation.yaml 사용
fluxloop evaluate experiment experiments/demo_run_20231215_123456 \
  --config configs/evaluation.yaml

# 출력 디렉터리 변경(기본값: evaluation_report)
fluxloop evaluate experiment experiments/demo_run_20231215_123456 \
  --output dashboards/latest_eval \
  --overwrite
```

완료되면 다음과 같은 메시지가 출력됩니다.

```
📊 Evaluating experiment at experiments/demo_run_20231215_123456
🧵 Per-trace data: …/per_trace_analysis/per_trace.jsonl
📁 Output: …/evaluation_report
…
✅ Report ready: …/evaluation_report/report.html
```

## Command Options

| Option | Description | Default |
| --- | --- | --- |
| `experiment_dir` | 실험 디렉터리 경로 | 필수 |
| `--config`, `-c` | `configs/evaluation.yaml` 위치 | `configs/evaluation.yaml` |
| `--output`, `-o` | 대시보드를 생성할 디렉터리 | `evaluation_report` |
| `--overwrite` | 기존 디렉터리를 삭제 후 재생성 | `false` |
| `--llm-api-key` | GPT-5 호출에 사용할 API Key | `FLUXLOOP_LLM_API_KEY` 또는 `OPENAI_API_KEY` |
| `--per-trace` | `per_trace_analysis/per_trace.jsonl` 경로 | 자동 감지 |
| `--verbose` | 단계별 로그를 자세히 출력 | `false` |

## Pipeline Output

```
experiments/<run>/
└── evaluation_report/
    └── report.html
```

`report.html`에는 다음 섹션이 들어 있습니다.

- Executive Summary + Pass Rate 게이지
- Trace × Metric 매트릭스
- 실패/마진/리뷰 케이스 타임라인 및 이슈 요약
- 토큰/턴/지연시간 카드 + 이상치 목록 + 페르소나 격차 시각화
- LLM-OV가 작성한 Response Quality 관찰, 패턴, Quick Wins, 추천조치

별도의 정적 파일이 없으므로 `report.html` 하나만 공유하면 됩니다.

## Configuration Highlights (`configs/evaluation.yaml`)

CLI 0.2.30부터는 **메트릭 기반 스키마**를 사용합니다. 템플릿 예시는 다음과 같습니다.

```yaml
evaluation_goal: "안전하게 취소/환불을 완료하는지 검증"

metrics:
  task_completion:
    enabled: true
    thresholds: {good: 80, fair: 60}
  hallucination:
    enabled: true
    thresholds: {good: 5, fair: 15}
  relevance:
    enabled: true
    thresholds: {good: 90, fair: 80}
  tool_usage_appropriateness:
    enabled: true
    thresholds: {good: 90, fair: 80}
  user_satisfaction:
    enabled: true
    thresholds: {good: 70, fair: 50}
  clarity:
    enabled: true
    thresholds: {good: 90, fair: 80}
  persona_consistency:
    enabled: true
    thresholds: {good: 85, fair: 70}

# 효율성 카드 (토큰/턴/지연시간) 이상치 감지 방식
efficiency:
  output_tokens:
    enabled: true
    outlier_mode: statistical
    std_multiplier: 2
  conversation_depth:
    enabled: true
    outlier_mode: statistical
  latency:
    enabled: true
    outlier_mode: statistical

advanced:
  llm_judge:
    model: "gpt-5.1"
    temperature: 0.0
```

- `evaluation_goal` 은 리포트 상단과 LLM 프롬프트에 그대로 사용됩니다.
- 각 `metrics.*.thresholds` 는 Pass/Fair/Poor 게이지 기준이자 LLM-OV 프롬프트에 포함됩니다.
- `efficiency` 블록은 성능 카드의 이상치 감지 규칙을 지정합니다.
- `advanced.llm_judge` 는 LLM-PT와 LLM-OV가 사용할 모델/파라미터입니다.

페르소나/변형 전략은 `configs/input.yaml` 에 정의되며, LLM-PT 시스템 프롬프트에 자동으로 주입됩니다.

## Tips & Troubleshooting

- `per_trace_analysis/per_trace.jsonl` 이 없으면 바로 종료합니다. 필요 시 `--per-trace` 로 절대경로를 넘기세요.
- 반복 실행 시 `--overwrite` 를 추가하면 기존 `evaluation_report` 디렉터리를 삭제하고 새로 생성합니다.
- `--output relative/path` 로 명시하면 실험 폴더 내부에 커스텀 대시보드를 여러 개 만들 수 있습니다 (예: `eval_model_a`, `eval_model_b`).
- 보고서를 공유할 때는 `report.html` 파일만 전달하면 됩니다. 외부 CDN 요청이 없으므로 오프라인 뷰잉이 가능합니다.
- 파이프라인 로그를 자세히 보고 싶을 때는 `--verbose` 로 실행하세요. Stage 1~5 진행 상황이 모두 출력됩니다.

더 큰 워크플로우 예시는 [First Experiment Guide](/cli/getting-started/first-experiment) 와 [Basic Workflow](/cli/workflows/basic-workflow) 문서를 참고하세요.
