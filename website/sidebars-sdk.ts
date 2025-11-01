import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  sdkSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'SDK Overview',
    },
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/basic-usage',
        'getting-started/async-support',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/client-config',
        'configuration/storage-backends',
        'configuration/environment-variables',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/decorators',
        'api/client',
        'api/context',
        'api/models',
      ],
    },
    {
      type: 'category',
      label: 'Framework Integration',
      items: [
        'frameworks/langchain',
        'frameworks/langgraph',
        'frameworks/custom',
      ],
    },
  ],
};

export default sidebars;

