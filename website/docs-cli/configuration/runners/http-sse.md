---
title: HTTP Server-Sent Events (SSE)
sidebar_position: 5
tags: [http, streaming, sse, p0]
---

## 개요

- **사용 시점**: HTTP SSE 엔드포인트를 통한 스트리밍 응답 수신
- **난이도**: ⭐⭐ 중급
- **우선순위**: P0 (Production-Ready)
- **의존성**: HTTP 서버 (로컬/원격), SSE 프로토콜 지원

Server-Sent Events 프로토콜로 실시간 스트리밍 응답을 수집. OpenAI/Anthropic 스트리밍 API, 커스텀 chat 서버 등에 사용.

## 기본 설정

```yaml
runner:
  http:
    method: POST
    url: "http://localhost:8000/chat"
    stream: sse
    stream_output_path: "delta"        # SSE 데이터 필드 내 텍스트 경로
```

## 전체 옵션

```yaml
runner:
  http:
    method: POST                        # GET/POST/PUT/PATCH
    url: "http://localhost:8000/chat"
    headers:
      Content-Type: application/json
      Authorization: "Bearer ${OPENAI_API_KEY}"  # 환경변수 치환
    timeout: 60s                        # 전체 요청 타임아웃
    retry:
      attempts: 2                       # 재시도 횟수
      backoff: 200ms                    # 재시도 간격
      status_codes: [502, 503, 504]     # 재시도 대상 상태 코드
    
    stream: sse                         # SSE 모드
    stream_output_path: "delta"         # 각 SSE 이벤트 데이터 내 텍스트 JSONPath
    stream_event_filter: "message"      # 선택: 특정 이벤트 타입만 수집
    
    body_template:                      # 요청 바디 매핑
      type: json
      mapping:
        input: "$.messages[-1].content" # 시뮬레이션 입력 → 요청 필드
        model: "gpt-4"                  # 정적 값
    
  guards:
    max_duration: 120s
    output_char_limit: 20000
```

## SSE 프로토콜 예시

### 서버 응답 스트림

```
event: message
data: {"delta": "Hello"}

event: message
data: {"delta": " world"}

event: message
data: {"delta": "!"}

event: done
data: {"finish_reason": "stop"}
```

### 텍스트 집계

`stream_output_path: "delta"` 설정 시:
1. 각 `data` JSON을 파싱
2. `$.delta` 경로로 텍스트 추출
3. 순서대로 조인 → 최종 결과: `"Hello world!"`

## 예제

### 예제 1: OpenAI 스트리밍 API

**configs/simulation.yaml**
```yaml
runner:
  http:
    method: POST
    url: "https://api.openai.com/v1/chat/completions"
    headers:
      Content-Type: application/json
      Authorization: "Bearer ${OPENAI_API_KEY}"
    timeout: 60s
    stream: sse
    stream_output_path: "choices[0].delta.content"
    body_template:
      type: json
      mapping:
        model: "gpt-4"
        messages: [{"role": "user", "content": "$.input"}]
        stream: true
```

### 예제 2: 커스텀 FastAPI SSE 서버

**server.py** (별도 실행)
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def generate_sse(input: str):
    words = f"Response to: {input}".split()
    for word in words:
        yield f"event: message\ndata: {json.dumps({'delta': word + ' '})}\n\n"
        await asyncio.sleep(0.1)
    yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"

@app.post("/chat")
async def chat(request: dict):
    input_text = request.get("input", "")
    return StreamingResponse(
        generate_sse(input_text),
        media_type="text/event-stream"
    )
```

**configs/simulation.yaml**
```yaml
runner:
  http:
    method: POST
    url: "http://localhost:8000/chat"
    stream: sse
    stream_output_path: "delta"
    body_template:
      type: json
      mapping:
        input: "$.input"
```

**실행**
```bash
# 터미널 1: 서버 실행
uvicorn server:app --port 8000

# 터미널 2: FluxLoop 실행
fluxloop run experiment
```

### 예제 3: Anthropic Claude 스트리밍

**configs/simulation.yaml**
```yaml
runner:
  http:
    method: POST
    url: "https://api.anthropic.com/v1/messages"
    headers:
      Content-Type: application/json
      x-api-key: "${ANTHROPIC_API_KEY}"
      anthropic-version: "2023-06-01"
    stream: sse
    stream_output_path: "delta.text"
    stream_event_filter: "content_block_delta"  # 텍스트 델타 이벤트만
    body_template:
      type: json
      mapping:
        model: "claude-3-opus-20240229"
        messages: [{"role": "user", "content": "$.input"}]
        max_tokens: 1024
        stream: true
```

## 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 연결 타임아웃 | 서버 미실행 또는 URL 오류 | `curl [url]`로 서버 확인 |
| SSE 파싱 실패 | 데이터 포맷 불일치 | `stream_output_path` 경로 점검, 서버 로그 확인 |
| 빈 응답 | `stream_event_filter` 불일치 | 필터 제거하거나 실제 이벤트 타입 확인 |
| 텍스트 손실 | 네트워크 끊김 | `retry.attempts` 증가, 서버 안정성 점검 |
| 환경변수 미치환 | `${}` 문법 오류 | `.env` 파일 확인, 변수명 정확성 검증 |
| 재시도 과다 | 서버 500 에러 | `retry.status_codes`에서 500 제외 고려 |

## 고급 주제

### 복잡한 JSONPath 매핑

OpenAI 형식으로 변환:

```yaml
runner:
  http:
    body_template:
      type: json
      mapping:
        model: "gpt-4-turbo"
        messages: |
          [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "$.input"}
          ]
        temperature: 0.7
```

### 이벤트 타입 필터링

특정 이벤트만 처리:

```yaml
runner:
  http:
    stream: sse
    stream_event_filter: "text_delta"   # "event: text_delta"만 수집
    stream_output_path: "content"
```

### 재시도 전략

일시적 네트워크 오류 대응:

```yaml
runner:
  http:
    retry:
      attempts: 3
      backoff: 500ms
      status_codes: [429, 502, 503, 504]  # Rate limit + 서버 오류
```

## 성능 최적화

- **타임아웃 조정**: 긴 응답 예상 시 `timeout` 증가 (기본 60s)
- **연결 재사용**: 동일 호스트 반복 호출 시 HTTP/1.1 Keep-Alive 자동 활용
- **병렬 실행**: `simulation.parallelism`으로 여러 요청 동시 처리 (단, API rate limit 고려)

## 보안

- **API 키 관리**: `.env` 파일 + `.gitignore` 등록 필수
- **HTTPS 사용**: 프로덕션 환경에서 `https://` URL 사용
- **헤더 로깅**: FluxLoop은 `Authorization` 헤더를 자동 마스킹

## 관련 문서

- [HTTP REST](./http-rest) – 비스트리밍 HTTP 요청
- [WebSocket](./http-websocket) – 양방향 스트리밍
- [Streaming Schema](./streaming-schema) – 고급 이벤트 경로 설정
- [Guards](./guards) – 타임아웃/출력 제한

## MCP 메타데이터

```json
{
  "pattern": "http-sse",
  "tags": ["http", "streaming", "sse", "p0", "openai", "anthropic"],
  "examples": [
    "examples/openai-streaming/",
    "samples/sse-fastapi.md",
    "samples/anthropic-claude.md"
  ],
  "faq": [
    "How to handle SSE reconnection?",
    "OpenAI streaming configuration?",
    "Rate limiting best practices?",
    "Environment variable interpolation?"
  ],
  "related_patterns": [
    "http-rest",
    "http-websocket",
    "streaming-schema"
  ],
  "dependencies": [
    "httpx (CLI internal)",
    "SSE-compatible server"
  ]
}
```

