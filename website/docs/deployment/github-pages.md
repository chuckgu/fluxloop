---
sidebar_position: 1
---

# GitHub Pages 배포

FluxLoop 문서를 GitHub Pages로 무료 호스팅하세요.

## 준비사항

1. GitHub 계정
2. FluxLoop 저장소
3. Node.js 18 이상

## 설정 방법

### 1. docusaurus.config.ts 업데이트

GitHub Pages 설정을 추가하세요:

```typescript
const config: Config = {
  url: 'https://your-username.github.io',
  baseUrl: '/fluxloop/',  // 저장소 이름
  organizationName: 'your-username',
  projectName: 'fluxloop',
  
  // GitHub Pages 배포 설정
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
};
```

### 2. package.json 스크립트 확인

이미 배포 스크립트가 포함되어 있습니다:

```json
{
  "scripts": {
    "deploy": "docusaurus deploy"
  }
}
```

### 3. Git 설정

GitHub 원격 저장소를 추가하세요:

```bash
cd /Users/user/Documents/fluxloop
git remote add origin https://github.com/your-username/fluxloop.git
```

### 4. 배포 실행

```bash
cd website
npm run deploy
```

이 명령은:
1. 사이트를 빌드합니다
2. `gh-pages` 브랜치를 생성/업데이트합니다
3. GitHub에 푸시합니다

### 5. GitHub Pages 활성화

1. GitHub 저장소로 이동
2. **Settings** → **Pages**
3. Source: `gh-pages` 브랜치 선택
4. **Save** 클릭

약 1-2분 후 사이트가 `https://your-username.github.io/fluxloop/`에서 접근 가능합니다.

## 사용자 정의 도메인

### 도메인 설정

1. 도메인 제공업체에서 CNAME 레코드 추가:
   ```
   CNAME  docs  your-username.github.io
   ```

2. `static/CNAME` 파일 생성:
   ```
   docs.fluxloop.dev
   ```

3. `docusaurus.config.ts` 업데이트:
   ```typescript
   url: 'https://docs.fluxloop.dev',
   baseUrl: '/',
   ```

4. 재배포:
   ```bash
   npm run deploy
   ```

5. GitHub Settings → Pages에서 Custom domain 입력

## 문제 해결

### 404 오류

`baseUrl`이 저장소 이름과 일치하는지 확인:
```typescript
baseUrl: '/fluxloop/',  // /로 시작하고 끝나야 함
```

### CSS/JS 파일 로딩 실패

`url`과 `baseUrl`이 올바른지 확인:
```typescript
url: 'https://your-username.github.io',
baseUrl: '/fluxloop/',
```

### 배포 권한 오류

GitHub Personal Access Token 설정:
```bash
export GIT_USER=your-username
export GIT_PASS=your-personal-access-token
npm run deploy
```

## 자동 배포 (CI/CD)

GitHub Actions로 자동 배포를 설정하려면 [CI/CD 가이드](./cicd)를 참조하세요.

## 장점과 단점

### ✅ 장점
- 무료 호스팅
- GitHub과 통합
- 자동 HTTPS
- 사용자 정의 도메인 지원

### ❌ 단점
- 빌드 시간 제한 (10분)
- 대역폭 제한 (월 100GB)
- Public 저장소만 무료

## 다음 단계

- [Netlify 배포](./netlify) - 더 빠른 배포
- [Vercel 배포](./vercel) - 최고의 성능
- [CI/CD 설정](./cicd) - 자동화된 배포

