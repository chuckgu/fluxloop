# FluxLoop Documentation Website

This directory contains the FluxLoop documentation website built with [Docusaurus](https://docusaurus.io/).

## Structure

```
website/
├── docs/                    # Main documentation (getting started, guides)
├── docs-sdk/                # SDK documentation (v0.1.3)
├── docs-cli/                # CLI documentation (v0.2.1)
├── blog/                    # Release notes and tutorials
├── src/
│   ├── components/          # React components
│   ├── css/                 # Custom styles
│   └── pages/               # Landing page and custom pages
├── static/
│   └── img/                 # Images and assets
├── docusaurus.config.ts     # Main configuration
├── sidebars.ts              # Main docs sidebar
├── sidebars-sdk.ts          # SDK sidebar
└── sidebars-cli.ts          # CLI sidebar
```

## Development

### Prerequisites

- Node.js >= 18.0
- npm

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm start
```

This starts a local development server at `http://localhost:3000` with live reload.

### Build

```bash
npm run build
```

This generates static content into the `build` directory that can be served by any static hosting service.

### Serve Built Site

```bash
npm run serve
```

Test the production build locally.

## Documentation Sections

### Main Docs (`/docs`)

Getting started guides, core concepts, and general documentation.

### SDK (`/sdk`)

Python SDK documentation for agent instrumentation.
- Current version: 0.1.3
- Source: `packages/sdk/`
- Requires: Python 3.11+

### CLI (`/cli`)

CLI tool documentation for project management and experiments.
- Current version: 0.2.1
- Source: `packages/cli/`
- Guides include the new Pytest Bridge walkthrough (`docs-cli/guides/pytest-bridge.md`) plus the accompanying CI workflow (`examples/ci/fluxloop_pytest.yml`) referenced throughout the site.

## Deployment

### GitHub Pages

```bash
npm run deploy
```

### Manual Deployment

Build and serve the `build/` directory:

```bash
npm run build
# Upload build/ directory to your hosting provider
```

## Configuration

Edit `docusaurus.config.ts` to:
- Update site metadata (title, URL, etc.)
- Configure navbar and footer
- Add plugins
- Enable features (search, i18n, etc.)

## Versioning

Documentation versioning is configured in `docusaurus.config.ts`. To create a new version snapshot:

```bash
# For SDK docs
npm run docusaurus docs:version:sdk 0.2.0

# For CLI docs
npm run docusaurus docs:version:cli 0.3.0
```

## Internationalization

The site supports English and Korean. To add translations:

```bash
npm run write-translations -- --locale ko
```

Edit generated JSON files in `i18n/ko/` directory.

## Contributing

When adding new documentation:

1. Choose the appropriate section (docs, docs-sdk, docs-cli)
2. Create Markdown files with frontmatter:
   ```markdown
   ---
   sidebar_position: 1
   title: Page Title
   ---
   # Content
   ```
3. Update the corresponding sidebar file if needed
4. Test locally with `npm start`
5. Submit a pull request

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Markdown Features](https://docusaurus.io/docs/markdown-features)

---

**Built with ❤️ using Docusaurus**
