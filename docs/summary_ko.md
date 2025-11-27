**FluxLoop: AI 에이전트를 100개 이상의 입력 변형으로 자동 테스트 (오픈소스)**

**요약:** LLM으로 100개 이상의 현실적인 입력 변형을 생성하고, 현실적인 프로덕션 컨텍스트에서 에이전트에 대해 재생하여, 정확히 어떤 시나리오가 성공/실패하는지 보여주는 구조화된 결과를 얻습니다.

---

**핵심 문제**

AI 에이전트를 만들었습니다. 다음으로 테스트합니다:

- ✅ "안녕하세요, 주문 관련 도움이 필요합니다"
- ✅ "계좌 잔액 확인해주세요"

잘 동작합니다! 배포합니다. 그런데 사용자들이 이렇게 입력합니다:

- ❌ "ㅇㅇ 그거 안되는데 ㅋㅋ"
- ❌ "안녕하세요........... 도와주세요........... 급해요..........."
- ❌ "Hello! Can you help me?" (예상치 못한 언어)
- ❌ "주문번호 #12345 안왔음!!!!" (대문자, 맥락 없음)
- ❌ 10가지 다른 요청이 담긴 500단어 장황한 메시지

**이런 케이스를 테스트하지 않은 이유:**

1. 100개의 테스트 케이스를 수동으로 작성하는 것은 지루함
2. 어떤 엣지 케이스가 존재하는지 모름
3. 실행하려면 프로덕션과 유사한 컨텍스트가 필요함 (콜백, 세션 데이터 등)

---

**FluxLoop의 솔루션: 자동 입력 변형 + 컨텍스트 재생**

### 워크플로우

```python
# 1. 스테이징에서 실제 호출 하나를 녹화 (모든 컨텍스트 포함)
@fluxloop.agent()
async def handle_message(connection_id, data, user_session, callbacks):
    result = await your_agent_logic(data)
    return result

fluxloop.record_call_args(target="app:handle_message", **all_kwargs)
# 캡처: connection_id, 세션 데이터, 콜백, 모든 것

```

```bash
# 2. 자동으로 100개의 입력 변형 생성
fluxloop generate inputs \\
  --config setting.yaml \\
  --from-recording recordings/args.jsonl \\
  --limit 100

# 이렇게 변형을 생성:
# - 공손함: "안녕하세요, 주문 추적 도움이 필요합니다."
# - 캐주얼: "ㅇㅇ 택배 어디있는지 확인 좀"
# - 화남: "이게 세 번째인데!!!"
# - 다국어: 언어 혼합
# - 엣지 케이스: 빈 문자열, 매우 긴 텍스트, 특수 문자 등

```

```yaml
# 3. 무엇을 변형할지 설정
# setting.yaml
input_generation:
  provider: "openai"
  model: "gpt-4o-mini"
  prompt: |
    다양한 고객 지원 문의를 생성하세요:
    - 톤 (공손함, 화남, 혼란스러움)
    - 길이 (짧음, 장황함)
    - 언어 (한글, 영어, 혼합)
    - 엣지 케이스 (오타, 대문자, 이모지)

```

```bash
# 4. 모든 변형으로 시뮬레이션 실행
fluxloop run experiment --config setting.yaml

# FluxLoop:
# - 녹화된 프로덕션 컨텍스트를 로드 (세션, 콜백 등)
# - 100번 재생, 각각 다른 입력으로
# - 에이전트가 실제 코드, 실제 LLM 호출로 실행
# - 구조화된 산출물 생성

```

**결과:**

```
experiments/exp_20241005/
├── summary.json          # 100회 실행: 85 성공, 15 실패
├── trace_summary.jsonl   # 입력별 결과
├── observations.jsonl    # 모든 LLM 호출, 모든 단계
└── per_trace_analysis/   # 사람이 읽을 수 있는 분석
    ├── 00_polite_inquiry.md        ✅ 성공
    ├── 01_all_caps_angry.md        ❌ 실패 (왜?)
    ├── 02_multilingual.md          ✅ 성공
    └── ...

```

---

**왜 중요한가**

### FluxLoop 이전:

```python
# 수동 테스팅
test_input_1 = "안녕하세요, 도와주세요"
test_input_2 = "지원이 필요합니다"
test_input_3 = "도와주실 수 있나요?"
# ... 100개를 이렇게 작성할 건가요? 아니죠.

```

### FluxLoop 사용:

```bash
# 자동 생성
fluxloop generate inputs --limit 100
# → 30초 만에 100개의 다양하고 현실적인 변형

```

### 실제 가치:

✅ **생각지도 못한 엣지 케이스 발견**

✅ **정확히 어떤 입력 패턴이 에이전트를 망가뜨리는지 확인**

✅ **실제 프로덕션 컨텍스트로 재생** (수동 모킹 불필요)

✅ **디버깅을 위한 재현 가능한 결과**

✅ **빠른 반복**: 프롬프트 변경 → 100개 변형 재생성 → 재실행

---

**실제 예시: 고객 지원 봇**

**녹화된 컨텍스트 (한 번):**

- `user_session`: {"user_id": "123", "tier": "premium", "history": [...]}
- `send_callback`: 실제 WebSocket 전송자
- `db_connection`: 실제 데이터베이스 연결

**생성된 입력 (100개 변형):**

1. "안녕하세요, 주문 #5432가 아직 도착하지 않았습니다"
2. "야 내 물건 어디있음"
3. "Hello, I need help with my order"
4. "........................안녕하세요"
5. [빈 문자열]
6. "지난주에 뭔가 주문했는데 어제 도착했어야 할 것 같은데 확실하지 않고 또 계정에 대한 다른 질문도 있고..."
... 94개 더

**시뮬레이션 결과:**

- ✅ 78개 올바르게 처리
- ⚠️ 15개 상담원으로 폴백 필요 (허용 가능)
- ❌ 7개 크래시 또는 잘못된 답변 (수정 필요!)

**7개 실패가 보여주는 것:**

- 에이전트가 빈 입력을 처리 못함 → 검증 추가
- 다국어 미지원 → 감지 추가
- 매우 긴 입력이 중요 정보 잘라냄 → 프롬프트 윈도우 수정

**FluxLoop 없이는 프로덕션 전에 이걸 절대 발견하지 못했을 것입니다.**

---

**주요 기능**

### 🎯 LLM 기반 입력 생성

- 평범한 한글로 생성 전략 정의
- 자동 변형: 톤, 길이, 언어, 엣지 케이스
- 자체 프롬프트 또는 내장 템플릿 사용

### 🔄 컨텍스트 재생 (수동 모킹 불필요)

- 모든 인자와 함께 실제 함수 호출 녹화
- 다른 입력, 동일한 컨텍스트로 재생
- 콜백, WebSocket 핸들러, 데이터베이스 연결과 동작

### 🧪 오프라인 우선 시뮬레이션

- 모든 것이 로컬에서 실행
- 시뮬레이션 중 클라우드 의존성 없음
- 데이터가 절대 외부로 나가지 않음

### 📊 구조화된 산출물

- 프로그래밍 방식 분석을 위한 JSON/JSONL 출력
- 사람이 읽을 수 있는 Markdown 타임라인
- 모든 평가 백엔드와 호환

### 🚀 프레임워크 무관

- LangChain, LangGraph, AutoGPT, 커스텀 에이전트와 동작
- `@fluxloop.agent()` 데코레이터만 추가
- Python 3.9+

---

**시작하기 (5분)**

```bash
pip install fluxloop-cli fluxloop

# 프로젝트 초기화
fluxloop init project --name my-agent
cd fluxloop/my-agent

# 입력 생성을 위한 LLM 설정
export OPENAI_API_KEY=sk-...

# 50개 입력 변형 생성
fluxloop generate inputs --config setting.yaml --limit 50

# 시뮬레이션 실행
fluxloop run experiment --config setting.yaml

# 결과를 사람이 읽을 수 있는 형식으로 파싱
fluxloop parse experiment experiments/<latest>/

```

⭐ GitHub: [[링크]](https://github.com/chuckgu/fluxloop)

---

**왜 오픈소스인가?**

AI 에이전트 테스팅은 보편적인 문제입니다. 우리에게 필요한 것:

- **커뮤니티 주도 입력 생성 전략**
- **표준 평가 계약**
- **프레임워크 통합**
- **새로운 평가 방법론**

**이런 컨트리뷰터를 찾습니다:**

- 🔧 특정 도메인을 위한 입력 생성기 구축 (의료, 법률, 금융)
- 🧪 평가 메트릭 및 점수 시스템 개발
- 📝 인기 프레임워크를 위한 통합 가이드 작성
- 🎨 CLI/VSCode 익스텐션 UX 개선

**초기 컨트리뷰터가 표준을 정의합니다.** 이것은 AI 신뢰성을 위한 기초 인프라입니다.

---

**FAQ**

*Q: 입력 생성이 유닛 테스트와 어떻게 다른가요?*

A: 유닛 테스트는 수동으로 작성한 고정 입력을 사용합니다. FluxLoop는 LLM을 사용하여 자동으로 다양하고 현실적인 변형을 생성합니다.

*Q: 자체 입력 생성 로직을 사용할 수 있나요?*

A: 네! 자체 생성기를 가져오거나 FluxLoop의 LLM 기반 생성기를 사용하세요.

*Q: LangSmith/Helicone을 대체하나요?*

A: 아니요. 그것들은 프로덕션을 모니터링합니다. FluxLoop는 프로덕션 이전을 시뮬레이션합니다. 둘 다 사용하세요.

---

**라이선스:** Apache 2.0

**에이전트를 제대로 테스트하세요.** 🚀