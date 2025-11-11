---
sidebar_position: 1
---

# Installation

FluxLoop VSCode Extension 설치 방법을 안내합니다.

## 설치 방법

FluxLoop Extension은 **Extension Marketplace에서 직접 설치**할 수 있습니다!

### 🎯 방법 1: Extension Marketplace에서 설치 (권장)

#### Cursor 사용자

1. **Extensions 탭 열기** (왼쪽 사이드바 또는 `Cmd+Shift+X`)
2. **"FluxLoop" 검색**
3. **Install 클릭**
4. **Cursor 재시작**

> ✨ Cursor는 [Open VSX Registry](https://open-vsx.org/extension/fluxloop/fluxloop)에서 자동으로 Extension을 다운로드합니다.

#### VS Code 사용자

1. **Extensions 탭 열기** (`Cmd+Shift+X` / `Ctrl+Shift+X`)
2. **"FluxLoop" 검색**
3. **Install 클릭**
4. **VS Code 재시작**

> 또는 [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop)에서 직접 설치

**또는 명령 팔레트에서:**
```
ext install fluxloop.fluxloop
```

#### 설치 확인

재시작 후:
- 왼쪽 Activity Bar에 **FluxLoop 아이콘** 표시
- 아이콘 클릭 시 Projects, Inputs, Experiments, Results, Status 패널 표시

### 📦 방법 2: VSIX 파일로 수동 설치 (대체 방법)

Marketplace를 사용할 수 없는 경우:

#### 1. VSIX 파일 다운로드

[GitHub Releases](https://github.com/chuckgu/fluxloop/releases) 페이지에서 최신 버전의 VSIX 파일을 다운로드합니다.

- 파일명 예시: `fluxloop-0.1.1.vsix`

#### 2. 설치

1. **Command Palette 열기** (`Cmd+Shift+P` 또는 `Ctrl+Shift+P`)
2. **"Extensions: Install from VSIX..."** 입력 및 선택
3. **다운로드한 VSIX 파일 선택**
4. **재시작**

## 필수 요구사항

FluxLoop Extension을 사용하려면 FluxLoop CLI, SDK, MCP 서버가 설치되어 있어야 합니다.

### 권장 설치 방법

프로젝트별 가상환경에 설치하는 것을 권장합니다:

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# FluxLoop 패키지 설치
pip install fluxloop-cli fluxloop fluxloop-mcp
```

### 대체 설치 방법

#### uv 사용

```bash
uv venv
source .venv/bin/activate
uv pip install fluxloop-cli fluxloop fluxloop-mcp
```

#### pipx (글로벌 설치)

```bash
pipx install fluxloop-cli
pipx install fluxloop-mcp
pip install fluxloop  # SDK는 프로젝트 venv에 설치 권장
```

### 설치 확인

확장에서 자동으로 진단:
```
FluxLoop: Run Doctor
```

또는 터미널에서:
```bash
# CLI 버전 확인
fluxloop --version

# SDK 확인
python -c "import fluxloop; print(fluxloop.__version__)"

# MCP 서버 확인
fluxloop-mcp --help

# 전체 환경 진단
fluxloop doctor
```

## 시스템 요구사항

- **Cursor**: 최신 버전 (VSCode 1.74.0+ 기반)
- **VS Code**: 1.74.0 이상
- **Python**: 3.8 이상
- **운영체제**: macOS, Linux, Windows

## 문제 해결

### Extension이 활성화되지 않음

**증상**: FluxLoop 아이콘이 보이지 않거나, 패널이 비어있음

**해결**:
1. Cursor/VS Code 재시작
2. Developer Tools 열기 (View → Toggle Developer Tools)
3. Console에서 에러 확인
4. 일반적으로 FluxLoop CLI 미설치가 원인:
   ```bash
   pip install fluxloop-cli fluxloop
   ```

### "Cannot find module 'yaml'" 에러

**증상**: Extension 활성화 시 에러 발생

**해결**:
- 최신 VSIX 파일 다운로드 및 재설치
- 구버전 VSIX는 런타임 의존성이 누락되었을 수 있습니다

### CLI가 인식되지 않음

**증상**: "FluxLoop CLI is not installed" 메시지

**해결**:
1. **환경 확인:**
   ```
   FluxLoop: Show Environment Info
   ```

2. **프로젝트 venv에 설치:**
```bash
   source .venv/bin/activate
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

3. **또는 글로벌 설치:**
   ```bash
pipx install fluxloop-cli
   pipx install fluxloop-mcp
   ```

4. **환경 모드 설정:**
   ```
   FluxLoop: Select Environment
   ```

5. **PATH 확인:**
   ```bash
   which fluxloop
   fluxloop doctor
```

### Cursor에서 Extension이 검색되지 않음

**증상**: Cursor Extensions에서 "FluxLoop" 검색 시 결과 없음

**해결**:
1. Extensions 탭이 제대로 로드되었는지 확인
2. 검색어를 정확히 **"FluxLoop"**로 입력
3. Cursor를 최신 버전으로 업데이트
4. 여전히 안 보이면 [Open VSX 페이지](https://open-vsx.org/extension/fluxloop/fluxloop)에서 직접 VSIX 다운로드 후 수동 설치

## 업데이트

### 자동 업데이트 (Cursor & VS Code)

**Marketplace에서 설치한 경우 자동 업데이트가 지원됩니다:**

- **Cursor**: Open VSX에서 새 버전 감지 시 자동 업데이트 또는 알림 표시
- **VS Code**: Marketplace에서 새 버전 감지 시 자동 업데이트 또는 알림 표시

Extensions 탭에서 FluxLoop을 찾아 **Update** 버튼이 있으면 클릭하세요.

### 수동 업데이트

VSIX로 설치한 경우:

1. GitHub Releases에서 최신 VSIX 다운로드
2. 기존 Extension 제거: Extensions 탭에서 FluxLoop → Uninstall
3. 재시작
4. Command Palette (`Cmd+Shift+P`) → **"Extensions: Install from VSIX..."**
5. 새 VSIX 파일 선택 후 재시작

## 다음 단계

Extension 설치 후:

- [프로젝트 생성하기](creating-first-project)
- [실험 실행하기](running-experiments)
- [사용자 가이드](../user-guide/creating-projects)
