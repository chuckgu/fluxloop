import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/core-concepts',
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'guides/local-testing-workflow',
        'guides/virtual-environment-setup',
      ],
    },
    {
      type: 'category',
      label: 'Web Platform',
      items: [
        'platform/platform-overview',
        'platform/projects-and-scenarios',
        'platform/viewing-results',
        'platform/api-keys',
      ],
    },
    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/custom-storage',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/configuration',
        'reference/json-contract',
        'reference/artifacts',
      ],
    },
  ],
};

export default sidebars;
