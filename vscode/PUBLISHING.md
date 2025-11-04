# FluxLoop VSCode Extension 게시 가이드

이 문서는 FluxLoop VSCode Extension을 배포하는 방법을 안내합니다.

## 📦 배포 방식

FluxLoop VSCode Extension은 **두 가지 방법**으로 배포할 수 있습니다:

1. **GitHub Releases (VSIX)** - Cursor 사용자를 위한 권장 방식
2. **VS Code Marketplace** - VS Code 사용자를 위한 공식 방식 (선택사항)

---

## 🎯 방법 1: GitHub Releases (VSIX 배포) - **권장**

### 왜 GitHub Releases를 사용하나요?

- ✅ **Cursor 호환성**: Cursor는 VS Code Marketplace를 직접 지원하지 않습니다
- ✅ **간단한 배포**: Marketplace 승인 없이 즉시 배포 가능
- ✅ **버전 관리**: GitHub Release와 연동하여 체계적 관리
- ✅ **직접 제어**: 승인 프로세스 없이 자유롭게 업데이트

### 1.1 버전 업데이트

```bash
cd packages/vscode

# package.json의 버전 업데이트
# "version": "0.1.1"

# CHANGELOG.md 업데이트
# 변경사항 기록
```

### 1.2 빌드 및 VSIX 생성

```bash
# 의존성 설치
npm install

# TypeScript 컴파일
npm run compile

# VSIX 패키지 생성
npx vsce package
# 출력: fluxloop-0.1.1.vsix
```

**중요**: `.vscodeignore` 파일에서 `node_modules/**`를 제외하지 **않도록** 확인하세요. 
런타임 의존성(`yaml`, `which` 등)이 VSIX에 포함되어야 합니다.

### 1.3 로컬 테스트

#### Cursor에서 테스트:
1. Cursor 실행
2. Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
3. **"Extensions: Install from VSIX..."** 입력 및 선택
4. 생성된 `fluxloop-0.1.1.vsix` 선택
5. Cursor 재시작
6. FluxLoop 패널이 정상 작동하는지 확인

#### VS Code에서 테스트:
1. VS Code 실행
2. Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
3. **"Extensions: Install from VSIX..."** 입력 및 선택
4. VSIX 파일 선택
5. 재시작 후 확인

### 1.4 GitHub Release 생성

#### GitHub 웹사이트에서:

1. 저장소 → **Releases** → **Draft a new release**
2. 태그 버전 생성: `vscode-v0.1.1` (또는 `v0.1.1`)
3. Release 제목: `VSCode Extension v0.1.1`
4. 설명 작성 (CHANGELOG.md 참고):
   ```markdown
   ## 🎉 FluxLoop VSCode Extension v0.1.1
   
   ### ✨ Features
   - Projects 관리
   - 실험 실행 및 결과 조회
   - 입력 생성 및 관리
   - 레코딩 모드 지원
   
   ### 📦 설치 방법
   
   #### Cursor 사용자
1. [fluxloop-0.1.1.vsix](링크) 다운로드
   2. Cursor → Extensions → `...` → Install from VSIX...
   3. 다운로드한 파일 선택
   4. 재시작
   
   #### VS Code 사용자
   - Marketplace에서 "FluxLoop" 검색 후 설치
   - 또는 VSIX 파일로 수동 설치
   
   ### 📋 필수 요구사항
   ```bash
   pip install fluxloop-cli fluxloop
   ```
   
   ### 🔗 문서
   - [사용자 가이드](https://docs.fluxloop.dev/vscode)
   - [GitHub](https://github.com/fluxloop/fluxloop)
   ```

5. **Attach binaries**: `fluxloop-0.1.1.vsix` 파일 업로드
6. **Publish release** 클릭

#### 명령줄에서 (GitHub CLI 사용):

```bash
# GitHub CLI 설치 확인
gh --version

# Release 생성 및 VSIX 업로드
cd packages/vscode
gh release create vscode-v0.1.1 \
  fluxloop-0.1.1.vsix \
  --title "VSCode Extension v0.1.1" \
  --notes-file CHANGELOG.md
```

### 1.5 사용자 설치 안내

Release 페이지에 다음 안내를 추가하세요:

```markdown
## 📥 설치 방법

### Cursor 사용자 (권장)

1. **VSIX 다운로드**
   - [fluxloop-0.1.1.vsix](릴리스 링크) 클릭하여 다운로드

2. **Cursor에 설치**
   - Command Palette 열기 (`Cmd+Shift+P` 또는 `Ctrl+Shift+P`)
   - **"Extensions: Install from VSIX..."** 입력 및 선택
   - 다운로드한 `.vsix` 파일 선택

3. **Cursor 재시작**

4. **FluxLoop CLI 설치** (필수)
   ```bash
   pip install fluxloop-cli fluxloop
   ```

### VS Code 사용자

- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop)에서 설치
- 또는 위와 동일한 방법으로 VSIX 수동 설치

## ⚙️ 요구사항

- Cursor 또는 VS Code 1.74.0 이상
- Python 3.8+
- FluxLoop CLI: `pip install fluxloop-cli fluxloop`
```

---

## 🌐 방법 2: Open VSX 배포 (Cursor 사용자용 - 권장)

Cursor 사용자들이 Extensions 탭에서 검색하여 설치할 수 있도록 Open VSX에 배포합니다.

### 2.1 사전 요구사항

1. **Open VSX 계정**
   - https://open-vsx.org 에 GitHub 계정으로 로그인

2. **Access Token 발급**
   - Open VSX 웹사이트 → 우측 상단 프로필 → **Settings**
   - **Access Tokens** 탭
   - **New Access Token** 클릭
   - Description: "FluxLoop Publishing"
   - **Create** 클릭
   - ⚠️ **토큰을 복사해서 안전한 곳에 저장** (다시 볼 수 없습니다!)

### 2.2 Namespace 생성 (최초 1회만)

```bash
cd packages/vscode

# 환경 변수로 토큰 설정
export OVSX_PAT=your_token_here

# Namespace 생성
npx ovsx create-namespace fluxloop -p $OVSX_PAT
```

**성공 메시지**: `✅ Created namespace fluxloop`

### 2.3 Extension 게시

```bash
# VSIX 파일이 있는지 확인
ls fluxloop-*.vsix

# Open VSX에 게시
npx ovsx publish fluxloop-0.1.1.vsix -p $OVSX_PAT
```

### 2.4 게시 확인

게시 후 즉시:
- **Open VSX 페이지**: `https://open-vsx.org/extension/fluxloop/fluxloop`
- Cursor Extensions 탭에서 "FluxLoop" 검색하면 표시됨

### 2.5 Verified Publisher 되기 (선택사항)

현재는 ⚠️ "Unverified publisher" 경고가 표시됩니다. Verified 표시를 받으려면:

1. **GitHub Issue 생성**
   - https://github.com/EclipseFdn/open-vsx.org/issues/new

2. **템플릿:**
   ```markdown
   Title: Request namespace ownership: fluxloop
   
   I would like to claim ownership of the namespace "fluxloop" on Open VSX.
   
   - Project: https://github.com/chuckgu/fluxloop
   - Open VSX Extension: https://open-vsx.org/extension/fluxloop/fluxloop
   - Publisher: fluxloop (matches namespace)
   
   I am the maintainer of FluxLoop, an open-source AI agent simulation toolkit.
   ```

3. **승인 대기** (3-7일 소요)
4. 승인되면 🛡️ Verified 표시 및 경고 제거

---

## 🏪 방법 3: VS Code Marketplace 배포 (VS Code 사용자용)

VS Code 사용자를 위해 공식 Marketplace에도 배포할 수 있습니다.

### 2.1 사전 요구사항

1. **Publisher 생성 완료**
   - Publisher ID: `fluxloop`
   - [Marketplace 관리 페이지](https://marketplace.visualstudio.com/manage)

2. **Azure DevOps Personal Access Token (PAT) 준비**

### 2.2 Personal Access Token 생성

1. [Azure DevOps](https://dev.azure.com/)에 접속
2. 오른쪽 상단 프로필 아이콘 클릭 → **Personal Access Tokens**
3. **+ New Token** 클릭
4. 설정:
   - **Name**: `vsce-publish-token`
   - **Organization**: All accessible organizations
   - **Expiration**: 1년
   - **Scopes**: 
     - ✅ **Custom defined** 선택
     - ✅ **Marketplace** → **Manage** 체크
5. **Create** 클릭
6. ⚠️ **토큰을 복사해서 안전한 곳에 저장**

### 2.3 vsce 로그인

```bash
cd packages/vscode
npx vsce login fluxloop
# Personal Access Token 입력
```

### 2.4 Marketplace에 게시

```bash
# 처음 게시
npx vsce publish

# 특정 버전으로 게시
npx vsce publish 0.1.1

# 자동 버전 증가
npx vsce publish patch  # 0.1.1 → 0.1.2
npx vsce publish minor  # 0.1.1 → 0.2.0
npx vsce publish major  # 0.1.1 → 1.0.0
```

### 2.5 게시 확인

게시 후 5-10분 내에:
- **Marketplace 페이지**: `https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop`
- **관리 페이지**: `https://marketplace.visualstudio.com/manage/publishers/fluxloop`

---

## 📝 버전 업데이트 체크리스트

새 버전 배포 시:

- [ ] `package.json`의 `version` 업데이트
- [ ] `CHANGELOG.md`에 변경사항 추가
- [ ] `README.md` 업데이트 (필요시)
- [ ] `npm run compile` 성공 확인
- [ ] `npx vsce package` 성공 및 VSIX 생성 확인
- [ ] Cursor 및 VS Code에서 VSIX 로컬 설치 테스트
- [ ] GitHub Release 생성 및 VSIX 업로드
- [ ] Git 태그 생성: `git tag vscode-v0.1.1 && git push --tags`
- [ ] (선택) Marketplace에 게시: `npx vsce publish`

---

## 🛠️ 문제 해결

### "Cannot find module 'yaml'" 에러

**원인**: `.vscodeignore`가 `node_modules`를 제외하여 런타임 의존성이 누락됨

**해결**:
```bash
# .vscodeignore 확인
# node_modules/** 라인이 주석 처리되었는지 확인

# 다시 패키징
npx vsce package
```

### Cursor에서 "There is no data provider registered" 에러

**원인**: Extension 활성화 중 오류 발생

**해결**:
1. Cursor Developer Tools 열기 (View → Toggle Developer Tools)
2. Console에서 에러 확인
3. 보통 의존성 누락 문제이므로 VSIX 재빌드

### VSIX 파일 크기가 너무 큼

**해결**:
```bash
# .vscodeignore에 불필요한 파일 제외 추가
# 예: 테스트 파일, 예제 등
test/**
examples/**
*.test.ts
```

### Marketplace 게시 실패

**"Extension version should be different"**:
- `package.json`의 버전을 이전 버전과 다르게 업데이트

**"Invalid publisher"**:
- `package.json`의 `publisher` 필드 확인: `"publisher": "fluxloop"`

**"License is required"**:
- 프로젝트 루트에 `LICENSE` 파일 추가

---

## 📚 참고 자료

- [Open VSX Registry](https://open-vsx.org/)
- [Open VSX Publishing Guide](https://github.com/eclipse/openvsx/wiki/Publishing-Extensions)
- [Open VSX Namespace Access](https://github.com/eclipse/openvsx/wiki/Namespace-Access)
- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [vsce CLI 문서](https://github.com/microsoft/vscode-vsce)
- [GitHub Releases 문서](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [FluxLoop Releases](https://github.com/chuckgu/fluxloop/releases)

---

## 🎯 권장 배포 전략

### 일반 릴리스 (3단계 배포)

1. **Open VSX** - Cursor 사용자 자동 업데이트 ⭐
   ```bash
   npx ovsx publish fluxloop-0.1.1.vsix -p $OVSX_PAT
   ```

2. **VS Code Marketplace** - VS Code 사용자 자동 업데이트 ⭐
   ```bash
   npx vsce publish
   ```

3. **GitHub Releases (VSIX)** - 수동 설치용 (백업)
   ```bash
   ./deploy.sh --tag vscode-v0.1.1
   ```

### 베타/알파 릴리스
- **GitHub Releases만 사용** (Pre-release로 표시)
- VSIX 파일명에 `beta` 표시: `fluxloop-0.2.0-beta.1.vsix`
- Marketplace는 정식 버전만 게시

### 핫픽스
1. 빠르게 Open VSX + Marketplace 배포 (즉시 반영)
2. GitHub Release는 선택사항

### 버전 업데이트 워크플로우

```bash
# 1. 버전 올리기 (package.json, CHANGELOG.md)
# 2. 빌드
npm run compile
npx vsce package

# 3. 로컬 테스트
# - VSIX로 설치 후 확인

# 4. 배포
npx ovsx publish fluxloop-0.1.1.vsix -p $OVSX_PAT    # Cursor
npx vsce publish                                      # VS Code
./deploy.sh --tag vscode-v0.1.1                       # GitHub (선택)
```
