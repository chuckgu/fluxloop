# PyPI 배포 가이드

FluxLoop SDK와 CLI를 PyPI에 배포하는 방법입니다.

## 사전 준비

### 1. PyPI 계정 생성
- [PyPI](https://pypi.org) 계정 생성
- [TestPyPI](https://test.pypi.org) 계정 생성 (테스트용, 선택사항)

### 2. API 토큰 발급
PyPI 웹사이트에서 API 토큰을 발급받습니다:
1. PyPI에 로그인
2. Account Settings → API tokens
3. "Add API token" 클릭
4. Scope: "Entire account" 또는 특정 프로젝트 선택
5. 토큰 복사 (한 번만 표시됩니다!)

### 3. 필수 도구 설치
```bash
pip install --upgrade build twine
```

## 배포 절차

### Step 1: 버전 확인 및 업데이트

각 패키지의 `pyproject.toml`에서 버전을 확인하고 필요시 업데이트합니다:
- `packages/sdk/pyproject.toml`: `version = "0.1.0"`
- `packages/cli/pyproject.toml`: `version = "0.1.0"`

버전 업데이트 규칙 ([Semantic Versioning](https://semver.org/)):
- `0.1.0` → `0.1.1`: 버그 수정
- `0.1.0` → `0.2.0`: 새 기능 추가
- `0.1.0` → `1.0.0`: 메이저 변경

### Step 2: SDK 빌드 및 배포

**⚠️ 중요: SDK를 먼저 배포해야 합니다** (CLI가 SDK에 의존하므로)

```bash
# SDK 디렉토리로 이동
cd packages/sdk

# 이전 빌드 삭제 및 새로 빌드
./build.sh

# 빌드 결과 확인
ls dist/
# 출력 예시:
# fluxloop-0.1.0-py3-none-any.whl
# fluxloop-0.1.0.tar.gz
```

### Step 3: SDK를 TestPyPI에 업로드 (선택사항, 권장)

먼저 테스트 서버에 업로드하여 문제가 없는지 확인:

```bash
# TestPyPI에 업로드
twine upload --repository testpypi dist/*

# Username: __token__
# Password: <TestPyPI API 토큰>

# TestPyPI에서 설치 테스트
pip install --index-url https://test.pypi.org/simple/ --no-deps fluxloop
```

### Step 4: SDK를 PyPI에 업로드

```bash
# PyPI에 업로드
twine upload dist/*

# Username: __token__
# Password: <PyPI API 토큰>
```

### Step 5: CLI 빌드 및 배포

SDK 배포가 완료되고 PyPI에 반영될 때까지 5-10분 정도 기다린 후:

```bash
# CLI 디렉토리로 이동
cd ../cli

# 빌드
./build.sh

# TestPyPI 테스트 (선택사항)
twine upload --repository testpypi dist/*

# PyPI에 업로드
twine upload dist/*
```

### Step 6: 설치 확인

```bash
# 새로운 가상환경에서 테스트
python3 -m venv test_env
source test_env/bin/activate

# 설치
pip install fluxloop
pip install fluxloop-cli

# 확인
python -c "import fluxloop; print(fluxloop.__version__)"
fluxloop --help

# 정리
deactivate
rm -rf test_env
```

## 자동화된 배포 (권장)

`.pypirc` 파일을 생성하여 자동화할 수 있습니다:

```bash
# ~/.pypirc 파일 생성
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <PyPI API 토큰>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <TestPyPI API 토큰>
EOF

chmod 600 ~/.pypirc
```

이후 비밀번호 입력 없이 배포 가능:
```bash
twine upload dist/*  # PyPI
twine upload --repository testpypi dist/*  # TestPyPI
```

## 배포 스크립트

전체 프로세스를 자동화하는 스크립트:

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 FluxLoop PyPI 배포 시작..."

# SDK 배포
echo "📦 SDK 빌드 및 배포..."
cd packages/sdk
./build.sh
twine upload dist/*

echo "⏳ PyPI 반영 대기 중 (10초)..."
sleep 10

# CLI 배포
echo "📦 CLI 빌드 및 배포..."
cd ../cli
./build.sh
twine upload dist/*

echo "✅ 배포 완료!"
echo "확인: pip install fluxloop fluxloop-cli"
```

## 버전 업데이트 체크리스트

새 버전 배포 시:

- [ ] 변경사항 정리 (`CHANGELOG.md` 업데이트)
- [ ] `pyproject.toml`의 버전 번호 업데이트
- [ ] SDK와 CLI의 버전 호환성 확인
- [ ] 로컬 테스트 실행 (`pytest`)
- [ ] SDK 먼저 배포
- [ ] CLI는 SDK 배포 후 배포
- [ ] PyPI에서 설치 테스트
- [ ] Git 태그 생성: `git tag v0.1.0 && git push --tags`

## 문제 해결

### 이미 존재하는 버전 에러
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists.
```
→ `pyproject.toml`의 버전을 올려야 합니다. PyPI는 같은 버전을 다시 업로드할 수 없습니다.

### 인증 실패
```
403 Forbidden
```
→ API 토큰이 올바른지 확인하세요. Username은 반드시 `__token__`이어야 합니다.

### README 렌더링 문제
→ `twine check dist/*`로 미리 확인하세요.

### CLI가 SDK를 찾지 못함
→ SDK를 먼저 배포하고, PyPI에 반영될 때까지 기다려야 합니다.

## 참고 링크

- [PyPI](https://pypi.org)
- [TestPyPI](https://test.pypi.org)
- [Python Packaging Guide](https://packaging.python.org)
- [Twine Documentation](https://twine.readthedocs.io)
- [Semantic Versioning](https://semver.org)

