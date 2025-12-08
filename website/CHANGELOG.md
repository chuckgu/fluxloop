# FluxLoop Documentation Website - Changelog

## [Unreleased] - 2025-01-09

### Added
- 📦 MCP Server documentation (v0.1.0)
- 🧠 AI-assisted integration guides and repository analysis tools
- 🔧 Framework detection documentation (Express, FastAPI, Next.js, NestJS)

### Changed
- Updated SDK version to 0.1.3 (Python 3.11+ required)
- Updated CI to run tests on Python 3.11/3.12 only

## [Initial Release] - 2024-11-02

### Added
- 🎉 Initial Docusaurus documentation website
- 📚 70+ documentation pages for SDK, CLI, and VSCode Extension
- 🎨 Custom branded landing page with FluxLoop logo
- 📱 Responsive design with dark mode support
- 🔍 Multi-instance docs (separate sections for SDK/CLI/VSCode/MCP)
- 🌐 i18n support (English and Korean)
- 🚀 Vercel deployment configuration
- 🤖 GitHub Actions CI/CD pipeline
- 📖 Comprehensive guides and API references

### Changed
- Updated navigation to use absolute paths
- Improved dark mode contrast for hero section
- Replaced default Docusaurus logo with FluxLoop logo

### Documentation Sections
- **Main Docs**: Getting Started, Guides, Advanced, Reference
- **SDK (v0.1.3)**: Installation, Basic Usage, Async Support, Configuration, API (Python 3.11+)
- **CLI (v0.2.1)**: Installation, Commands, Configuration, Workflows
- **VSCode (v0.1.0)**: Installation, User Guide, Commands, Views
- **MCP (v0.1.0)**: Installation, Tools, Repository Analysis, Integration Workflows (Python 3.11+)

### Deployment
- Root Directory: `website` (in OSS repo)
- Build Command: `npm run build`
- Output Directory: `build`
- URL: https://docs.fluxloop.ai

---

## Future Plans

### Version 0.1.0 (Next)
- [ ] Add screenshots and diagrams
- [ ] Enable TypeDoc API documentation
- [ ] Add search (Algolia DocSearch)
- [ ] Add version dropdown
- [ ] Expand CLI command documentation
- [ ] Add video tutorials
- [ ] Complete Korean translations

### Version 0.2.0
- [ ] Interactive code examples
- [ ] API playground
- [ ] Performance metrics dashboard
- [ ] Community showcase
- [ ] Blog for release notes

