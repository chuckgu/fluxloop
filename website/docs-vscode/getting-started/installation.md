---
sidebar_position: 1
---

# Installation

FluxLoop VSCode Extension 설치 방법을 안내합니다.

## 설치 방법

FluxLoop Extension은 **두 가지 방법**으로 설치할 수 있습니다:

### 방법 1: VSIX 파일로 설치 (Cursor 사용자 권장)

Cursor IDE는 VS Code Marketplace를 직접 지원하지 않으므로, VSIX 파일을 다운로드하여 설치해야 합니다.

#### 1. VSIX 파일 다운로드

[GitHub Releases](https://github.com/chuckgu/fluxloop/releases) 페이지에서 최신 버전의 VSIX 파일을 다운로드합니다.

- 파일명 예시: `fluxloop-0.1.0.vsix`
- 항상 최신 릴리스를 사용하세요

#### 2. Cursor에 설치

1. **Cursor 실행**
2. **Command Palette 열기** (`Cmd+Shift+P` 또는 `Ctrl+Shift+P`)
3. **"Extensions: Install from VSIX..."** 입력 및 선택
4. **다운로드한 VSIX 파일 선택**
5. **Cursor 재시작**

#### 3. 설치 확인

Cursor 재시작 후:
- 왼쪽 Activity Bar에 FluxLoop 아이콘이 표시됩니다
- 아이콘 클릭 시 Projects, Inputs, Experiments, Results, Status 패널이 표시됩니다

### 방법 2: VS Code Marketplace에서 설치 (VS Code 사용자)

VS Code를 사용하는 경우 Marketplace에서 직접 설치할 수 있습니다.

1. **VS Code 실행**
2. **Extensions 탭** (`Cmd+Shift+X` / `Ctrl+Shift+X`)
3. **"FluxLoop" 검색**
4. **Install 클릭**
5. **재시작**

또는 명령 팔레트에서:
```
ext install fluxloop.fluxloop
```

## 필수 요구사항

FluxLoop Extension을 사용하려면 FluxLoop CLI와 SDK가 설치되어 있어야 합니다.

### CLI 및 SDK 설치

```bash
# pip로 설치
pip install fluxloop-cli fluxloop

# 또는 pipx로 설치 (권장)
pipx install fluxloop-cli
pip install fluxloop
```

### 설치 확인

```bash
# CLI 버전 확인
fluxloop --version

# SDK 확인
python -c "import fluxloop; print(fluxloop.__version__)"
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
```bash
# PATH 확인
which fluxloop

# 없다면 설치
pip install fluxloop-cli

# 또는 pipx 사용
pipx install fluxloop-cli
```

### Cursor에서 Extension이 검색되지 않음

**증상**: Cursor Marketplace에서 "FluxLoop" 검색 시 결과 없음

**해결**:
- **정상 동작입니다**. Cursor는 VS Code Marketplace를 직접 지원하지 않습니다
- 대신 **VSIX 파일을 다운로드하여 수동 설치**하세요 (위 방법 1 참고)

## 업데이트

### Cursor 사용자

1. GitHub Releases에서 최신 VSIX 다운로드
2. 기존 Extension 제거:
   - Extensions 탭에서 FluxLoop 찾기 → Uninstall
3. Cursor 재시작
4. Command Palette (`Cmd+Shift+P`) → **"Extensions: Install from VSIX..."**
5. 새 VSIX 파일 선택 후 재시작

### VS Code 사용자

- Extensions 탭에서 자동 업데이트 알림 표시
- 또는 수동 업데이트: Extensions → FluxLoop → Update

## 다음 단계

Extension 설치 후:

- [프로젝트 생성하기](creating-first-project)
- [실험 실행하기](running-experiments)
- [사용자 가이드](../user-guide/creating-projects)
