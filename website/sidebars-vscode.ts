import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  vscodeSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'VSCode Extension',
    },
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/creating-first-project',
        'getting-started/running-experiments',
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: [
        'user-guide/creating-projects',
        'user-guide/managing-inputs',
        'user-guide/running-experiments',
        'user-guide/viewing-results',
        'user-guide/recording-mode',
      ],
    },
    {
      type: 'category',
      label: 'Commands',
      items: [
        'commands/project-commands',
        'commands/workflow-commands',
        'commands/recording-commands',
      ],
    },
    {
      type: 'category',
      label: 'Integration Assistant',
      items: [
        'integration-assistant/overview',
        'integration-assistant/setup',
        'integration-assistant/knowledge-search',
        'integration-assistant/flux-agent',
        'integration-assistant/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'Views',
      items: [
        'views/projects-view',
        'views/inputs-view',
        'views/experiments-view',
        'views/results-view',
        'views/status-view',
        'views/integration-view',
      ],
    },
    {
      type: 'doc',
      id: 'troubleshooting',
      label: 'Troubleshooting',
    },
  ],
};

export default sidebars;

