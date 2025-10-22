#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

echo_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

# Check if twine is installed
if ! command -v twine >/dev/null 2>&1; then
    echo_error "twine이 설치되지 않았습니다."
    echo_info "다음 명령으로 설치하세요: pip install twine"
    exit 1
fi

# Check if build is installed
if ! python3 -m pip show build >/dev/null 2>&1; then
    echo_error "build 패키지가 설치되지 않았습니다."
    echo_info "다음 명령으로 설치하세요: pip install build"
    exit 1
fi

# Parse arguments
ENVIRONMENT="pypi"
SKIP_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            ENVIRONMENT="testpypi"
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --help)
            echo "사용법: $0 [옵션]"
            echo ""
            echo "옵션:"
            echo "  --test         TestPyPI에 배포 (기본: PyPI)"
            echo "  --skip-tests   테스트 건너뛰기"
            echo "  --help         도움말 표시"
            exit 0
            ;;
        *)
            echo_error "알 수 없는 옵션: $1"
            echo "도움말: $0 --help"
            exit 1
            ;;
    esac
done

echo_info "🚀 FluxLoop ${ENVIRONMENT} 배포 시작..."
echo ""

# Step 1: Run tests (unless skipped)
if [ "$SKIP_TESTS" = false ]; then
    echo_info "📝 SDK 테스트 실행 중..."
    cd "${SCRIPT_DIR}/sdk"
    if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
        if python3 -m pytest tests/ -v 2>/dev/null; then
            echo_success "SDK 테스트 통과"
        else
            echo_warning "SDK 테스트 실패 또는 pytest 미설치 (계속 진행)"
        fi
    else
        echo_warning "SDK 테스트 없음 (건너뜀)"
    fi
    
    echo ""
    echo_info "📝 CLI 테스트 실행 중..."
    cd "${SCRIPT_DIR}/cli"
    if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
        if python3 -m pytest tests/ -v 2>/dev/null; then
            echo_success "CLI 테스트 통과"
        else
            echo_warning "CLI 테스트 실패 또는 pytest 미설치 (계속 진행)"
        fi
    else
        echo_warning "CLI 테스트 없음 (건너뜀)"
    fi
    echo ""
fi

# Step 2: Build and upload SDK
echo_info "📦 SDK 빌드 중..."
cd "${SCRIPT_DIR}/sdk"

# Extract version from pyproject.toml
SDK_VERSION=$(grep -m 1 '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo_info "SDK 버전: ${SDK_VERSION}"

./build.sh

echo_info "SDK 패키지 검증 중..."
twine check dist/*

if [ "$ENVIRONMENT" = "testpypi" ]; then
    echo_info "TestPyPI에 SDK 업로드 중..."
    twine upload --repository testpypi dist/*
    INSTALL_COMMAND="pip install --index-url https://test.pypi.org/simple/ --no-deps fluxloop"
else
    echo_info "PyPI에 SDK 업로드 중..."
    twine upload dist/*
    INSTALL_COMMAND="pip install fluxloop"
fi

echo_success "SDK 업로드 완료!"
echo ""

# Step 3: Wait for PyPI to process
echo_info "⏳ ${ENVIRONMENT} 서버가 패키지를 처리할 때까지 대기 중..."
WAIT_TIME=15
for i in $(seq $WAIT_TIME -1 1); do
    echo -ne "\r${YELLOW}남은 시간: ${i}초${NC}  "
    sleep 1
done
echo -e "\r${GREEN}대기 완료!${NC}           "
echo ""

# Step 4: Build and upload CLI
echo_info "📦 CLI 빌드 중..."
cd "${SCRIPT_DIR}/cli"

# Extract version from pyproject.toml
CLI_VERSION=$(grep -m 1 '^version' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo_info "CLI 버전: ${CLI_VERSION}"

./build.sh

echo_info "CLI 패키지 검증 중..."
twine check dist/*

if [ "$ENVIRONMENT" = "testpypi" ]; then
    echo_info "TestPyPI에 CLI 업로드 중..."
    # CLI needs SDK, so we need to allow external dependencies
    twine upload --repository testpypi dist/*
    INSTALL_CLI_COMMAND="pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple fluxloop-cli"
else
    echo_info "PyPI에 CLI 업로드 중..."
    twine upload dist/*
    INSTALL_CLI_COMMAND="pip install fluxloop-cli"
fi

echo_success "CLI 업로드 완료!"
echo ""

# Summary
echo_success "=========================================="
echo_success "🎉 배포 완료!"
echo_success "=========================================="
echo ""
echo_info "배포된 버전:"
echo "  - fluxloop: ${SDK_VERSION}"
echo "  - fluxloop-cli: ${CLI_VERSION}"
echo ""
echo_info "설치 방법:"
echo "  ${INSTALL_COMMAND}"
echo "  ${INSTALL_CLI_COMMAND}"
echo ""
echo_info "다음 단계:"
echo "  1. 새로운 가상환경에서 설치 테스트"
echo "  2. Git 태그 생성: git tag v${SDK_VERSION} && git push --tags"
echo "  3. GitHub Release 생성 (선택사항)"
echo ""

if [ "$ENVIRONMENT" = "testpypi" ]; then
    echo_warning "TestPyPI에 배포되었습니다. 실제 배포는 --test 옵션 없이 실행하세요."
fi

