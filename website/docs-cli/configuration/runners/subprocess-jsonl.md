---
title: Subprocess (JSONL Protocol)
sidebar_position: 7
tags: [subprocess, jsonl, node, go, p0]
---

## 개요

- **사용 시점**: 타 언어 런타임(Node.js, Go, Rust 등) 에이전트 연동
- **난이도**: ⭐⭐ 중급
- **우선순위**: P0 (Production-Ready)
- **의존성**: 실행 가능한 바이너리/스크립트, JSONL 프로토콜 구현

로컬 프로세스를 실행하여 STDIN/STDOUT으로 JSONL(JSON Lines) 메시지를 교환. Python 외 언어로 작성된 에이전트를 통합할 때 사용.

## 기본 설정

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
```

## 전체 옵션

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]      # 실행 명령어 (배열)
    cwd: .                              # 작업 디렉터리
    env:                                # 환경변수 (선택)
      NODE_ENV: production
      API_KEY: "${API_KEY}"             # 환경변수 치환
    protocol: jsonl                     # 현재 jsonl만 지원
    
    stream_output_path: "delta"         # JSONL 이벤트 내 델타 경로
    ready_pattern: "^READY$"            # 선택: 시작 준비 신호 (정규식)
    timeout: 120s                       # 전체 실행 타임아웃
    
    # 프로세스 관리
    kill_signal: SIGTERM                # 종료 시그널 (기본)
    kill_timeout: 5s                    # 강제 종료 대기 시간
    
  guards:
    max_duration: 180s
```

## JSONL 프로토콜 규약

### FluxLoop → 프로세스 (STDIN)

**입력 메시지**
```json
{"type": "input", "input": "User query here", "context": {"persona": "expert_user", "iteration": 1}}
```

### 프로세스 → FluxLoop (STDOUT)

**스트리밍 델타** (선택)
```json
{"type": "delta", "delta": "First chunk"}
{"type": "delta", "delta": " second chunk"}
```

**최종 응답**
```json
{"type": "final", "output": "Complete response text"}
```

**에러 보고** (선택)
```json
{"type": "error", "error": "Something went wrong", "code": "INTERNAL_ERROR"}
```

### 준비 신호 (선택)

프로세스가 초기화 완료 후 STDOUT에 출력:
```
READY
```

FluxLoop이 이 줄을 감지한 후 입력 메시지를 전송.

## 예제

### 예제 1: Node.js Echo 에이전트

**agent.mjs**
```javascript
import readline from 'readline';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// 준비 신호
console.log('READY');

rl.on('line', (line) => {
  const msg = JSON.parse(line);
  
  if (msg.type === 'input') {
    const response = `Echo from Node.js: ${msg.input}`;
    console.log(JSON.stringify({ type: 'final', output: response }));
  }
});
```

**configs/simulation.yaml**
```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
    ready_pattern: "^READY$"
```

**실행**
```bash
fluxloop run experiment
```

### 예제 2: Node.js 스트리밍 에이전트 (OpenAI)

**streaming_agent.mjs**
```javascript
import OpenAI from 'openai';
import readline from 'readline';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

console.log('READY');

rl.on('line', async (line) => {
  const msg = JSON.parse(line);
  
  if (msg.type === 'input') {
    const stream = await client.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: msg.input }],
      stream: true,
    });
    
    for await (const chunk of stream) {
      const delta = chunk.choices[0]?.delta?.content || '';
      if (delta) {
        console.log(JSON.stringify({ type: 'delta', delta }));
      }
    }
    
    console.log(JSON.stringify({ type: 'final', output: '[STREAM_END]' }));
  }
});
```

**configs/simulation.yaml**
```yaml
runner:
  process:
    command: ["node", "streaming_agent.mjs"]
    protocol: jsonl
    stream_output_path: "delta"
    ready_pattern: "^READY$"
    timeout: 120s
```

### 예제 3: Go 에이전트

**agent.go**
```go
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
)

type InputMessage struct {
    Type    string                 `json:"type"`
    Input   string                 `json:"input"`
    Context map[string]interface{} `json:"context"`
}

type OutputMessage struct {
    Type   string `json:"type"`
    Output string `json:"output"`
}

func main() {
    fmt.Println("READY")
    
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        var msg InputMessage
        if err := json.Unmarshal(scanner.Bytes(), &msg); err != nil {
            continue
        }
        
        if msg.Type == "input" {
            response := OutputMessage{
                Type:   "final",
                Output: "Response from Go: " + msg.Input,
            }
            data, _ := json.Marshal(response)
            fmt.Println(string(data))
        }
    }
}
```

**빌드 & 설정**
```bash
go build -o agent agent.go
```

**configs/simulation.yaml**
```yaml
runner:
  process:
    command: ["./agent"]
    protocol: jsonl
    ready_pattern: "^READY$"
```

## 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| 프로세스 시작 실패 | 명령어 경로 오류 | `command` 절대 경로 사용 또는 `cwd` 조정 |
| JSONL 파싱 실패 | 잘못된 JSON 형식 | STDERR 로그 확인, 프로세스 디버깅 |
| 타임아웃 | 응답 느림 또는 무한 대기 | `timeout` 증가, `ready_pattern` 확인 |
| 준비 신호 미감지 | 패턴 불일치 | 정규식 테스트, STDOUT 버퍼링 해제 |
| 출력 누락 | STDOUT 버퍼링 | Node: `console.log`, Go: `fmt.Println` 사용 (자동 플러시) |
| 프로세스 좀비 | 종료 실패 | `kill_signal`/`kill_timeout` 조정 |

## 고급 주제

### 환경변수 격리

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    env:
      NODE_ENV: production
      API_KEY: "${OPENAI_API_KEY}"      # .env 파일에서 로드
    # 시스템 환경변수는 기본적으로 상속됨
```

### 에러 처리

프로세스가 에러를 보고:

```json
{"type": "error", "error": "API rate limit exceeded", "code": "RATE_LIMIT"}
```

FluxLoop은 이를 실험 실패로 기록하고 다음 입력으로 진행.

### 준비 신호 없이 즉시 실행

간단한 프로세스는 `ready_pattern` 생략 가능:

```yaml
runner:
  process:
    command: ["python", "simple_agent.py"]
    protocol: jsonl
    # ready_pattern 생략 → 즉시 입력 전송
```

단, 초기화 시간이 긴 프로세스는 첫 입력 손실 가능.

### 여러 입력 처리 (재사용)

기본적으로 FluxLoop은 각 입력마다 새 프로세스를 실행. 재사용하려면 프로세스가 여러 입력을 순차 처리하도록 구현:

```javascript
// Node.js 재사용 예시
rl.on('line', async (line) => {
  const msg = JSON.parse(line);
  if (msg.type === 'input') {
    const output = await process_input(msg.input);
    console.log(JSON.stringify({ type: 'final', output }));
  }
});
```

설정에서 재사용 모드 활성화 (추후 지원 예정):

```yaml
runner:
  process:
    command: ["node", "agent.mjs"]
    protocol: jsonl
    reuse: true                         # 프로세스 재사용 (P1 roadmap)
```

## 성능

- **시작 오버헤드**: 프로세스 생성(~10-100ms). 반복 실험 시 누적 가능.
- **병렬 실행**: `simulation.parallelism`으로 여러 프로세스 동시 실행.
- **메모리**: 각 프로세스는 독립 메모리 공간 사용.

## 보안

- **입력 검증**: 프로세스는 악의적 입력 가능성 고려해야 함.
- **샌드박싱**: 컨테이너 환경에서 실행 권장 (P2: Docker 패턴).
- **로그 민감정보**: API 키 등이 STDOUT/STDERR에 노출되지 않도록 주의.

## 관련 문서

- HTTP REST (Coming soon) – 원격 서비스 통합
- Container Docker (Coming soon) – 격리된 프로세스 실행
- Streaming Schema (Coming soon) – 고급 델타 경로 설정
- Guards (Coming soon) – 타임아웃/리소스 제한
- [Simulation Config](../simulation-config) – 전체 설정 구조

## MCP 메타데이터

```json
{
  "pattern": "subprocess-jsonl",
  "tags": ["subprocess", "jsonl", "node", "go", "rust", "p0", "cross-language"],
  "examples": [
    "examples/node-agent/",
    "samples/go-jsonl.md",
    "samples/rust-stdio.md"
  ],
  "faq": [
    "How to debug JSONL parsing errors?",
    "Process reuse vs per-input spawn?",
    "Environment variable passing?",
    "Ready signal best practices?"
  ],
  "related_patterns": [
    "http-rest",
    "container-docker",
    "streaming-schema"
  ],
  "dependencies": [
    "Node.js/Go/Rust runtime",
    "JSONL protocol implementation"
  ]
}
```

