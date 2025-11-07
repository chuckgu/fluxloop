---
title: Python Function & Method
sidebar_position: 1
tags: [python, sync, async, p0]
---

## 개요

- **사용 시점**: Python 모듈의 함수 또는 메서드를 직접 호출
- **난이도**: ⭐ 초급
- **우선순위**: P0 (Production-Ready)
- **의존성**: Python 3.8+, FluxLoop SDK (선택)

가장 간단하고 일반적인 통합 패턴. 동기/비동기 함수 모두 지원.

## 기본 설정

### 패턴 1: Module + Function (간결)

```yaml
runner:
  target: "app.agent:run"
  working_directory: .
```

### 패턴 2: Module + Function (명시)

```yaml
runner:
  module_path: "app.agent"
  function_name: "run"
  working_directory: .
```

## 전체 옵션

```yaml
runner:
  target: "app.agent:run"           # 또는 module_path + function_name
  working_directory: .               # 모듈 import 기준 디렉터리
  python_path:                       # sys.path에 추가할 경로 (선택)
    - "src"
    - "lib"
  
  # 리소스 가드 (선택)
  guards:
    max_duration: 120s
    output_char_limit: 20000
```

## 함수 시그니처 요구사항

### 기본 시그니처 (권장)

```python
def run(input: str) -> str:
    """
    Args:
        input: 시뮬레이션 입력 텍스트
    Returns:
        응답 텍스트
    """
    return f"Response to: {input}"
```

### 비동기 함수

```python
async def run(input: str) -> str:
    await asyncio.sleep(0.1)
    return f"Async response to: {input}"
```

### 컨텍스트 포함 (고급)

```python
def run(input: str, context: dict = None) -> str:
    """
    Args:
        input: 시뮬레이션 입력
        context: 추가 메타데이터 (persona, iteration 등)
    """
    persona = context.get("persona", "default") if context else "default"
    return f"[{persona}] Response to: {input}"
```

## 예제

### 예제 1: 간단한 Echo 에이전트

**app/agent.py**
```python
def run(input: str) -> str:
    return f"Echo: {input}"
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.agent:run"
  working_directory: .

output:
  directory: "experiments"
```

**실행**
```bash
fluxloop run experiment
```

### 예제 2: OpenAI 호출 (비동기)

**app/openai_agent.py**
```python
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat(input: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": input}]
    )
    return response.choices[0].message.content
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.openai_agent:chat"
  working_directory: .
  guards:
    max_duration: 60s
```

### 예제 3: FluxLoop SDK 통합 (트레이싱)

**app/traced_agent.py**
```python
from fluxloop_sdk import fluxloop

@fluxloop.trace()
def run(input: str) -> str:
    # SDK가 자동으로 입력/출력/타이밍 기록
    result = process_request(input)
    return result

def process_request(input: str) -> str:
    # 비즈니스 로직
    return f"Processed: {input}"
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.traced_agent:run"
  working_directory: .
```

SDK는 자동으로 컨텍스트를 전파하여 trace/span 정보를 기록합니다.

## 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError` | 모듈 경로 불일치 | `working_directory` 또는 `python_path` 조정 |
| 함수가 호출되지 않음 | 함수명 오타 | `target` 문자열 확인 (`module:function`) |
| 비동기 함수 에러 | 이벤트 루프 충돌 | FluxLoop이 자동 처리하지만, 중첩 루프 시 `nest_asyncio` 필요 |
| 출력이 `None` | `return` 누락 | 함수가 명시적으로 문자열 반환하는지 확인 |
| 타임아웃 | 장시간 실행 | `guards.max_duration` 늘리거나 함수 최적화 |

## 고급 주제

### 모듈 스코프 인스턴스 메서드 (Bound Method)

모듈에 이미 생성된 인스턴스의 메서드를 호출:

**app/server.py**
```python
class SupportServer:
    def __init__(self, model: str):
        self.model = model
    
    def respond(self, input: str) -> str:
        return f"[{self.model}] Response: {input}"

# 모듈 레벨에서 인스턴스 생성
support_server = SupportServer(model="gpt-4")
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.server:support_server.respond"
```

### 클래스 메서드 (무인자 생성자)

클래스를 런타임에 인스턴스화 (생성자 인자 없음):

**app/handler.py**
```python
class Handler:
    def __init__(self):
        # 무인자 생성자
        self.config = load_config()
    
    def handle(self, input: str) -> str:
        return f"Handled: {input}"
```

**configs/simulation.yaml**
```yaml
runner:
  target: "app.handler:Handler.handle"
```

생성자에 인자가 필요하면 [python-factory](./python-factory) 패턴 사용.

## 관련 문서

- [Python Class with Factory](./python-factory) – 복잡한 생성자 의존성
- [Python Async Generator](./python-async-generator) – 스트리밍 응답
- [Guards](./guards) – 리소스 제한
- [SDK Tracing Guide](../../../docs-sdk/guides/tracing) – 자동 계측

## MCP 메타데이터

```json
{
  "pattern": "python-function",
  "tags": ["python", "sync", "async", "p0", "basic"],
  "examples": [
    "examples/simple-agent/",
    "samples/openai-basic.md"
  ],
  "faq": [
    "How to pass context to function?",
    "Can I use async functions?",
    "ModuleNotFoundError troubleshooting"
  ],
  "related_patterns": [
    "python-class",
    "python-factory",
    "python-async-generator"
  ]
}
```

