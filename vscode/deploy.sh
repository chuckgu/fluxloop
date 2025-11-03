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

# Parse arguments
MARKETPLACE=false
TAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --marketplace)
            MARKETPLACE=true
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --help)
            echo "사용법: $0 [옵션]"
            echo ""
            echo "옵션:"
            echo "  --marketplace    VS Code Marketplace에도 게시"
            echo "  --tag TAG        GitHub Release 태그 지정 (예: vscode-v0.1.0)"
            echo "  --help           도움말 표시"
            exit 0
            ;;
        *)
            echo_error "알 수 없는 옵션: $1"
            echo "도움말: $0 --help"
            exit 1
            ;;
    esac
done

echo_info "🚀 FluxLoop VSCode Extension 배포 시작..."
echo ""

cd "$SCRIPT_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo_error "package.json을 찾을 수 없습니다."
    exit 1
fi

# Extract version from package.json
VERSION=$(grep -m 1 '"version"' package.json | sed 's/.*"version": "\(.*\)".*/\1/')
echo_info "Extension 버전: ${VERSION}"
echo ""

# Step 1: Install dependencies
echo_info "📦 의존성 설치 중..."
npm install
echo_success "의존성 설치 완료"
echo ""

# Step 2: Compile TypeScript
echo_info "🔨 TypeScript 컴파일 중..."
npm run compile
echo_success "컴파일 완료"
echo ""

# Step 3: Package VSIX
echo_info "📦 VSIX 패키징 중..."
VSIX_FILE="fluxloop-${VERSION}.vsix"
npx vsce package --out "$VSIX_FILE"
echo_success "VSIX 생성 완료: ${VSIX_FILE}"
echo ""

# Step 4: Test VSIX
echo_info "🧪 VSIX 파일 확인 중..."
if [ -f "$VSIX_FILE" ]; then
    FILE_SIZE=$(ls -lh "$VSIX_FILE" | awk '{print $5}')
    echo_success "VSIX 파일 크기: ${FILE_SIZE}"
else
    echo_error "VSIX 파일 생성 실패"
    exit 1
fi
echo ""

# Step 5: Create GitHub Release (if tag provided)
if [ -n "$TAG" ]; then
    echo_info "🏷️  GitHub Release 생성 중..."
    
    # Check if gh CLI is installed
    if ! command -v gh >/dev/null 2>&1; then
        echo_warning "gh CLI가 설치되지 않았습니다."
        echo_info "수동으로 GitHub Release를 생성하고 다음 파일을 업로드하세요:"
        echo_info "  ${VSIX_FILE}"
    else
        # Check if tag already exists
        if gh release view "$TAG" >/dev/null 2>&1; then
            echo_warning "Release '$TAG'가 이미 존재합니다."
            echo_info "VSIX 파일을 추가하시겠습니까? (y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                gh release upload "$TAG" "$VSIX_FILE" --clobber
                echo_success "VSIX 파일이 기존 Release에 추가되었습니다."
            fi
        else
            # Create new release
            NOTES="## FluxLoop VSCode Extension v${VERSION}

### 📦 설치 방법

#### Cursor 사용자
1. [$VSIX_FILE]을 다운로드
2. Cursor → Extensions → ... → Install from VSIX...
3. 다운로드한 파일 선택
4. 재시작

#### VS Code 사용자
- Marketplace에서 \"FluxLoop\" 검색 후 설치
- 또는 VSIX 파일로 수동 설치

### 📋 필수 요구사항
\`\`\`bash
pip install fluxloop-cli fluxloop
\`\`\`

### 🔗 문서
- [사용자 가이드](https://docs.fluxloop.dev/vscode)
- [GitHub](https://github.com/fluxloop/fluxloop)
"
            
            gh release create "$TAG" "$VSIX_FILE" \
                --title "VSCode Extension v${VERSION}" \
                --notes "$NOTES"
            
            echo_success "GitHub Release 생성 완료: https://github.com/fluxloop/fluxloop/releases/tag/${TAG}"
        fi
    fi
    echo ""
fi

# Step 6: Publish to Marketplace (if requested)
if [ "$MARKETPLACE" = true ]; then
    echo_info "🏪 VS Code Marketplace에 게시 중..."
    
    # Check if vsce is logged in
    if ! npx vsce ls >/dev/null 2>&1; then
        echo_warning "vsce 로그인이 필요합니다."
        echo_info "다음 명령으로 로그인하세요:"
        echo "  npx vsce login fluxloop"
        exit 1
    fi
    
    npx vsce publish
    echo_success "Marketplace 게시 완료"
    echo ""
fi

# Summary
echo_success "=========================================="
echo_success "🎉 배포 완료!"
echo_success "=========================================="
echo ""
echo_info "배포된 파일:"
echo "  - ${VSIX_FILE}"
echo ""
echo_info "다음 단계:"
echo "  1. Cursor/VS Code에서 VSIX 파일 설치 테스트"

if [ -z "$TAG" ]; then
    echo "  2. GitHub Release 생성:"
    echo "     ./deploy.sh --tag vscode-v${VERSION}"
fi

if [ "$MARKETPLACE" = false ]; then
    echo "  3. (선택) Marketplace에 게시:"
    echo "     ./deploy.sh --marketplace"
fi

echo ""
echo_info "VSIX 파일 위치: ${SCRIPT_DIR}/${VSIX_FILE}"
echo ""

