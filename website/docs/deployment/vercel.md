---
sidebar_position: 1
---

# Vercel 배포 (추천)

FluxLoop 문서를 Vercel로 배포하고 `fluxloop.ai` 도메인을 연결하세요.

## 왜 Vercel인가?

- ⚡ **엄청나게 빠름**: 글로벌 Edge Network
- 🔄 **자동 배포**: Git push하면 자동 배포
- 🎨 **PR 프리뷰**: 모든 PR마다 고유 URL 생성
- 🌍 **커스텀 도메인**: `fluxloop.ai` 무료 연결
- 🔒 **자동 HTTPS**: Let's Encrypt 인증서 자동 갱신
- 💰 **무료**: 개인/오픈소스 프로젝트 무료

## 1단계: Git 저장소 푸시

먼저 코드를 GitHub에 푸시하세요:

```bash
cd /Users/user/Documents/fluxloop

# 원격 저장소 추가 (아직 안했다면)
git remote add origin https://github.com/chuckgu/fluxloop.git

# 커밋 및 푸시
git add .
git commit -m "Add documentation website"
git push -u origin main
```

## 2단계: Vercel 프로젝트 생성

### 웹 UI 방식 (추천)

1. **[Vercel](https://vercel.com)에 로그인**
   - GitHub 계정으로 로그인

2. **"Add New Project" 클릭**

3. **Import Git Repository**
   - `fluxloop` 저장소 선택
   - Import 클릭

4. **프로젝트 설정**
   ```
   Framework Preset: Other
   Root Directory: website
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```

5. **Deploy 클릭**
   - 약 1-2분 후 배포 완료
   - `https://fluxloop.vercel.app` 같은 URL 생성

### CLI 방식 (선택사항)

```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 디렉토리로 이동
cd /Users/user/Documents/fluxloop/website

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

## 3단계: 커스텀 도메인 연결

### Vercel에서 도메인 추가

1. **Vercel 대시보드** → 프로젝트 선택

2. **Settings** → **Domains**

3. **Add Domain**
   - `docs.fluxloop.ai` 입력 (또는 `fluxloop.ai`)
   - Add 클릭

4. **DNS 설정 지시사항 표시**
   - Vercel이 추가할 DNS 레코드를 보여줍니다

### 도메인 제공업체 DNS 설정

도메인 등록업체(GoDaddy, Namecheap, Cloudflare 등)에서:

#### 옵션 1: 서브도메인 (docs.fluxloop.ai)

```
Type: CNAME
Name: docs
Value: cname.vercel-dns.com
```

#### 옵션 2: Apex 도메인 (fluxloop.ai)

```
Type: A
Name: @
Value: 76.76.21.21
```

**추가 A 레코드:**
```
Type: A
Name: @
Value: 76.76.19.19
```

#### www 리다이렉트 (선택사항)

```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### DNS 전파 확인

DNS 변경은 최대 48시간이 걸릴 수 있지만, 보통 5-10분 내에 완료됩니다.

```bash
# DNS 확인
nslookup docs.fluxloop.ai

# 또는
dig docs.fluxloop.ai
```

## 4단계: 프로젝트 설정 최적화

### docusaurus.config.ts 업데이트

커스텀 도메인에 맞게 설정:

```typescript
const config: Config = {
  url: 'https://docs.fluxloop.ai',  // 또는 'https://fluxloop.ai'
  baseUrl: '/',  // Apex 도메인이므로 /
  organizationName: 'chuckgu',
  projectName: 'fluxloop',
  
  // ... 나머지 설정
};
```

변경 후 커밋하고 푸시:

```bash
git add website/docusaurus.config.ts
git commit -m "Update domain to fluxloop.ai"
git push
```

Vercel이 자동으로 재배포합니다!

## 5단계: 자동 배포 설정 완료 ✅

이제 모든 것이 자동화됩니다:

### Main 브랜치 → 프로덕션

```bash
git push origin main
# → 자동으로 docs.fluxloop.ai에 배포
```

### PR → 프리뷰 URL

```bash
git checkout -b feature/new-docs
git push origin feature/new-docs
# GitHub에서 PR 생성
# → Vercel이 자동으로 프리뷰 URL 생성
# 예: https://fluxloop-pr-123.vercel.app
```

## 환경 변수 설정

검색(Algolia) 등에 필요한 환경 변수:

1. **Vercel Dashboard** → **Settings** → **Environment Variables**

2. **추가할 변수들:**
   ```
   ALGOLIA_APP_ID=your-app-id
   ALGOLIA_API_KEY=your-api-key
   ALGOLIA_INDEX_NAME=fluxloop
   ```

3. **Save**

4. **Redeploy** (자동으로 새 빌드 시작)

## Vercel 설정 팁

### 빌드 최적화

`vercel.json` 파일 생성 (선택사항):

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": null,
  "devCommand": "npm start",
  "installCommand": "npm install",
  "regions": ["icn1", "sfo1"],
  "github": {
    "silent": false
  }
}
```

### 성능 모니터링

Vercel Analytics 활성화:

1. **Dashboard** → **Analytics**
2. **Enable Analytics**
3. 무료 플랜: 10,000 페이지뷰/월

### 보안 헤더

`vercel.json`에 추가:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

## CI/CD with GitHub Actions (선택사항)

Vercel은 자동 배포를 제공하지만, 추가 검증을 위해 GitHub Actions를 사용할 수 있습니다.

`.github/workflows/docs.yml` 생성:

```yaml
name: Documentation CI

on:
  push:
    branches: [main]
    paths:
      - 'website/**'
  pull_request:
    branches: [main]
    paths:
      - 'website/**'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'npm'
          cache-dependency-path: website/package-lock.json
      
      - name: Install dependencies
        run: |
          cd website
          npm ci
      
      - name: Build website
        run: |
          cd website
          npm run build
      
      - name: Test build
        run: |
          cd website
          npm run serve &
          sleep 5
          curl --fail http://localhost:3000 || exit 1
```

이렇게 하면:
- PR마다 빌드 테스트
- 문제 있으면 머지 차단
- Vercel 배포는 여전히 자동

## 배포 확인

### 체크리스트

- [ ] Vercel 프로젝트 생성 완료
- [ ] Git push로 자동 배포 확인
- [ ] 커스텀 도메인 연결 (`docs.fluxloop.ai`)
- [ ] HTTPS 인증서 활성화 확인
- [ ] PR 프리뷰 URL 생성 확인
- [ ] 환경 변수 설정 (필요시)

### 테스트

```bash
# 도메인 접속 테스트
curl -I https://docs.fluxloop.ai

# 응답 확인
# HTTP/2 200
# server: Vercel
```

## 문제 해결

### 빌드 실패

1. **Vercel Dashboard** → **Deployments** → 실패한 배포 클릭
2. 빌드 로그 확인
3. 로컬에서 테스트:
   ```bash
   cd website
   npm run build
   ```

### DNS 연결 안됨

1. **Vercel Dashboard** → **Domains** 상태 확인
2. DNS 전파 확인: https://dnschecker.org
3. 최대 48시간 대기 (보통 10분)

### 404 오류

`docusaurus.config.ts`의 `baseUrl` 확인:
```typescript
baseUrl: '/',  // Apex 도메인의 경우
```

## 비용

### 무료 플랜 제한
- 100GB 대역폭/월
- 100GB 빌드 시간/월
- 무제한 배포
- 무제한 커스텀 도메인

**FluxLoop 문서 사이트는 무료 플랜으로 충분합니다!**

## 다음 단계

배포 완료 후:

1. **Algolia 검색 설정** (선택사항)
   - [DocSearch 신청](https://docsearch.algolia.com/apply/)
   - 무료로 문서 사이트 검색 제공

2. **Analytics 설정**
   - Vercel Analytics 활성화
   - 또는 Google Analytics 추가

3. **SEO 최적화**
   - `sitemap.xml` 자동 생성됨
   - Google Search Console 등록

4. **모니터링**
   - Vercel 대시보드에서 성능 확인
   - 빌드 시간 모니터링

---

**축하합니다!** 🎉 

FluxLoop 문서 사이트가 `https://docs.fluxloop.ai`에서 라이브되었습니다!

