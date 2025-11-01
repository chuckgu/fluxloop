# FluxLoop 문서 배포 가이드

## 🚀 빠른 배포 (Vercel 추천)

### 전제조건
- ✅ GitHub 계정
- ✅ Vercel 계정 (GitHub로 로그인)
- ✅ fluxloop.io 도메인

### 1단계: 코드 푸시

```bash
cd /Users/user/Documents/fluxloop
git add .
git commit -m "Add documentation website"
git push origin main
```

### 2단계: Vercel에서 임포트

1. https://vercel.com/new 접속
2. "Import Git Repository" → `fluxloop` 선택
3. 설정:
   - **Root Directory**: `website`
   - **Framework Preset**: Other
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
4. **Deploy** 클릭

약 2분 후 → `https://fluxloop-xxx.vercel.app` 생성됨

### 3단계: 커스텀 도메인 연결

**Vercel 대시보드:**
1. Settings → Domains
2. Add `docs.fluxloop.io`
3. DNS 레코드 안내 표시됨

**도메인 DNS 설정:**
```
Type: CNAME
Name: docs
Value: cname.vercel-dns.com
```

5-10분 후 → `https://docs.fluxloop.io` 접속 가능!

## 📋 상세 가이드

전체 가이드: [website/docs/deployment/vercel.md](./docs/deployment/vercel.md)

## 🔄 자동 배포

이제 모든 것이 자동입니다:

```bash
# 문서 수정
vim docs/intro.md

# 커밋 & 푸시
git commit -am "Update docs"
git push

# ✨ Vercel이 자동으로 빌드하고 배포!
```

## 🎨 PR 프리뷰

PR 생성하면:
- Vercel이 자동으로 프리뷰 URL 생성
- 예: `https://fluxloop-pr-123.vercel.app`
- PR에 자동으로 코멘트 추가

## 📊 모니터링

**Vercel Dashboard:**
- 배포 상태
- 빌드 로그
- Analytics (옵션)
- 성능 메트릭

## 🛠 로컬 테스트

배포 전 로컬에서 테스트:

```bash
cd website

# 빌드
npm run build

# 로컬 서버
npm run serve
# http://localhost:3000
```

## 📁 프로젝트 구조

```
fluxloop/
├── website/                 # 문서 사이트
│   ├── docs/               # 메인 문서
│   ├── docs-sdk/           # SDK 문서 (v0.1.0)
│   ├── docs-cli/           # CLI 문서 (v0.2.1)
│   ├── docs-vscode/        # VSCode 문서 (v0.1.0)
│   ├── blog/               # 블로그/릴리즈 노트
│   ├── src/                # 커스텀 페이지
│   ├── static/             # 이미지, 파일
│   ├── docusaurus.config.ts # 설정
│   ├── vercel.json         # Vercel 설정
│   └── package.json
├── packages/               # SDK, CLI, VSCode
├── services/               # Collector
└── .github/
    └── workflows/
        └── docs-ci.yml     # CI 자동화
```

## 🔧 환경 변수

**Vercel Dashboard → Settings → Environment Variables:**

검색 기능 활성화 (선택사항):
```
ALGOLIA_APP_ID=your-app-id
ALGOLIA_API_KEY=your-api-key
ALGOLIA_INDEX_NAME=fluxloop
```

## 🎯 체크리스트

배포 완료 후 확인:

- [ ] https://docs.fluxloop.io 접속 가능
- [ ] HTTPS 인증서 활성화
- [ ] 모든 페이지 정상 작동
- [ ] 네비게이션 링크 작동
- [ ] 모바일 반응형 확인
- [ ] PR 프리뷰 URL 생성 확인
- [ ] Git push → 자동 배포 확인

## 💡 팁

1. **빌드 속도 최적화**
   - `vercel.json`에 캐시 설정 완료
   - Node.js 18 사용

2. **SEO 최적화**
   - `sitemap.xml` 자동 생성됨
   - Google Search Console 등록 권장

3. **검색 추가**
   - Algolia DocSearch 신청 (무료)
   - https://docsearch.algolia.com/apply

4. **Analytics**
   - Vercel Analytics (무료 10K/월)
   - 또는 Google Analytics

## 🆘 문제 해결

### 빌드 실패
```bash
# 로컬에서 먼저 테스트
cd website
npm run build
```

### DNS 연결 안됨
- DNS 전파 대기 (최대 48시간, 보통 10분)
- https://dnschecker.org 에서 확인

### 404 오류
- `docusaurus.config.ts`의 `baseUrl: '/'` 확인
- `url: 'https://docs.fluxloop.io'` 확인

## 📞 지원

- **문서**: [Vercel 가이드](./docs/deployment/vercel.md)
- **Vercel 문서**: https://vercel.com/docs
- **Docusaurus 문서**: https://docusaurus.io/docs/deployment

---

**Happy Deploying!** 🚀

