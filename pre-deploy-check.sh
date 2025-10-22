#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((CHECKS_WARNING++))
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FluxLoop 배포 전 검증${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check 1: Python version
echo "🔍 Python 버전 확인..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    check_pass "Python 버전: $PYTHON_VERSION"
else
    check_fail "Python 3.8 이상이 필요합니다. 현재: $PYTHON_VERSION"
fi
echo ""

# Check 2: Required tools
echo "🔍 필수 도구 확인..."
if command -v twine >/dev/null 2>&1; then
    TWINE_VERSION=$(twine --version 2>&1 | head -n1)
    check_pass "twine 설치됨: $TWINE_VERSION"
else
    check_fail "twine이 설치되지 않음. 설치: pip install twine"
fi

if python3 -m pip show build >/dev/null 2>&1; then
    BUILD_VERSION=$(python3 -m pip show build | grep Version | awk '{print $2}')
    check_pass "build 설치됨: $BUILD_VERSION"
else
    check_fail "build가 설치되지 않음. 설치: pip install build"
fi
echo ""

# Check 3: SDK files
echo "🔍 SDK 파일 확인..."
cd "${SCRIPT_DIR}/sdk"

if [ -f "pyproject.toml" ]; then
    check_pass "SDK pyproject.toml 존재"
    SDK_VERSION=$(grep -m 1 '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo "   📦 SDK 버전: $SDK_VERSION"
else
    check_fail "SDK pyproject.toml 없음"
fi

if [ -f "README.md" ]; then
    check_pass "SDK README.md 존재"
    README_SIZE=$(wc -c < README.md)
    if [ "$README_SIZE" -lt 100 ]; then
        check_warn "SDK README.md가 너무 짧습니다 (${README_SIZE} bytes)"
    fi
else
    check_fail "SDK README.md 없음"
fi

if [ -d "fluxloop" ]; then
    check_pass "SDK 소스 디렉토리 존재 (fluxloop/)"
    PY_FILES=$(find fluxloop -name "*.py" | wc -l)
    echo "   📄 Python 파일: $PY_FILES개"
else
    check_fail "SDK 소스 디렉토리 없음 (fluxloop/)"
fi
echo ""

# Check 4: CLI files
echo "🔍 CLI 파일 확인..."
cd "${SCRIPT_DIR}/cli"

if [ -f "pyproject.toml" ]; then
    check_pass "CLI pyproject.toml 존재"
    CLI_VERSION=$(grep -m 1 '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo "   📦 CLI 버전: $CLI_VERSION"
    
    # Check if CLI depends on correct SDK version
    SDK_DEP=$(grep 'fluxloop>=' pyproject.toml | sed 's/.*fluxloop>=\([0-9.]*\).*/\1/' || echo "")
    if [ -n "$SDK_DEP" ]; then
        echo "   🔗 SDK 의존성: >=$SDK_DEP"
        if [ "$SDK_DEP" != "$SDK_VERSION" ]; then
            check_warn "CLI가 요구하는 SDK 버전($SDK_DEP)과 현재 SDK 버전($SDK_VERSION)이 다릅니다"
        fi
    fi
else
    check_fail "CLI pyproject.toml 없음"
fi

if [ -f "README.md" ]; then
    check_pass "CLI README.md 존재"
    README_SIZE=$(wc -c < README.md)
    if [ "$README_SIZE" -lt 100 ]; then
        check_warn "CLI README.md가 너무 짧습니다 (${README_SIZE} bytes)"
    fi
else
    check_fail "CLI README.md 없음"
fi

if [ -d "fluxloop_cli" ]; then
    check_pass "CLI 소스 디렉토리 존재 (fluxloop_cli/)"
    PY_FILES=$(find fluxloop_cli -name "*.py" | wc -l)
    echo "   📄 Python 파일: $PY_FILES개"
else
    check_fail "CLI 소스 디렉토리 없음 (fluxloop_cli/)"
fi
echo ""

# Check 5: License
echo "🔍 라이센스 확인..."
cd "${SCRIPT_DIR}"
if [ -f "LICENSE" ]; then
    check_pass "LICENSE 파일 존재"
    
    # Check if license in pyproject.toml matches LICENSE file
    SDK_LICENSE=$(grep -m 1 'license.*=' sdk/pyproject.toml | sed 's/.*"\(.*\)".*/\1/' || echo "")
    CLI_LICENSE=$(grep -m 1 'license.*=' cli/pyproject.toml | sed 's/.*"\(.*\)".*/\1/' || echo "")
    
    if grep -q "Apache" LICENSE; then
        LICENSE_TYPE="Apache-2.0"
    elif grep -q "MIT" LICENSE; then
        LICENSE_TYPE="MIT"
    else
        LICENSE_TYPE="Unknown"
    fi
    
    echo "   📜 LICENSE 파일 타입: $LICENSE_TYPE"
    echo "   📜 SDK pyproject.toml: $SDK_LICENSE"
    echo "   📜 CLI pyproject.toml: $CLI_LICENSE"
    
    if [ "$SDK_LICENSE" != "$LICENSE_TYPE" ] || [ "$CLI_LICENSE" != "$LICENSE_TYPE" ]; then
        check_warn "pyproject.toml의 라이센스가 LICENSE 파일과 일치하지 않을 수 있습니다"
    fi
else
    check_fail "LICENSE 파일 없음"
fi
echo ""

# Check 6: Git status
echo "🔍 Git 상태 확인..."
cd "${SCRIPT_DIR}/.."
if git rev-parse --git-dir > /dev/null 2>&1; then
    if [ -n "$(git status --porcelain)" ]; then
        check_warn "커밋되지 않은 변경사항이 있습니다"
        echo "   다음 파일들이 변경되었습니다:"
        git status --short | head -5
    else
        check_pass "Git 작업 디렉토리가 깨끗합니다"
    fi
    
    # Check if tag exists
    if [ -n "$SDK_VERSION" ]; then
        if git tag | grep -q "^v${SDK_VERSION}$"; then
            check_warn "태그 v${SDK_VERSION}이(가) 이미 존재합니다"
        else
            echo "   ℹ️  배포 후 태그 생성 권장: git tag v${SDK_VERSION}"
        fi
    fi
else
    check_warn "Git 저장소가 아닙니다"
fi
echo ""

# Check 7: Test build (dry run)
echo "🔍 빌드 테스트 (시험 실행)..."
cd "${SCRIPT_DIR}/sdk"
if ./build.sh > /dev/null 2>&1; then
    check_pass "SDK 빌드 성공"
    if [ -d "dist" ] && [ "$(ls -A dist 2>/dev/null)" ]; then
        DIST_FILES=$(ls dist | wc -l)
        echo "   📦 생성된 파일: $DIST_FILES개"
        
        # Validate package
        if command -v twine >/dev/null 2>&1; then
            if twine check dist/* > /dev/null 2>&1; then
                check_pass "SDK 패키지 검증 통과"
            else
                check_fail "SDK 패키지 검증 실패"
                twine check dist/* 2>&1 | head -5
            fi
        fi
    fi
    rm -rf dist build
else
    check_fail "SDK 빌드 실패"
fi

cd "${SCRIPT_DIR}/cli"
if ./build.sh > /dev/null 2>&1; then
    check_pass "CLI 빌드 성공"
    if [ -d "dist" ] && [ "$(ls -A dist 2>/dev/null)" ]; then
        DIST_FILES=$(ls dist | wc -l)
        echo "   📦 생성된 파일: $DIST_FILES개"
        
        # Validate package
        if command -v twine >/dev/null 2>&1; then
            if twine check dist/* > /dev/null 2>&1; then
                check_pass "CLI 패키지 검증 통과"
            else
                check_fail "CLI 패키지 검증 실패"
                twine check dist/* 2>&1 | head -5
            fi
        fi
    fi
    rm -rf dist build
else
    check_fail "CLI 빌드 실패"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  검증 결과${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 통과: $CHECKS_PASSED${NC}"
echo -e "${YELLOW}⚠️  경고: $CHECKS_WARNING${NC}"
echo -e "${RED}❌ 실패: $CHECKS_FAILED${NC}"
echo ""

if [ "$CHECKS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 배포 준비가 완료되었습니다!${NC}"
    echo ""
    echo "다음 단계:"
    echo "  1. TestPyPI 배포: ./deploy.sh --test"
    echo "  2. PyPI 배포: ./deploy.sh"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  배포 전에 실패한 검사를 수정해주세요.${NC}"
    echo ""
    exit 1
fi

