---
title: Runner Targets (Overview)
sidebar_position: 20
---

## 개요

`configs/simulation.yaml`의 `runner` 섹션으로 FluxLoop와 에이전트 코드를 연결합니다. 다양한 언어·프레임워크·실행 환경을 지원하기 위해 여러 통합 패턴을 제공합니다.

## 통합 패턴 분류

### 🟢 P0: 기본 지원 (Production-Ready)

| 패턴 | 사용 시점 | 문서 |
|------|----------|------|
| **Python 함수/메서드** | Python 동기/비동기 함수 직접 호출 | [python-function](./runners/python-function) |
| **Python 클래스** | 클래스 인스턴스 메서드 호출 (팩토리 지원) | _Coming soon_ |
| **Python 비동기 제너레이터** | 스트리밍 응답 (OpenAI/Anthropic SDK 등) | _Coming soon_ |
| **HTTP REST/SSE** | 원격 API 또는 로컬 서버 (스트리밍 포함) | [http-sse](./runners/http-sse) |
| **WebSocket** | 양방향 스트리밍 (실시간 chat) | _Coming soon_ |
| **서브프로세스(JSONL)** | 타 언어 런타임 (Node/Go 등) 연동 | [subprocess-jsonl](./runners/subprocess-jsonl) |
| **스텝 루프** | 다단계 대화/플로우 (`step()` 반복) | _Coming soon_ |
| **리소스 가드** | 타임아웃/출력 제한 안전망 | _Coming soon_ |

### 🟡 P1: 고급 기능 (Beta)

| 패턴 | 사용 시점 | 문서 |
|------|----------|------|
| **배치 실행** | JSONL/CSV 데이터셋 병렬 평가 | _Coming soon_ |
| **고급 스트리밍 스키마** | 툴콜/함수콜 이벤트 경로 설정 | _Coming soon_ |
| **입출력 어댑터** | 함수 시그니처 변환 (프레임워크 간 매핑) | _Coming soon_ |

### 🔴 P2: 실험적 (Roadmap)

| 패턴 | 사용 시점 | 문서 |
|------|----------|------|
| **Docker 컨테이너** | 격리·재현성 (이미지 기반 실행) | _Coming soon_ |
| **Redis/SQS 큐** | 프로덕션 스케일 비동기 워커 | _Coming soon_ |
| **멀티타깃 컴포지트** | 순차/병렬/앙상블 에이전트 조합 | _Coming soon_ |

## 빠른 시작

### 1) Python 함수 (가장 간단)

```yaml
runner:
  target: "app.agent:run"
  working_directory: .
```

### 2) HTTP API (원격 서비스)

```yaml
runner:
  http:
    method: POST
    url: "http://localhost:8000/chat"
    stream: sse
```

### 3) 서브프로세스 (Node.js 에이전트)

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
```

## 공통 옵션

모든 러너에서 사용 가능:

```yaml
runner:
  # ... 패턴별 설정 ...
  
  # 공통
  working_directory: .
  python_path: ["src", "lib"]           # Python 패턴만
  stream_output_path: "message.delta"   # 스트리밍 러너
  
  # 리소스 가드 (선택)
  guards:
    max_duration: 120s
    output_char_limit: 20000
```

## Argument Replay (선택)

복잡한 kwargs 재사용:

```yaml
runner:
  target: "app.agent:run"
  
replay_args:
  enabled: true
  recording_file: recordings/args_recording.jsonl
  # override_param_path: "item.content.0.text"
```

자세한 내용은 시뮬레이션 설정 문서를 참조하세요.

## 다음 단계

- 패턴별 상세 문서에서 전체 옵션과 예제 확인
- [Simulation Config](./simulation-config) 전체 구조
- [Run Command](../commands/run) CLI 사용법

## MCP 서버 통합

본 문서와 하위 패턴 문서들은 FluxLoop MCP 서버의 지식 베이스로 사용됩니다:
- `analyze_repository` → 프레임워크 탐지 → 적합한 패턴 추천
- `generate_integration_steps` → 패턴별 체크리스트 생성
- `faq` → 각 패턴 문서의 트러블슈팅/예제 검색

MCP 서버 계획: [docs/prd/mcp_server_plan.md](https://github.com/your-org/fluxloop/blob/main/docs/prd/mcp_server_plan.md)


