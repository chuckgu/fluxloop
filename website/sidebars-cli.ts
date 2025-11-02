import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  cliSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'CLI Overview',
    },
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/project-setup',
        'getting-started/first-experiment',
      ],
    },
    {
      type: 'category',
      label: 'Commands',
      items: [
        'commands/init',
        'commands/generate',
        'commands/run',
        'commands/parse',
        'commands/record',
        'commands/config',
        'commands/status',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/project-config',
        'configuration/input-config',
        'configuration/simulation-config',
        'configuration/runner-targets',
        'configuration/evaluation-config',
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/basic-workflow',
        'workflows/recording-workflow',
        'workflows/ci-cd-integration',
      ],
    },
  ],
};

export default sidebars;

