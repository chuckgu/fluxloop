import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Welcome',
    },
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/core-concepts',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/end-to-end-workflow',
        'guides/ai-assistant-integration-guide',
        'guides/virtual-environment-setup',
      ],
    },
    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/argument-replay',
        'advanced/recording-mode',
        'advanced/custom-storage',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/configuration',
        'reference/artifacts',
        'reference/json-contract',
      ],
    },
  ],
};

export default sidebars;
