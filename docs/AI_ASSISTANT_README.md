# AI Assistant Integration Guide - How to Use

## For Users (Human Developers)

### Quick Start: Using this Guide with AI IDEs

이 문서들은 **AI IDE(Cursor, Claude Code, GitHub Copilot 등)**가 자동으로 FluxLoop을 여러분의 에이전트 코드에 통합할 수 있도록 설계되었습니다.

#### 사용 방법

**방법 1: 파일 전체를 AI에게 제공**

```
@guides/ai-assistant-integration-guide.md 

내 에이전트 코드에 FluxLoop을 추가하고 테스트를 실행해줘.
```

또는 한국어로:

```
@guides/ai-assistant-integration-guide-ko.md

내 에이전트 코드에 FluxLoop SDK 통합하고 100개 입력 변형으로 테스트해줘.
```

**방법 2: 직접 복사해서 붙여넣기**

1. `guides/ai-assistant-integration-guide.md` (또는 `-ko.md`) 파일을 엽니다
2. 전체 내용을 복사합니다
3. AI IDE 채팅에 붙여넣고 요청사항을 추가합니다

**방법 3: URL로 제공 (만약 온라인에서 접근 가능하다면)**

```
이 가이드를 참조해서 작업해줘: 
https://github.com/yourrepo/fluxloop/blob/main/packages/docs/guides/ai-assistant-integration-guide.md

내 코드에 FluxLoop을 추가해줘.
```

---

## What the AI Will Do

AI 어시스턴트가 이 가이드를 받으면 다음을 수행합니다:

### 1단계: 코드 분석
- ✅ 에이전트의 주요 진입점 함수 찾기
- ✅ 사용 중인 프레임워크 식별 (LangChain, LangGraph, 커스텀 등)
- ✅ 함수 시그니처와 매개변수 분석

### 2단계: SDK 통합
- ✅ `fluxloop` 패키지 설치
- ✅ 적절한 임포트 추가
- ✅ `@trace()` 데코레이터 추가
- ✅ (선택사항) 녹화 코드 추가

### 3단계: 프로젝트 설정
- ✅ FluxLoop 디렉토리 구조 생성
- ✅ `setting.yaml` 설정 파일 생성
- ✅ `.env` 파일 설정
- ✅ 프로젝트 경로 맞게 설정

### 4단계: 테스트 실행
- ✅ 입력 변형 생성 (예: 100개)
- ✅ 실험 실행
- ✅ 결과 파싱 및 분석
- ✅ 실패 원인 요약

---

## Example Conversations

### 예시 1: 기본 통합

**You:**
```
@guides/ai-assistant-integration-guide-ko.md

내 LangChain 에이전트에 FluxLoop을 추가해줘.
파일은 app/agent.py에 있어.
```

**AI will:**
1. `app/agent.py` 파일을 읽습니다
2. LangChain 에이전트 함수를 찾습니다
3. FluxLoop 통합 코드를 추가합니다
4. `fluxloop/` 디렉토리와 설정 파일을 만듭니다
5. 설치 및 실행 명령을 제공합니다

---

### 예시 2: 전체 워크플로우

**You:**
```
@guides/ai-assistant-integration-guide.md

My agent is a FastAPI endpoint at src/api/chat.py.
Add FluxLoop, generate 50 test inputs, and run the experiment.
```

**AI will:**
1. FastAPI 엔드포인트에 `@trace()` 추가
2. FluxLoop 프로젝트 설정
3. 입력 생성 명령 실행
4. 실험 실행
5. 결과 파싱 및 실패 분석
6. 개선 제안

---

### 예시 3: 프로덕션 컨텍스트 재생

**You:**
```
@guides/ai-assistant-integration-guide-ko.md

WebSocket 핸들러를 테스트하고 싶어.
실제 세션 데이터와 콜백을 사용해서 100가지 입력으로 테스트해줘.
```

**AI will:**
1. 녹화 설정 추가 (`fluxloop.configure()`)
2. 함수 인자 녹화 코드 추가
3. 사용자에게 앱 실행 후 한 번 트리거하라고 안내
4. 녹화된 컨텍스트로 입력 생성
5. 실험 실행 및 결과 분석

---

## What You Need to Provide

AI가 작업하는 데 필요한 것들:

### 필수
- ✅ 에이전트 코드 (또는 파일 경로)
- ✅ 어떤 프레임워크 사용 중인지 (또는 AI가 추론)

### 선택사항이지만 유용
- 🔹 API 키 (OpenAI, Anthropic 등) - 입력 생성에 필요
- 🔹 테스트하고 싶은 특정 시나리오
- 🔹 예상 입력 형식 예시
- 🔹 실패하길 원하는 엣지 케이스

---

## Expected Outcomes

작업 완료 후 얻게 되는 것:

### 코드 변경사항
```python
# Before
def my_agent(user_input: str):
    return process(user_input)

# After
from fluxloop import trace

@trace()
def my_agent(user_input: str):
    return process(user_input)
```

### 새로운 파일 구조
```
your-project/
├── app/
│   └── agent.py  (수정됨 - FluxLoop 데코레이터 추가)
├── fluxloop/
│   └── my-test/
│       ├── setting.yaml
│       ├── .env
│       ├── inputs/
│       │   └── generated.yaml  (100개 변형)
│       ├── recordings/
│       │   └── args.jsonl  (선택사항)
│       └── experiments/
│           └── test-run_20241022/
│               ├── summary.json
│               ├── trace_summary.jsonl
│               ├── observations.jsonl
│               └── per_trace_analysis/
│                   ├── 00_polite.md
│                   ├── 01_angry.md
│                   └── ... (100개 파일)
```

### 분석 리포트
```
실험 결과:
- 총 100개 테스트 케이스
- ✅ 성공: 87개
- ❌ 실패: 13개

주요 실패 패턴:
1. 빈 입력 처리 실패 (5건)
2. 다국어 감지 안됨 (4건)
3. 매우 긴 입력 잘림 (4건)

권장 개선사항:
- 입력 검증 로직 추가
- 언어 감지 기능 추가
- 프롬프트 윈도우 크기 증가
```

---

## Advanced Usage

### 특정 섹션만 참조

AI에게 가이드의 특정 부분만 요청할 수 있습니다:

```
@guides/ai-assistant-integration-guide.md (Section 2만)

LangChain 통합 패턴만 보여줘.
```

### 반복 개선

```
@guides/ai-assistant-integration-guide.md (Section 8)

이전 실험에서 나온 실패를 바탕으로 코드를 개선하고 다시 테스트해줘.
```

### 커스텀 생성 프롬프트

```
@guides/ai-assistant-integration-guide.md

의료 상담 에이전트를 위한 입력을 생성해줘.
환자가 증상을 설명하는 다양한 방식을 포함해서.
```

---

## Troubleshooting

### AI가 가이드를 찾지 못하면

**해결책 1: 파일 내용 직접 복사**
```
[가이드 전체 내용을 복사해서 붙여넣기]

위 가이드를 따라서 내 에이전트에 FluxLoop을 추가해줘.
```

**해결책 2: 단계별로 요청**
```
1. 먼저 FluxLoop SDK 설치해줘
2. 내 에이전트 함수에 @trace() 데코레이터 추가해줘
3. setting.yaml 파일 만들어줘
... (순서대로 진행)
```

### AI가 잘못된 프레임워크를 감지하면

명시적으로 알려주세요:
```
내 에이전트는 LangGraph를 사용해 (LangChain 아님).
LangGraph 통합 패턴을 사용해서 FluxLoop을 추가해줘.
```

### 파일 경로 문제

절대 경로를 제공하세요:
```
에이전트 코드는 /Users/myname/project/src/agent.py에 있어.
FluxLoop 설정은 /Users/myname/project/fluxloop/에 만들어줘.
```

---

## Files in This Documentation

- **`ai-assistant-integration-guide.md`** - 영어 완전 가이드 (모든 섹션, 예제, 코드 템플릿)
- **`ai-assistant-integration-guide-ko.md`** - 한국어 완전 가이드 (위와 동일한 내용)
- **`AI_ASSISTANT_README.md`** (이 파일) - 가이드 사용 방법 설명

---

## For AI Assistants Reading This

When a user provides this file or the integration guide:

1. **Read the full integration guide** (either EN or KO version)
2. **Follow the decision tree** to determine the user's starting point
3. **Execute the checklist** in Section 11 systematically
4. **Use the code templates** in Section 12 as starting points
5. **Verify success criteria** in Section 13 before completing

**Key Principles:**
- Ask clarifying questions if the agent structure is unclear
- Always test that code still runs after adding decorators
- Explain what each step does to the user
- Show concrete results (e.g., "Generated 100 inputs, 87 passed, 13 failed")
- Iterate based on failures

**Output Format:**
- Show code changes with clear before/after
- Provide command-line instructions ready to copy-paste
- Summarize findings in human-readable format
- Suggest specific improvements based on failures

---

## Quick Reference Card

### One-Line Request

영어:
```
@guides/ai-assistant-integration-guide.md Add FluxLoop to my agent and test with 100 inputs
```

한국어:
```
@guides/ai-assistant-integration-guide-ko.md 내 에이전트에 FluxLoop 추가하고 100개 입력으로 테스트
```

### What AI Will Create

1. Modified agent file with `@trace()` decorator
2. `fluxloop/` directory with config files
3. Generated inputs (100+ variations)
4. Experiment results with success/failure analysis
5. Actionable recommendations for improvement

### Total Time

- Integration: 2-5 minutes (AI does it)
- Input generation: 30 seconds - 2 minutes (depends on LLM)
- Experiment execution: 2-10 minutes (depends on agent complexity)
- Analysis: Immediate (AI summarizes)

**Total: 5-20 minutes from zero to full test results** 🚀

---

## Feedback & Updates

이 가이드를 사용한 경험을 공유해주세요:
- GitHub Issues: Report problems or suggest improvements
- Pull Requests: Contribute new patterns or examples
- Discord: Share success stories and use cases

**Version:** 1.0.0  
**Last Updated:** 2024-10-22  
**License:** Apache 2.0

---

**시작하세요! AI IDE를 열고 가이드를 제공한 후, 에이전트 테스트를 요청하세요.** ✨

