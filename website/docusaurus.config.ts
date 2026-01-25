import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'FluxLoop',
  tagline: 'Simulate, Evaluate, and Trust Your AI Agents',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://fluxloop.ai',  // 또는 'https://docs.fluxloop.ai'
  baseUrl: '/',  // Apex/서브도메인 모두 /

  organizationName: 'chuckgu',
  projectName: 'fluxloop',
  
  // Vercel 배포 설정
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ko'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/chuckgu/fluxloop/tree/main/website/',
          routeBasePath: 'docs',
          path: 'docs',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl: 'https://github.com/chuckgu/fluxloop/tree/main/website/',
          blogTitle: 'FluxLoop Blog',
          blogDescription: 'Release notes, tutorials, and updates',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'sdk',
        path: 'docs-sdk',
        routeBasePath: 'sdk',
        sidebarPath: './sidebars-sdk.ts',
        editUrl: 'https://github.com/chuckgu/fluxloop/tree/main/website/',
      },
    ],
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'cli',
        path: 'docs-cli',
        routeBasePath: 'cli',
        sidebarPath: './sidebars-cli.ts',
        editUrl: 'https://github.com/chuckgu/fluxloop/tree/main/website/',
      },
    ],
  ],

  themeConfig: {
    image: 'img/logo.png',
    colorMode: {
      respectPrefersColorScheme: true,
      defaultMode: 'light',
    },
    navbar: {
      title: 'FluxLoop',
      logo: {
        alt: 'FluxLoop Logo',
        src: 'img/logo.png',
        srcDark: 'img/logo.png',
        width: 32,
        height: 32,
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/sdk/',
          label: 'SDK',
          position: 'left',
        },
        {
          to: '/cli/',
          label: 'CLI',
          position: 'left',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left'
        },
        {
          type: 'localeDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/chuckgu/fluxloop',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/',
            },
            {
              label: 'SDK',
              to: '/sdk/',
            },
            {
              label: 'CLI',
              to: '/cli/',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Discussions',
              href: 'https://github.com/chuckgu/fluxloop/discussions',
            },
            {
              label: 'GitHub Issues',
              href: 'https://github.com/chuckgu/fluxloop/issues',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/chuckgu/fluxloop',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} FluxLoop. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'typescript', 'yaml', 'json'],
    },
    algolia: {
      // Algolia search integration (optional, can be added later)
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'fluxloop',
      contextualSearch: true,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
