---
title: AI 어시스턴트 통합 가이드 - FluxLoop 완전 설정
audience: AI 코딩 어시스턴트 (Cursor, Claude Code, GitHub Copilot 등)
purpose: AI 어시스턴트가 사용자의 에이전트 코드에 FluxLoop을 자동으로 통합할 수 있도록 지원
---

# AI 어시스턴트 가이드: 에이전트 코드에 FluxLoop 통합하기

## AI 어시스턴트를 위한 컨텍스트

이 가이드는 AI 코딩 어시스턴트가 사용자의 AI 에이전트 코드에 FluxLoop SDK를 통합하고 전체 테스트 워크플로우를 실행할 수 있도록 단계별 지침을 제공합니다. 사용자가 "FluxLoop 추가해줘" 또는 "내 에이전트를 FluxLoop으로 테스트해줘"라고 요청할 때 이 지침을 순차적으로 따르세요.

---

## 빠른 의사결정 트리

**Q: 사용자가 무엇을 가지고 있나요?**

- ✅ 기존 에이전트 코드가 있음 → [섹션 1: 통합](#섹션-1-통합-단계)로 이동
- ❌ 에이전트 코드가 없음 → [섹션 0: 새 프로젝트 설정](#섹션-0-새-프로젝트-설정-선택사항)으로 시작

**Q: 에이전트가 어떤 프레임워크를 사용하나요?**

- LangChain → [LangChain 통합](#langchain-통합) 사용
- LangGraph → [LangGraph 통합](#langgraph-통합) 사용
- 커스텀/기타 → [일반 통합](#일반-통합) 사용

---

## 섹션 0: 새 프로젝트 설정 (선택사항)

사용자가 기존 에이전트 프로젝트가 없는 경우:

```bash
# FluxLoop 설치
pip install fluxloop-cli fluxloop

# 새 FluxLoop 프로젝트 생성
fluxloop init project --name <프로젝트명>
cd fluxloop/<프로젝트명>
```

생성되는 구조:
```
fluxloop/<프로젝트명>/
├── setting.yaml          # 실험 설정
├── .env                  # API 키와 설정
├── experiments/          # 결과 출력 디렉토리
├── inputs/               # 생성된 입력
└── recordings/           # 녹화된 함수 인자
```

---

## 섹션 1: 통합 단계

### 단계 1.1: FluxLoop SDK 설치

사용자의 프로젝트에 추가:

```bash
# pip 사용 시
pip install fluxloop

# poetry 사용 시
poetry add fluxloop

# requirements.txt 사용 시
echo "fluxloop>=0.1.0" >> requirements.txt
pip install -r requirements.txt
```

### 단계 1.2: 대상 함수 식별

**사용자에게 질문하거나 코드에서 추론:**

- 에이전트의 주요 진입점 함수는 무엇인가요?
- 함수 매개변수는 무엇인가요?
- 동기(sync)인가요 비동기(async)인가요?
- 어떤 프레임워크를 사용하나요 (있다면)?

**찾아볼 일반적인 패턴:**

```python
# 패턴 1: WebSocket/Socket.IO 핸들러
async def handle_message(connection_id, data, session, callbacks):
    ...

# 패턴 2: HTTP 엔드포인트 핸들러
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    ...

# 패턴 3: LangChain 에이전트
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(...)
result = agent_executor.invoke({"input": user_input})

# 패턴 4: LangGraph 워크플로우
from langgraph.graph import StateGraph
workflow = StateGraph(...)
result = workflow.invoke(initial_state)

# 패턴 5: 일반 함수
def process_user_query(query: str, context: dict):
    ...
```

### 단계 1.3: FluxLoop 임포트 추가

대상 파일 상단에 추가:

```python
import fluxloop
from fluxloop import trace, FluxLoopClient

# 선택사항: 명시적 설정을 위해
# from fluxloop import configure
```

---

## 섹션 2: 프레임워크별 통합

### LangChain 통합

#### 옵션 A: AgentExecutor 호출에 데코레이터 추가

```python
from fluxloop import trace
from langchain.agents import AgentExecutor

# 기존 코드
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# FluxLoop 추적 추가
@trace()
def run_agent(user_input: str):
    """추적되는 에이전트 실행"""
    result = agent_executor.invoke({"input": user_input})
    return result

# 사용
result = run_agent("오늘 날씨 어때?")
```

#### 옵션 B: LangChain 콜백 사용 (가능한 경우)

```python
from fluxloop.integrations.langchain import FluxLoopCallbackHandler

# 에이전트 실행 시
callbacks = [FluxLoopCallbackHandler()]
result = agent_executor.invoke(
    {"input": user_input},
    config={"callbacks": callbacks}
)
```

### LangGraph 통합

```python
from fluxloop import trace
from langgraph.graph import StateGraph

# 그래프 구축
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("action", action_node)
# ... 그래프 설정 ...
app = workflow.compile()

# 전체 워크플로우 호출을 래핑
@trace()
def run_workflow(initial_input: dict):
    """추적되는 LangGraph 워크플로우"""
    result = app.invoke(initial_input)
    return result

# 사용
result = run_workflow({"messages": [user_message]})
```

### 일반 통합

커스텀 에이전트 또는 모든 Python 함수:

```python
from fluxloop import trace

@trace()
async def handle_user_request(
    user_id: str,
    message: str,
    session_data: dict,
    callbacks: dict
):
    """
    FluxLoop 추적이 있는 에이전트 로직.
    FluxLoop이 자동으로 캡처:
    - 함수 입력 (user_id, message, session_data, callbacks)
    - 함수 출력 (반환값)
    - 실행 중 발생한 모든 LLM 호출 (OpenAI/Anthropic 등 사용 시)
    - 실행 시간 및 오류
    """
    # 기존 에이전트 로직
    response = await your_agent_logic(message, session_data)
    
    # 선택사항: 콜백으로 전송
    if callbacks.get('send'):
        await callbacks['send'](response)
    
    return response
```

---

## 섹션 3: 프로덕션 컨텍스트 녹화

현실적인 프로덕션 컨텍스트(세션 데이터, 콜백 등)로 테스트를 재생하려면 실제 함수 호출을 녹화하세요:

### 단계 3.1: 녹화 설정

애플리케이션 시작 시 추가:

```python
import fluxloop

# main.py 또는 앱 초기화에서
fluxloop.configure(
    record_args=True,
    recording_file="./recordings/args.jsonl"
)
```

### 단계 3.2: 함수 인자 녹화

대상 함수 내부에 녹화 호출 추가:

```python
@trace()
async def handle_message(connection_id, data, user_session, send_callback, error_callback):
    # 재생을 위해 실제 인자 녹화
    fluxloop.record_call_args(
        target="app.handler:MessageHandler.handle_message",  # 모듈:클래스.메서드 형식
        connection_id=connection_id,
        data=data,
        user_session=user_session,
        send_callback=send_callback,
        error_callback=error_callback,
    )
    
    # 에이전트 로직
    result = await process_message(data, user_session)
    await send_callback(result)
    return result
```

### 단계 3.3: 녹화 트리거

사용자에게 요청:

1. 애플리케이션을 정상적으로 실행 (개발/스테이징 환경)
2. 실제 요청 하나로 에이전트 트리거
3. `recordings/args.jsonl`이 생성되었는지 확인

---

## 섹션 4: FluxLoop 프로젝트 설정

### 단계 4.1: FluxLoop 디렉토리 초기화

프로젝트에 FluxLoop 작업공간 생성:

```bash
# 디렉토리 생성
mkdir -p fluxloop/my-test
cd fluxloop/my-test
mkdir -p experiments inputs recordings
```

### 단계 4.2: 설정 파일 생성

`setting.yaml` 생성:

```yaml
# FluxLoop 설정
project_name: "my-agent-test"

# 테스트할 대상 함수
runner:
  target: "app.handler:MessageHandler.handle_message"  # 이 경로 업데이트
  working_directory: "../.."  # 이 설정 파일에서 프로젝트 루트까지의 경로

# 입력 생성 설정
input_generation:
  provider: "openai"  # 또는 "anthropic"
  model: "gpt-4o-mini"
  prompt: |
    고객 지원 에이전트를 위한 다양한 사용자 메시지를 생성하세요.
    다음을 변형하세요:
    - 톤: 공손함, 화남, 혼란스러움, 분노, 캐주얼
    - 길이: 매우 짧음 (1-3단어), 짧음, 중간, 긴 글 (100단어 이상)
    - 언어: 한글, 영어, 혼합, 오타, 은어
    - 엣지 케이스: 빈 문자열, 특수 문자, 이모지, 코드 스니펫
    - 내용: 단순 요청, 복잡한 다중 요청, 불명확한 의도

# 인자 재생 설정 (녹화된 args 사용 시)
replay_args:
  enabled: true
  recording_file: "recordings/args.jsonl"
  override_param_path: "data.content"  # 생성된 입력으로 대체할 매개변수
  callable_providers:
    send_callback: "builtin:collector.send"  # 테스트용 모의 콜백
    error_callback: "builtin:collector.error"

# 실험 설정
inputs_file: "inputs/generated.yaml"
iterations: 50  # 실행할 테스트 케이스 수
output_directory: "experiments"
experiment_name: "variation-test"

# 선택사항: LLM 추적
collector:
  enabled: true
  endpoint: "http://localhost:8000"  # 선택사항: FluxLoop 수집기 서비스
```

### 단계 4.3: 환경 파일 생성

`.env` 파일 생성:

```bash
# LLM 제공자용 API 키
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# FluxLoop 설정 (선택사항)
FLUXLOOP_ENV=development
FLUXLOOP_PROJECT_ID=my-agent
```

---

## 섹션 5: 테스트 입력 생성

### 단계 5.1: 녹화 파일에서 입력 생성

녹화 파일이 있는 경우:

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording recordings/args.jsonl \
  --limit 100
```

이렇게 하면 100개의 변형을 가진 `inputs/generated.yaml`이 생성됩니다.

### 단계 5.2: 처음부터 입력 생성

녹화가 없는 경우, 먼저 수동 템플릿 생성:

`inputs/template.yaml` 생성:

```yaml
inputs:
  - persona: "baseline"
    data:
      content: "안녕하세요, 주문 관련 도움이 필요합니다"
      metadata:
        channel: "web"
```

그런 다음 변형 생성:

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-template inputs/template.yaml \
  --limit 100
```

### 단계 5.3: 생성된 입력 확인

`inputs/generated.yaml` 확인:

```bash
head -50 inputs/generated.yaml
```

다음과 같은 변형을 볼 수 있어야 합니다:

```yaml
inputs:
  - persona: "polite_formal"
    data:
      content: "안녕하세요, 최근 주문 추적에 도움이 필요합니다."
  - persona: "frustrated_caps"
    data:
      content: "내 주문 어디있어요??? 몇 주째 기다리고 있는데!!!"
  - persona: "minimal_typo"
    data:
      content: "ㅇㅇ 좀 도와줘"
  # ... 97개 더
```

---

## 섹션 6: 실험 실행

### 단계 6.1: 테스트 실행

```bash
fluxloop run experiment --config setting.yaml
```

**무슨 일이 일어나나요:**
1. FluxLoop이 100개의 생성된 입력을 로드
2. 각 입력에 대해 대상 함수를 다음과 같이 호출:
   - 변형된 입력 (`data.content` 또는 지정된 파라미터 대체)
   - 실제 녹화된 컨텍스트 (세션, 콜백 등)
3. 모든 LLM 호출, 타이밍, 출력 캡처
4. `experiments/<이름>_<타임스탬프>/`에 결과 기록

### 단계 6.2: 진행 상황 모니터링

CLI에서 실시간 진행 상황 표시:

```
Running experiment: variation-test
Progress: [====================] 100/100 (100%)
Success: 85 | Failed: 15 | Duration: 3m 24s
```

### 단계 6.3: 결과 디렉토리 확인

```bash
ls -la experiments/variation-test_20241022_143052/
```

출력 파일:
- `summary.json` - 전체 통계 (성공률, 평균 실행 시간 등)
- `trace_summary.jsonl` - 테스트 케이스당 한 줄
- `observations.jsonl` - 단계별 상세 추적
- `traces.jsonl` - 전체 실행 추적

---

## 섹션 7: 결과 분석

### 단계 7.1: 사람이 읽을 수 있는 형식으로 파싱

```bash
fluxloop parse experiment \
  experiments/variation-test_20241022_143052 \
  --output per_trace_analysis \
  --overwrite
```

각 테스트 케이스마다 개별 Markdown 파일 생성:

```
experiments/variation-test_20241022_143052/per_trace_analysis/
├── 00_polite_formal.md
├── 01_frustrated_caps.md
├── 02_minimal_typo.md
├── ...
└── 99_edge_case_empty.md
```

### 단계 7.2: 실패 검토

파싱된 파일을 열어 정확히 무슨 일이 있었는지 확인:

```markdown
# 추적 분석: frustrated_caps

**Trace ID:** 9eb64d0d-7bbf-41d0-9226-0bfc86892109  
**Persona:** frustrated_caps  
**상태:** ❌ 실패  
**실행 시간:** 2.3초  

## 입력
```json
{
  "content": "내 주문 어디있어요??? 몇 주째 기다리고 있는데!!!"
}
```

## 출력
```json
{
  "error": "요청 처리 불가 - 주문 ID 누락"
}
```

## 타임라인
1. **에이전트 시작** (0.0초)
2. **LLM 호출 - 의도 인식** (0.1초)
   - 모델: gpt-4o-mini
   - 감지된 의도: "order_tracking"
   - order_id 추출 실패
3. **오류 핸들러** (2.1초)
   - 이유: 필수 필드 'order_id' 누락
```

### 단계 7.3: 패턴 식별

일반적인 실패 패턴 찾기:

```bash
# 유형별 실패 건수
grep -h "상태: ❌" experiments/*/per_trace_analysis/*.md | wc -l

# 모든 실패 케이스 찾기
grep -l "상태: ❌" experiments/*/per_trace_analysis/*.md
```

---

## 섹션 8: 반복 및 개선

### 단계 8.1: 식별된 문제 수정

실패를 기반으로 에이전트 코드 업데이트:

```python
# 이전: 화난/대문자 입력에서 에이전트 실패
@trace()
async def handle_message(connection_id, data, user_session, callbacks):
    # 입력 정규화 누락
    result = await process(data['content'])
    return result

# 이후: 입력 전처리 추가
@trace()
async def handle_message(connection_id, data, user_session, callbacks):
    # 입력 정규화
    content = data['content'].strip().lower()
    
    # 검증
    if not content:
        return {"error": "빈 메시지", "fallback": "human_agent"}
    
    # LLM 프롬프트에 컨텍스트 추가
    enhanced_prompt = f"""
    사용자 메시지 (화날 수 있고, 대문자 사용, 오타 포함 가능): {data['content']}
    원래 톤: 보존하되 전문적으로 응답
    """
    
    result = await process(enhanced_prompt, user_session)
    return result
```

### 단계 8.2: 입력 재생성 (선택사항)

`setting.yaml`의 생성 프롬프트를 업데이트하여 특정 엣지 케이스에 집중:

```yaml
input_generation:
  prompt: |
    다음에 초점을 맞춘 고객 지원 메시지를 생성하세요:
    - 주문 ID 누락 (암시적 vs 명시적)
    - 욕설을 포함한 극도의 분노
    - 여러 언어 혼합
    - 매우 긴 장황한 메시지 (200단어 이상)
```

### 단계 8.3: 테스트 재실행

```bash
# 업데이트된 프롬프트로 새 입력 생성
fluxloop generate inputs --config setting.yaml --limit 100

# 실험 다시 실행
fluxloop run experiment --config setting.yaml

# 결과 비교
fluxloop parse experiment experiments/<new_experiment_dir>
```

---

## 섹션 9: 일반적인 통합 패턴

### 패턴 1: WebSocket 핸들러

```python
from fluxloop import trace
import socketio

sio = socketio.AsyncServer()

@sio.on('message')
@trace()
async def handle_socket_message(sid, data):
    """FluxLoop이 모든 WebSocket 메시지 추적"""
    fluxloop.record_call_args(
        target="app:handle_socket_message",
        sid=sid,
        data=data
    )
    
    response = await agent.process(data['content'])
    await sio.emit('response', response, room=sid)
    return response
```

### 패턴 2: FastAPI 엔드포인트

```python
from fastapi import FastAPI
from fluxloop import trace

app = FastAPI()

@app.post("/chat")
@trace()
async def chat_endpoint(request: ChatRequest):
    """FluxLoop이 모든 API 요청 추적"""
    fluxloop.record_call_args(
        target="app:chat_endpoint",
        request=request.dict()
    )
    
    result = await agent.chat(request.message, request.session_id)
    return {"response": result}
```

### 패턴 3: Discord 봇

```python
import discord
from fluxloop import trace

client = discord.Client()

@client.event
@trace()
async def on_message(message):
    """FluxLoop이 모든 Discord 메시지 추적"""
    if message.author == client.user:
        return
    
    fluxloop.record_call_args(
        target="bot:on_message",
        message=message.content,
        author=message.author.name,
        channel=message.channel.name
    )
    
    response = await agent.process(message.content)
    await message.channel.send(response)
```

### 패턴 4: Slack 봇

```python
from slack_bolt.async_app import AsyncApp
from fluxloop import trace

app = AsyncApp()

@app.event("message")
@trace()
async def handle_message_events(event, say):
    """FluxLoop이 모든 Slack 메시지 추적"""
    fluxloop.record_call_args(
        target="slack_bot:handle_message_events",
        event=event,
        user=event['user'],
        text=event['text']
    )
    
    response = await agent.process(event['text'])
    await say(response)
```

---

## 섹션 10: 문제 해결

### 문제 1: 임포트 에러

**에러:** `ModuleNotFoundError: No module named 'fluxloop'`

**해결책:**
```bash
pip install fluxloop
# 또는
pip install --upgrade fluxloop
```

### 문제 2: 대상 함수를 찾을 수 없음

**에러:** `Could not import target: app.handler:MessageHandler.handle_message`

**해결책:**
- 모듈 경로가 올바른지 확인
- 파일이 PYTHONPATH에 있는지 확인
- 절대 임포트 사용
- `setting.yaml`의 `runner.working_directory` 업데이트

**디버그:**
```bash
# working_directory에서 시도:
python -c "from app.handler import MessageHandler; print(MessageHandler.handle_message)"
```

### 문제 3: 녹화 파일이 생성되지 않음

**에러:** `FileNotFoundError: recordings/args.jsonl`

**해결책:**
```python
# 녹화 전에 configure() 호출 확인
import fluxloop

fluxloop.configure(
    record_args=True,
    recording_file="./recordings/args.jsonl"  # 전체 경로 권장
)

# 필요시 디렉토리 생성
import os
os.makedirs("recordings", exist_ok=True)
```

### 문제 4: LLM 호출이 캡처되지 않음

**문제:** 추적에 실행은 나타나지만 LLM 호출이 없음

**해결책:**
- 지원되는 LLM 클라이언트 사용 확인 (OpenAI, Anthropic, LangChain)
- FluxLoop이 이러한 라이브러리를 자동으로 계측
- 커스텀 클라이언트의 경우 래핑:

```python
from fluxloop import trace_llm_call

response = trace_llm_call(
    provider="custom",
    model="my-model",
    messages=[{"role": "user", "content": prompt}],
    call_fn=lambda: my_custom_llm_client.chat(prompt)
)
```

### 문제 5: 실험이 실행되지만 출력 없음

**에러:** `experiments/` 디렉토리 비어있음

**해결책:**
- `setting.yaml`의 `output_directory` 확인
- 쓰기 권한 확인
- 콘솔 출력에서 오류 확인
- `iterations` > 0 확인

### 문제 6: 입력 생성 실패

**에러:** `OpenAI API key not found`

**해결책:**
```bash
# API 키 설정
export OPENAI_API_KEY=sk-...

# 또는 .env 파일에
echo "OPENAI_API_KEY=sk-..." >> .env

# 또는 setting.yaml에 (권장하지 않음, 환경 변수 사용)
input_generation:
  api_key: "sk-..."
```

---

## 섹션 11: AI 어시스턴트 워크플로우 체크리스트

사용자의 FluxLoop 통합을 도울 때 이 체크리스트를 따르세요:

### 단계 1: 발견
- [ ] 주요 에이전트 진입점 함수 식별
- [ ] 동기/비동기 여부 결정
- [ ] 사용 중인 프레임워크 확인 (있다면)
- [ ] 모든 함수 매개변수 나열
- [ ] 프로덕션 컨텍스트 녹화 원하는지 확인

### 단계 2: 설치
- [ ] 의존성에 `fluxloop` 추가
- [ ] pip/poetry/requirements.txt로 설치
- [ ] 설치 확인: `python -c "import fluxloop; print(fluxloop.__version__)"`

### 단계 3: 코드 통합
- [ ] 파일 상단에 임포트 추가
- [ ] 대상 함수에 `@trace()` 데코레이터 추가
- [ ] (선택) 재생을 위해 `fluxloop.record_call_args()` 추가
- [ ] (선택) 시작 시 `fluxloop.configure()` 추가
- [ ] 코드가 여전히 정상적으로 실행되는지 테스트

### 단계 4: FluxLoop 프로젝트 설정
- [ ] `fluxloop/` 디렉토리 구조 생성
- [ ] `setting.yaml` 설정 생성
- [ ] API 키가 포함된 `.env` 생성
- [ ] 프로젝트 구조에 맞게 설정의 경로 업데이트

### 단계 5: 녹화 (선택사항)
- [ ] 사용자가 애플리케이션을 정상적으로 실행
- [ ] 사용자가 실제 요청으로 에이전트 트리거
- [ ] `recordings/args.jsonl`이 생성되었는지 확인
- [ ] 녹화를 검사하여 데이터가 올바른지 확인

### 단계 6: 입력 생성
- [ ] `fluxloop generate inputs` 명령 실행
- [ ] `inputs/generated.yaml`이 생성되었는지 확인
- [ ] 처음 몇 개의 입력을 검사하여 다양성 확인
- [ ] 필요시 생성 프롬프트 조정

### 단계 7: 실험 실행
- [ ] `fluxloop run experiment` 명령 실행
- [ ] 콘솔에서 진행 상황 모니터링
- [ ] 실험이 완료되었는지 확인
- [ ] 출력 디렉토리가 생성되었는지 확인

### 단계 8: 분석
- [ ] `fluxloop parse experiment` 명령 실행
- [ ] 추적별 분석 파일 검토
- [ ] 실패 패턴 식별
- [ ] 사용자에게 발견 사항 요약

### 단계 9: 반복
- [ ] 식별된 문제 수정 지원
- [ ] 실험 재실행
- [ ] 이전/이후 결과 비교
- [ ] 만족스러운 성공률까지 반복

---

## 섹션 12: AI 어시스턴트용 코드 템플릿

### 템플릿: 최소 통합

사용자가 간단한 에이전트 함수를 가진 경우 사용:

```python
# 상단에 이 임포트 추가
from fluxloop import trace

# 메인 함수에 데코레이터 추가
@trace()
def agent_function(user_input: str) -> str:
    """에이전트 로직"""
    # 기존 코드는 그대로 유지
    response = your_existing_logic(user_input)
    return response
```

### 템플릿: 녹화를 포함한 전체 통합

사용자가 프로덕션 컨텍스트 재생을 원하는 경우 사용:

```python
import fluxloop
from fluxloop import trace

# 애플리케이션 시작 시 (예: main.py)
fluxloop.configure(
    record_args=True,
    recording_file="./recordings/args.jsonl"
)

# 핸들러 파일에서
@trace()
async def handle_request(param1, param2, param3):
    """메인 에이전트 진입점"""
    
    # 재생을 위한 인자 녹화
    fluxloop.record_call_args(
        target="<모듈_경로>:<클래스명>.<메서드명>",
        param1=param1,
        param2=param2,
        param3=param3
    )
    
    # 기존 에이전트 로직
    result = await your_agent(param1, param2)
    
    return result
```

### 템플릿: setting.yaml

이 템플릿을 사용하고 사용자의 필요에 맞게 커스터마이즈:

```yaml
project_name: "<프로젝트명>"

runner:
  target: "<모듈>:<클래스>.<메서드>"  # 예: "app.handler:MessageHandler.handle_message"
  working_directory: "."  # 프로젝트 루트까지의 경로

input_generation:
  provider: "openai"
  model: "gpt-4o-mini"
  prompt: |
    <이_프롬프트를_커스터마이즈>
    AI 에이전트 테스트를 위한 다양한 입력을 생성하세요.
    톤, 길이, 언어, 엣지 케이스를 변형하세요.

replay_args:
  enabled: false  # 녹화 사용 시 true로 설정
  recording_file: "recordings/args.jsonl"
  override_param_path: "data.content"  # 변형할 파라미터
  callable_providers: {}  # 필요시 모의 콜백 추가

inputs_file: "inputs/generated.yaml"
iterations: 50
output_directory: "experiments"
experiment_name: "test-run"
```

---

## 섹션 13: 성공 기준

통합 후 사용자와 함께 다음 결과를 확인하세요:

### ✅ 통합 성공
- [ ] `@trace()` 데코레이터로 에이전트 코드가 정상적으로 실행
- [ ] FluxLoop에서 오류나 경고 없음
- [ ] (선택) 유효한 데이터로 녹화 파일 생성

### ✅ 생성 성공
- [ ] `inputs/generated.yaml`에 원하는 수의 변형 포함
- [ ] 입력이 다양한 패턴 표시 (톤, 길이, 엣지 케이스)
- [ ] 입력이 에이전트 도메인에 현실적

### ✅ 실험 성공
- [ ] 크래시 없이 실험 완료
- [ ] 출력 디렉토리에 모든 예상 파일 포함
- [ ] `summary.json`에 합리적인 성공/실패율 표시
- [ ] 추적별 분석 파일 생성되고 읽기 가능

### ✅ 분석 성공
- [ ] 사용자가 실패 패턴 식별 가능
- [ ] 사용자가 특정 입력이 왜 실패했는지 이해
- [ ] 사용자에게 개선을 위한 실행 가능한 다음 단계 있음

---

## AI 어시스턴트를 위한 최종 참고사항

### 모범 사례

1. **항상 경로 확인**: 명령 실행 전 파일 존재와 경로가 올바른지 확인
2. **작게 시작**: 먼저 5-10개 입력으로 테스트 후 50-100개로 확장
3. **진행하며 설명**: 각 단계가 무엇을 하는지 사용자가 이해하도록 도움
4. **예제 표시**: 결과 파싱 시 1-2개의 실제 추적 표시
5. **반복**: FluxLoop은 반복적 - 여러 사이클을 거치도록 도움

### 단계를 건너뛸 때

- **녹화 건너뛰기**: 에이전트가 단순 입력만 가진 경우 (문자열/숫자만)
- **녹화 건너뛰기**: 사용자가 수동으로 입력 변형 생성을 원하는 경우
- **생성 건너뛰기**: 사용자가 이미 테스트 데이터셋을 가진 경우
- **파싱 건너뛰기**: 사용자가 Markdown보다 JSON 분석 선호 시

### 일반적인 사용자 요청

- "내 에이전트에 FluxLoop 추가해줘" → 전체 통합 (섹션 1-8)
- "다양한 입력으로 내 에이전트 테스트해줘" → 생성 및 실험 집중 (섹션 5-7)
- "왜 내 에이전트가 이 입력들에서 실패하지?" → 분석 및 반복 (섹션 7-8)
- "프로덕션 시나리오를 어떻게 재생하지?" → 녹화 및 재생 (섹션 3)

---

**AI 어시스턴트 가이드 끝**

더 자세한 내용은 다음을 참조하세요:
- [End-to-End Workflow](./end-to-end-workflow.md)
- [Virtual Environment Setup](./virtual-environment-setup.md)
- 메인 문서: https://docs.fluxloop.dev

