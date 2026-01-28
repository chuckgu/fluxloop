# FluxLoop 웹사이트 개편 방안

## 📋 현재 상황 분석

### 제품 구조 변경사항

#### Before (Old Architecture)
- **CLI**: 로컬 평가 도구 (evaluate, parse, record, doctor 등)
- **SDK**: Python instrumentation
- **VSCode Extension**: 로컬 개발 도구
- **MCP**: Model Context Protocol 지원

#### After (New Architecture)
- **FluxLoop Web**: 클라우드 기반 에이전트 시뮬레이션 & 테스팅 플랫폼
- **FluxLoop CLI**: 에이전트 first 도구 (Web 플랫폼 연동)
- **Claude Code Plugin**: FluxLoop 스킬/명령어 통합
- **SDK**: Python instrumentation (유지)

### 웹사이트 현재 문제점

#### 1. 삭제된 기능이 여전히 문서화됨
- ❌ VSCode Extension (언급만 있고 실제 문서 없음)
- ❌ Evaluation 명령어 (`evaluate.md`, `evaluation-config.md` - 1010줄의 상세 문서)
- ❌ Parse 명령어 (`parse.md`)
- ❌ Record 명령어 (`record.md`, `recording-mode.md`, `recording-workflow.md`)
- ❌ Doctor 명령어 (`doctor.md`)

#### 2. 새로운 기능이 문서화되지 않음
- ⭕ Claude Code Plugin (전혀 없음)
- ⭕ Web 플랫폼 연동 (projects, scenarios, apikeys, sync 등)
- ⭕ 에이전트 first 워크플로우

#### 3. 잘못된 제품 포지셔닝
- 현재: "로컬 AI 에이전트 시뮬레이션 및 평가 프레임워크"
- 실제: "클라우드 기반 에이전트 개발 플랫폼 + CLI 도구 + Claude Code 통합"

#### 4. 미완성 콘텐츠
- Blog: 여전히 Docusaurus 템플릿 상태
- 홈페이지: 오래된 메시지 ("Ship Agents with Data. Scale Business.")

---

## 🎯 개편 목표

### 1. 제품 포지셔닝 재정의
```
FluxLoop = Web 플랫폼 (핵심) + CLI (로컬 도구) + Claude Code (통합)
```

### 2. 대상 사용자
- **Primary**: Claude Code 사용자 (AI 에이전트 개발자)
- **Secondary**: Python 에이전트 개발자 (SDK 사용자)
- **Tertiary**: CI/CD 통합 사용자

### 3. 핵심 메시지
- "Build, Test, and Ship AI Agents with Confidence"
- "Claude Code에서 바로 시작하는 에이전트 테스팅"
- "합성 데이터로 에이전트를 규모있게 검증"

---

## 📐 새로운 사이트 구조

### 네비게이션 (상단바)

```
[FluxLoop Logo]  Docs  |  Web Platform  |  CLI  |  Claude Code  |  Blog  |  [GitHub]  [언어]
```

### 홈페이지 섹션

#### Hero Section
```
🚀 Build, Test, and Ship AI Agents with Confidence

Claude Code에서 바로 시작하는 AI 에이전트 테스팅 플랫폼
합성 데이터로 에이전트를 시뮬레이션하고, 실전에 배포하세요.

[Get Started with Claude Code]  [Explore Web Platform]  [Read Docs]

# 빠른 설치 (Claude Code)
claude code plugin install fluxloop
fluxloop setup
```

#### Feature Sections
```
1. 🎭 Synthetic Testing at Scale
   - 페르소나 기반 합성 입력 생성
   - 수백 개의 시나리오를 자동 실행
   - 실제 사용자처럼 에이전트와 상호작용

2. 🔗 Seamless Claude Code Integration
   - /fluxloop 명령어로 즉시 테스트
   - IDE에서 바로 결과 확인
   - 워크플로우 중단 없이 검증

3. 📊 Cloud-Powered Analysis
   - 웹 플랫폼에서 결과 시각화
   - 팀과 테스트 데이터 공유
   - 에이전트 성능 추적

4. 🐍 Python-First SDK
   - @agent, @trace 데코레이터로 간편 계측
   - LangChain, LangGraph 즉시 지원
   - pytest와 네이티브 통합
```

#### Product Showcase
```
Three Ways to Use FluxLoop:

[Claude Code Plugin]     [CLI Tool]              [Web Platform]
스킬로 즉시 실행          로컬 명령어 도구          클라우드 대시보드
/fluxloop test          fluxloop test           results.fluxloop.ai
```

---

## 📚 문서 구조 개편

### 1. 메인 문서 (docs/)

#### 새로운 구조
```yaml
# Welcome
- intro.md (재작성)

# Getting Started
- what-is-fluxloop.md (새로 작성)
- quickstart-claude-code.md (새로 작성)
- quickstart-cli.md (기존 quick-start.md 수정)
- core-concepts.md (수정)

# Workflows
- claude-code-workflow.md (새로 작성)
- local-testing-workflow.md (기존 end-to-end-workflow.md 수정)
- ci-cd-workflow.md (기존 cicd.md 이동)
- team-collaboration.md (새로 작성)

# Web Platform (새 섹션)
- platform-overview.md (새로 작성)
- projects-and-scenarios.md (새로 작성)
- viewing-results.md (새로 작성)
- api-keys.md (새로 작성)

# Guides
- synthetic-input-generation.md (새로 작성)
- persona-design.md (새로 작성)
- interpreting-results.md (새로 작성)

# Advanced
- custom-storage.md (유지)
- pytest-integration.md (이동)
- environment-setup.md (기존 virtual-environment-setup.md 수정)

# Reference
- configuration.md (대폭 수정)
- json-contract.md (유지)
- artifacts.md (유지)
```

#### 삭제할 파일
```
- docs/advanced/argument-replay.md (삭제)
- docs/advanced/recording-mode.md (삭제)
- docs/guides/ai-assistant-integration-guide.md (삭제)
- docs/guides/ai-assistant-integration-guide-ko.md (삭제)
- docs/deployment/* (4개 파일 - 통합)
```

---

### 2. CLI 문서 (docs-cli/)

#### 새로운 구조
```yaml
# CLI Overview
- intro.md (재작성)

# Getting Started
- installation.md (유지)
- authentication.md (새로 작성)
- first-test.md (기존 first-experiment.md 수정)

# Core Commands (재구성)
## Project Management
- init.md (수정)
- status.md (수정)
- config.md (수정)

## Authentication & Sync
- auth.md (새로 작성)
- projects.md (새로 작성)
- scenarios.md (새로 작성)
- apikeys.md (새로 작성)

## Testing Workflow
- generate.md (수정)
- test.md (기존 run.md 수정)
- criteria.md (새로 작성)
- sync.md (새로 작성)

## Input Generation
- personas.md (새로 작성)
- inputs.md (새로 작성)
- bundles.md (새로 작성)
- context.md (새로 작성)

# Configuration
- project-config.md (수정)
- input-config.md (수정)
- runner-targets.md (수정)
- runners/
  - python-function.md (유지)
  - http-sse.md (유지)
  - subprocess-jsonl.md (유지)

# Workflows
- basic-workflow.md (재작성)
- multi-turn-workflow.md (수정)
- pytest-integration.md (유지)
- ci-cd-integration.md (수정)

# Reference
- command-reference.md (새로 작성 - 전체 명령어 표)
- exit-codes.md (새로 작성)
```

#### 삭제할 파일
```
- docs-cli/commands/evaluate.md (삭제)
- docs-cli/commands/parse.md (삭제)
- docs-cli/commands/record.md (삭제)
- docs-cli/commands/doctor.md (삭제)
- docs-cli/configuration/evaluation-config.md (삭제 - 1010줄)
- docs-cli/configuration/simulation-config.md (삭제 또는 대폭 축소)
- docs-cli/workflows/recording-workflow.md (삭제)
```

---

### 3. Claude Code 문서 (docs-claude-code/) - 신규 생성

#### 구조
```yaml
# Claude Code Plugin Overview
- intro.md

# Getting Started
- installation.md
- setup.md
- first-test.md

# Skills Reference
- fluxloop-setup.md (/setup 스킬)
- fluxloop-test.md (/test 스킬)
- fluxloop-status.md (/status 스킬)
- fluxloop-criteria.md (/criteria 스킬)
- other-skills.md (기타 스킬들)

# Integration
- claude-code-workflow.md
- best-practices.md
- troubleshooting.md

# Advanced
- custom-skills.md
- hooks.md
- mcp-servers.md (선택사항)
```

---

### 4. SDK 문서 (docs-sdk/) - 유지

#### 수정 필요 항목
- **intro.md**: 버전 업데이트
- **storage-backends.md**: Web 플랫폼 연동 추가
- **runner-integration.md**: CLI 연동 섹션 추가

---

## 🗂️ Sidebar 재구성

### sidebars.ts (메인 문서)

```typescript
export default {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/what-is-fluxloop',
        'getting-started/quickstart-claude-code',
        'getting-started/quickstart-cli',
        'getting-started/core-concepts',
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/claude-code-workflow',
        'workflows/local-testing-workflow',
        'workflows/ci-cd-workflow',
        'workflows/team-collaboration',
      ],
    },
    {
      type: 'category',
      label: 'Web Platform',
      items: [
        'platform/platform-overview',
        'platform/projects-and-scenarios',
        'platform/viewing-results',
        'platform/api-keys',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/synthetic-input-generation',
        'guides/persona-design',
        'guides/interpreting-results',
      ],
    },
    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/custom-storage',
        'advanced/pytest-integration',
        'advanced/environment-setup',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/configuration',
        'reference/json-contract',
        'reference/artifacts',
      ],
    },
  ],
};
```

### sidebars-cli.ts

```typescript
export default {
  cliSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/authentication',
        'getting-started/first-test',
      ],
    },
    {
      type: 'category',
      label: 'Core Commands',
      collapsed: false,
      items: [
        {
          type: 'category',
          label: 'Project Management',
          items: [
            'commands/init',
            'commands/status',
            'commands/config',
          ],
        },
        {
          type: 'category',
          label: 'Authentication & Sync',
          items: [
            'commands/auth',
            'commands/projects',
            'commands/scenarios',
            'commands/apikeys',
          ],
        },
        {
          type: 'category',
          label: 'Testing Workflow',
          items: [
            'commands/generate',
            'commands/test',
            'commands/criteria',
            'commands/sync',
          ],
        },
        {
          type: 'category',
          label: 'Input Generation',
          items: [
            'commands/personas',
            'commands/inputs',
            'commands/bundles',
            'commands/context',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/project-config',
        'configuration/input-config',
        'configuration/runner-targets',
        {
          type: 'category',
          label: 'Runner Types',
          items: [
            'configuration/runners/python-function',
            'configuration/runners/http-sse',
            'configuration/runners/subprocess-jsonl',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/basic-workflow',
        'workflows/multi-turn-workflow',
        'workflows/pytest-integration',
        'workflows/ci-cd-integration',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/command-reference',
        'reference/exit-codes',
      ],
    },
  ],
};
```

### sidebars-claude-code.ts (신규)

```typescript
export default {
  claudeCodeSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/setup',
        'getting-started/first-test',
      ],
    },
    {
      type: 'category',
      label: 'Skills Reference',
      items: [
        'skills/fluxloop-setup',
        'skills/fluxloop-test',
        'skills/fluxloop-status',
        'skills/fluxloop-criteria',
        'skills/other-skills',
      ],
    },
    {
      type: 'category',
      label: 'Integration',
      items: [
        'integration/claude-code-workflow',
        'integration/best-practices',
        'integration/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/custom-skills',
        'advanced/hooks',
      ],
    },
  ],
};
```

---

## 🎨 docusaurus.config.ts 수정

### 네비게이션 바 업데이트

```typescript
navbar: {
  title: 'FluxLoop',
  logo: {
    alt: 'FluxLoop Logo',
    src: 'img/logo.svg',
  },
  items: [
    // 문서 드롭다운
    {
      type: 'dropdown',
      label: 'Docs',
      position: 'left',
      items: [
        {
          label: 'Overview',
          to: '/docs/intro',
        },
        {
          label: 'Web Platform',
          to: '/docs/platform/platform-overview',
        },
        {
          type: 'html',
          value: '<hr style="margin: 0.3rem 0;">',
        },
        {
          label: 'Claude Code Plugin',
          to: '/claude-code/intro',
        },
        {
          label: 'CLI Reference',
          to: '/cli/intro',
        },
        {
          label: 'Python SDK',
          to: '/sdk/intro',
        },
      ],
    },

    // 빠른 링크
    {
      type: 'doc',
      docId: 'getting-started/quickstart-claude-code',
      position: 'left',
      label: 'Quick Start',
    },

    // Blog
    {
      to: '/blog',
      label: 'Blog',
      position: 'left'
    },

    // 외부 링크
    {
      href: 'https://app.fluxloop.ai',
      label: 'Web App',
      position: 'right',
    },
    {
      href: 'https://github.com/chuckgu/fluxloop',
      label: 'GitHub',
      position: 'right',
    },

    // 언어 선택
    {
      type: 'localeDropdown',
      position: 'right',
    },
  ],
}
```

### 플러그인 추가 (Claude Code 문서)

```typescript
plugins: [
  // 기존 플러그인...

  // Claude Code 플러그인
  [
    '@docusaurus/plugin-content-docs',
    {
      id: 'claude-code',
      path: 'docs-claude-code',
      routeBasePath: 'claude-code',
      sidebarPath: './sidebars-claude-code.ts',
      editUrl: 'https://github.com/chuckgu/fluxloop/tree/main/packages/website/',
    },
  ],
],
```

### Footer 업데이트

```typescript
footer: {
  style: 'dark',
  links: [
    {
      title: 'Product',
      items: [
        {
          label: 'Web Platform',
          href: 'https://app.fluxloop.ai',
        },
        {
          label: 'Claude Code Plugin',
          to: '/claude-code/intro',
        },
        {
          label: 'CLI Tool',
          to: '/cli/intro',
        },
        {
          label: 'Python SDK',
          to: '/sdk/intro',
        },
      ],
    },
    {
      title: 'Docs',
      items: [
        {
          label: 'Getting Started',
          to: '/docs/getting-started/quickstart-claude-code',
        },
        {
          label: 'Workflows',
          to: '/docs/workflows/claude-code-workflow',
        },
        {
          label: 'API Reference',
          to: '/sdk/api/decorators',
        },
      ],
    },
    {
      title: 'Community',
      items: [
        {
          label: 'GitHub',
          href: 'https://github.com/chuckgu/fluxloop',
        },
        {
          label: 'Discord',
          href: 'https://discord.gg/fluxloop', // 실제 링크로 교체
        },
        {
          label: 'Twitter',
          href: 'https://twitter.com/fluxloop_ai', // 실제 링크로 교체
        },
      ],
    },
    {
      title: 'More',
      items: [
        {
          label: 'Blog',
          to: '/blog',
        },
        {
          label: 'Changelog',
          to: '/changelog',
        },
      ],
    },
  ],
  copyright: `Copyright © ${new Date().getFullYear()} FluxLoop. Built with Docusaurus.`,
},
```

---

## ✍️ 새로 작성해야 할 주요 문서

### 우선순위 1 (즉시 작성)

1. **docs/intro.md** (재작성)
   - 제품 전체 개요
   - "에이전트 개발 플랫폼" 포지셔닝
   - 3가지 제품 소개 (Web, CLI, Claude Code)

2. **docs/getting-started/what-is-fluxloop.md**
   - FluxLoop가 해결하는 문제
   - 주요 기능
   - 사용 사례

3. **docs/getting-started/quickstart-claude-code.md**
   - Claude Code 플러그인 설치
   - 첫 테스트 실행
   - 결과 확인

4. **docs-claude-code/** (전체 신규)
   - 플러그인 문서 전체

5. **docs/platform/** (전체 신규)
   - 웹 플랫폼 사용 가이드

### 우선순위 2 (단기 작성)

6. **docs-cli/commands/** (신규 명령어)
   - auth.md, projects.md, scenarios.md
   - apikeys.md, personas.md, inputs.md, bundles.md
   - criteria.md, sync.md

7. **docs/workflows/claude-code-workflow.md**
   - Claude Code에서 FluxLoop 사용하는 전체 워크플로우

### 우선순위 3 (중기 작성)

8. **docs/guides/synthetic-input-generation.md**
   - 합성 입력 생성 철학
   - 페르소나 디자인 패턴

9. **Blog Posts**
    - "Introducing FluxLoop 2.0: Agent-First Testing Platform"
    - "From Local Evaluation to Cloud-Powered Testing"
    - "Testing AI Agents at Scale with Synthetic Data"

---

## 🗑️ 삭제 체크리스트

### 문서 파일 삭제

```bash
# 메인 문서
rm docs/advanced/argument-replay.md
rm docs/advanced/recording-mode.md
rm docs/guides/ai-assistant-integration-guide.md
rm docs/guides/ai-assistant-integration-guide-ko.md

# CLI 문서
rm docs-cli/commands/evaluate.md
rm docs-cli/commands/parse.md
rm docs-cli/commands/record.md
rm docs-cli/commands/doctor.md
rm docs-cli/configuration/evaluation-config.md
rm docs-cli/configuration/simulation-config.md  # 또는 대폭 축소
rm docs-cli/workflows/recording-workflow.md
```

### 코드에서 언급 제거

```bash
# VSCode 확장 언급 제거
grep -r "vscode" docs/ docs-cli/ docs-sdk/
grep -r "VSCode" docs/ docs-cli/ docs-sdk/
grep -r "Visual Studio Code" docs/ docs-cli/ docs-sdk/

# Evaluation 언급 제거
grep -r "evaluate" docs/ docs-cli/ docs-sdk/
grep -r "evaluation" docs/ docs-cli/ docs-sdk/

# Recording 언급 제거
grep -r "record" docs/ docs-cli/ docs-sdk/
grep -r "recording" docs/ docs-cli/ docs-sdk/
```

---

## 📅 실행 계획

### Phase 1: 정리 (Week 1)
- [ ] 삭제된 기능 문서 제거
- [ ] VSCode/MCP 언급 제거
- [ ] Sidebar 업데이트 (삭제된 항목 제거)
- [ ] docusaurus.config.ts 기본 수정

### Phase 2: 핵심 문서 작성 (Week 2-3)
- [ ] 새로운 intro.md 작성
- [ ] Claude Code 문서 작성 (docs-claude-code/)
- [ ] Web Platform 문서 작성 (docs/platform/)
- [ ] 새로운 CLI 명령어 문서 작성

### Phase 3: 홈페이지 개편 (Week 3)
- [ ] Hero 섹션 재작성
- [ ] Feature 섹션 재작성
- [ ] Product showcase 추가
- [ ] CTA 버튼 업데이트

### Phase 4: 추가 콘텐츠 (Week 4)
- [ ] Migration 가이드 작성
- [ ] Workflow 문서 작성
- [ ] Guide 문서 작성
- [ ] Blog 포스트 초안

### Phase 5: 검토 및 배포 (Week 5)
- [ ] 링크 검증
- [ ] 이미지/스크린샷 추가
- [ ] SEO 최적화
- [ ] Staging 배포 및 테스트
- [ ] Production 배포

---

## 🎯 성공 지표

1. **명확한 제품 포지셔닝**
   - 홈페이지 방문자가 5초 안에 FluxLoop가 무엇인지 이해
   - Claude Code 통합이 첫 번째 CTA

2. **완전한 문서**
   - 모든 CLI 명령어 문서화
   - Claude Code 플러그인 완전 가이드
   - Web 플랫폼 사용법 명확

3. **사용자 여정 최적화**
   - Quick Start → First Test → View Results: 10분 이내
   - 문서 검색으로 모든 질문 해결 가능

4. **기술 품질**
   - 깨진 링크 0개
   - 빌드 경고 0개
   - Lighthouse 점수 90+

---

## 📝 추가 고려사항

### 1. 한국어 번역
현재 일부 문서만 한국어 버전이 있습니다. 다음 우선순위로 번역:
1. Quick Start 가이드
2. Claude Code 플러그인 문서
3. CLI 주요 명령어 문서
4. Web Platform 가이드

### 2. 비디오 콘텐츠
- Quick Start 비디오 (3-5분)
- Claude Code 통합 데모
- Web Platform 투어

### 3. 인터랙티브 요소
- 홈페이지에 라이브 데모
- Interactive API playground
- CLI 명령어 빌더

### 4. SEO 최적화
- Meta 태그 업데이트
- Open Graph 이미지
- Sitemap 생성
- robots.txt 최적화

---

## 🤝 기여 가이드

문서 개편에 참여하는 방법:
1. 이 계획서를 GitHub Issue로 전환
2. 각 Phase를 별도 Milestone으로 관리
3. 문서별로 Issue 생성 및 할당
4. PR 템플릿 사용 (체크리스트 포함)

---

**다음 단계**: Phase 1 실행 - 삭제된 기능 문서 제거 및 정리
