# FluxLoop Documentation

FluxLoop SDK와 CLI를 위한 완전한 문서 모음입니다.

## 📚 Documentation Structure

```
docs/
├── README.md (이 파일)
├── AI_ASSISTANT_README.md          # AI IDE 사용자를 위한 빠른 시작
├── summary_en.md                   # 프로젝트 개요 (영어)
├── summary_ko.md                   # 프로젝트 개요 (한국어)
└── guides/
    ├── ai-assistant-integration-guide.md     # AI IDE용 완전 통합 가이드 (영어)
    ├── ai-assistant-integration-guide-ko.md  # AI IDE용 완전 통합 가이드 (한국어)
    ├── end-to-end-workflow.md               # 워크플로우 가이드
    └── virtual-environment-setup.md         # 개발 환경 설정
```

---

## 🎯 어떤 문서를 읽어야 할까요?

### 신규 사용자 (처음 사용하는 경우)

**AI IDE 사용자 (Cursor, Claude Code 등):**
- 👉 **시작:** [`AI_ASSISTANT_README.md`](./AI_ASSISTANT_README.md)
- 👉 **AI에게 제공:** [`guides/ai-assistant-integration-guide.md`](./guides/ai-assistant-integration-guide.md) (영어)
- 👉 **AI에게 제공:** [`guides/ai-assistant-integration-guide-ko.md`](./guides/ai-assistant-integration-guide-ko.md) (한국어)

**일반 사용자 (수동 통합):**
- 👉 **개요 이해:** [`summary_en.md`](./summary_en.md) 또는 [`summary_ko.md`](./summary_ko.md)
- 👉 **단계별 가이드:** [`guides/end-to-end-workflow.md`](./guides/end-to-end-workflow.md)

### 기존 사용자 (이미 사용 중인 경우)

- 📖 **전체 워크플로우:** [`guides/end-to-end-workflow.md`](./guides/end-to-end-workflow.md)
- 🔧 **개발 환경 설정:** [`guides/virtual-environment-setup.md`](./guides/virtual-environment-setup.md)

### 컨트리뷰터 & 개발자

- 📝 **프로젝트 이해:** [`summary_en.md`](./summary_en.md)
- 🤝 **기여하기:** [`../CONTRIBUTING.md`](../CONTRIBUTING.md)

---

## 📖 문서별 설명

### 🚀 AI Assistant Integration Guide (권장!)

**파일:**
- [`guides/ai-assistant-integration-guide.md`](./guides/ai-assistant-integration-guide.md) (영어)
- [`guides/ai-assistant-integration-guide-ko.md`](./guides/ai-assistant-integration-guide-ko.md) (한국어)

**대상:** AI IDE 사용자 (Cursor, Claude Code, GitHub Copilot 등)

**내용:**
- AI 어시스턴트가 자동으로 FluxLoop을 통합할 수 있도록 작성된 완전한 가이드
- 설치부터 테스트, 분석까지 전체 프로세스 포함
- LangChain, LangGraph, 커스텀 에이전트 등 모든 패턴 지원
- 13개 섹션, 100+ 코드 예제
- 문제 해결 가이드 포함

**사용 방법:**
```
# AI IDE 채팅에서
@guides/ai-assistant-integration-guide-ko.md 

내 에이전트에 FluxLoop을 추가하고 100개 입력으로 테스트해줘.
```

**이 문서를 선택하세요:**
- ✅ AI IDE를 사용 중이고 자동화를 원하는 경우
- ✅ 빠르게 시작하고 싶은 경우
- ✅ 모든 패턴과 예제를 한 곳에서 보고 싶은 경우

---

### 📋 Summary (프로젝트 개요)

**파일:**
- [`summary_en.md`](./summary_en.md) (영어)
- [`summary_ko.md`](./summary_ko.md) (한국어)

**대상:** 모든 사용자

**내용:**
- FluxLoop이 무엇인지, 왜 필요한지
- 핵심 문제와 솔루션
- 주요 기능 소개
- 5분 빠른 시작 가이드
- FAQ

**이 문서를 읽으세요:**
- ✅ FluxLoop이 무엇인지 이해하고 싶을 때
- ✅ 다른 도구와의 차이를 알고 싶을 때
- ✅ 프로젝트를 다른 사람에게 소개할 때

---

### 🔄 End-to-End Workflow

**파일:** [`guides/end-to-end-workflow.md`](./guides/end-to-end-workflow.md)

**대상:** 수동으로 통합하려는 사용자

**내용:**
- 프로젝트 초기화
- 인자 녹화
- 입력 생성
- 실험 실행
- 결과 파싱

**이 문서를 읽으세요:**
- ✅ 각 단계를 직접 수행하고 싶을 때
- ✅ CLI 명령어를 자세히 알고 싶을 때
- ✅ 워크플로우 전체를 이해하고 싶을 때

---

### 🛠️ Virtual Environment Setup

**파일:** [`guides/virtual-environment-setup.md`](./guides/virtual-environment-setup.md)

**대상:** 개발 환경 설정이 필요한 사용자

**내용:**
- Python 가상환경 설정
- 의존성 관리
- 개발 환경 구성

**이 문서를 읽으세요:**
- ✅ Python 환경 설정이 필요할 때
- ✅ 개발 환경을 구성하고 싶을 때

---

### 🤖 AI Assistant README

**파일:** [`AI_ASSISTANT_README.md`](./AI_ASSISTANT_README.md)

**대상:** AI IDE 사용자를 위한 빠른 참조

**내용:**
- AI 통합 가이드 사용 방법
- 예제 대화
- 기대 결과
- 문제 해결

**이 문서를 읽으세요:**
- ✅ AI IDE로 FluxLoop을 사용하고 싶을 때
- ✅ 빠른 예제가 필요할 때

---

## 🎓 Learning Path

### 경로 1: AI 자동화 (가장 빠름, 권장!)

```
1. AI_ASSISTANT_README.md 읽기 (2분)
   ↓
2. AI에게 ai-assistant-integration-guide-ko.md 제공
   ↓
3. "내 에이전트에 FluxLoop 추가해줘" 요청
   ↓
4. AI가 모든 것을 자동 설정 (5-10분)
   ↓
5. 결과 확인 및 개선 반복
```

**총 소요 시간:** 15-20분

---

### 경로 2: 수동 통합 (완전한 이해)

```
1. summary_ko.md 읽기 - 프로젝트 이해 (5분)
   ↓
2. end-to-end-workflow.md 읽기 - 워크플로우 학습 (10분)
   ↓
3. 직접 설치 및 통합 (20-30분)
   ↓
4. 입력 생성 및 실험 실행 (10분)
   ↓
5. 결과 분석 및 개선 (시간 가변)
```

**총 소요 시간:** 45-60분

---

### 경로 3: 빠른 시작 (최소한의 이해)

```
1. summary_ko.md의 "시작하기" 섹션만 읽기 (2분)
   ↓
2. 명령어 복사해서 실행
   ```bash
   pip install fluxloop-cli fluxloop
   fluxloop init project --name my-agent
   cd fluxloop/my-agent
   fluxloop generate inputs --config setting.yaml --limit 50
   fluxloop run experiment --config setting.yaml
   ```
   ↓
3. 결과 확인
```

**총 소요 시간:** 10-15분

---

## 💡 Use Cases by Role

### AI Agent 개발자
- **목표:** 에이전트가 다양한 입력에 잘 동작하는지 확인
- **추천 문서:**
  1. [`AI_ASSISTANT_README.md`](./AI_ASSISTANT_README.md)
  2. [`guides/ai-assistant-integration-guide-ko.md`](./guides/ai-assistant-integration-guide-ko.md)
- **예상 시간:** 15-20분

### QA/테스터
- **목표:** 체계적인 테스트 자동화
- **추천 문서:**
  1. [`summary_ko.md`](./summary_ko.md)
  2. [`guides/end-to-end-workflow.md`](./guides/end-to-end-workflow.md)
- **예상 시간:** 30분

### DevOps/SRE
- **목표:** CI/CD 파이프라인에 통합
- **추천 문서:**
  1. [`guides/end-to-end-workflow.md`](./guides/end-to-end-workflow.md)
  2. [`guides/virtual-environment-setup.md`](./guides/virtual-environment-setup.md)
- **예상 시간:** 45분

### 프로덕트 매니저/비개발자
- **목표:** FluxLoop이 무엇인지 이해
- **추천 문서:**
  1. [`summary_ko.md`](./summary_ko.md) 만 읽기
- **예상 시간:** 5분

---

## 🌟 Quick Start Commands

### 설치
```bash
pip install fluxloop-cli fluxloop
```

### 프로젝트 초기화
```bash
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

### 입력 생성
```bash
fluxloop generate inputs --config setting.yaml --limit 100
```

### 실험 실행
```bash
fluxloop run experiment --config setting.yaml
```

### 결과 파싱
```bash
fluxloop parse experiment experiments/<experiment_dir> --output per_trace_analysis
```

---

## 🤝 Contributing to Documentation

문서 개선에 기여하고 싶으신가요?

### 새 가이드 추가
1. `guides/` 디렉토리에 새 `.md` 파일 생성
2. 이 README의 "Documentation Structure"에 추가
3. Pull Request 제출

### 기존 문서 개선
1. 오타, 불명확한 설명, 누락된 내용 발견 시
2. 직접 수정하거나 Issue 생성
3. Pull Request 제출

### 번역 추가
현재 영어(EN)와 한국어(KO)를 지원합니다.
다른 언어로 번역하고 싶으신가요?
1. 기존 문서를 복사 (예: `summary_en.md` → `summary_ja.md`)
2. 번역
3. README에 링크 추가
4. Pull Request 제출

---

## 📞 Support & Community

### 문제가 있나요?
- 🐛 **버그 리포트:** [GitHub Issues](https://github.com/fluxloop/fluxloop/issues)
- 💬 **질문/토론:** [GitHub Discussions](https://github.com/fluxloop/fluxloop/discussions)
- 📧 **이메일:** team@fluxloop.dev

### 문서에서 답을 찾을 수 없나요?
1. 먼저 [`AI_ASSISTANT_README.md`](./AI_ASSISTANT_README.md)의 Troubleshooting 섹션 확인
2. [`guides/ai-assistant-integration-guide-ko.md`](./guides/ai-assistant-integration-guide-ko.md)의 Section 10 (문제 해결) 참조
3. 그래도 해결 안 되면 GitHub Issue 생성

---

## 📄 License

이 문서들은 FluxLoop 프로젝트의 일부이며 Apache 2.0 라이선스를 따릅니다.

---

## 🚀 Ready to Start?

### Option 1: AI 자동화 (가장 빠름!) ✨
```
AI IDE를 열고:
@guides/ai-assistant-integration-guide-ko.md 

내 에이전트에 FluxLoop을 추가하고 테스트해줘.
```

### Option 2: 직접 시작
```bash
# 1. 설치
pip install fluxloop-cli fluxloop

# 2. 프로젝트 생성
fluxloop init project --name my-agent

# 3. 가이드 읽기
cat guides/end-to-end-workflow.md

# 4. 실행!
```

**Happy Testing!** 🎉

---

**Last Updated:** 2024-10-22  
**Version:** 1.0.0  
**Maintainer:** FluxLoop Team

