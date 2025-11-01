# FluxLoop Documentation Deployment Guide

## Quick Start

```bash
# Build the site
npm run build

# Test locally
npm run serve

# Deploy (see options below)
```

## Deployment Options

### Option 1: GitHub Pages

1. Update `docusaurus.config.ts`:
   ```typescript
   url: 'https://your-username.github.io',
   baseUrl: '/fluxloop/',
   organizationName: 'your-username',
   projectName: 'fluxloop',
   ```

2. Deploy:
   ```bash
   npm run deploy
   ```

This builds the site and pushes to the `gh-pages` branch.

### Option 2: Netlify

1. Connect your repository to Netlify
2. Build command: `npm run build`
3. Publish directory: `build`
4. Deploy

### Option 3: Vercel

1. Connect your repository to Vercel
2. Build command: `npm run build`
3. Output directory: `build`
4. Deploy

### Option 4: Custom Server

1. Build the site:
   ```bash
   npm run build
   ```

2. Upload `build/` directory to your server

3. Configure web server (nginx example):
   ```nginx
   server {
       listen 80;
       server_name docs.fluxloop.dev;
       root /var/www/fluxloop-docs/build;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

## Environment Variables

No environment variables required for build.

For algolia search (optional):
- `ALGOLIA_APP_ID`
- `ALGOLIA_API_KEY`
- `ALGOLIA_INDEX_NAME`

## Version Management

To create a new version snapshot:

```bash
# SDK version
npm run docusaurus docs:version:sdk 0.2.0

# CLI version
npm run docusaurus docs:version:cli 0.3.0

# VSCode version
npm run docusaurus docs:version:vscode 0.2.0
```

This creates a snapshot in `versioned_docs/` and updates `versions.json`.

## Continuous Deployment

### GitHub Actions Example

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
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
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./website/build
```

## Troubleshooting

### Build Fails

1. Clear cache: `npm run clear`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check Node version: `node --version` (should be >= 18.0)

### Broken Links

Run build to check for broken links:
```bash
npm run build
```

Docusaurus will report all broken links during build.

### TypeDoc API Generation

To regenerate VSCode Extension API docs:

```bash
npm run generate-api-docs
```

Currently disabled in docusaurus.config.ts. Enable the plugin to activate.

## Production Checklist

Before deploying to production:

- [ ] Update `docusaurus.config.ts` with correct URL and base path
- [ ] Test build locally: `npm run build && npm run serve`
- [ ] Check all navigation links work
- [ ] Verify search functionality (if enabled)
- [ ] Test on mobile devices
- [ ] Check all 3 documentation sections (SDK, CLI, VSCode)
- [ ] Verify blog posts if any
- [ ] Test i18n if Korean locale is needed

## Monitoring

After deployment:

- Check site loads correctly
- Test all main navigation links
- Verify search works (if algolia is configured)
- Check mobile responsiveness
- Monitor build times

---

Need help? Check [Docusaurus Deployment Docs](https://docusaurus.io/docs/deployment) or open an issue.

