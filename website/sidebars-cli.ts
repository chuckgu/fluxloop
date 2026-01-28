import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  cliSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/authentication',
        'getting-started/first-test',
      ],
    },
    {
      type: 'category',
      label: 'Core Commands',
      collapsed: false,
      items: [
        {
          type: 'category',
          label: 'Project Management',
          items: [
            'commands/init',
            'commands/status',
            'commands/config',
          ],
        },
        {
          type: 'category',
          label: 'Authentication & Sync',
          items: [
            'commands/auth',
            'commands/projects',
            'commands/scenarios',
            'commands/apikeys',
            'commands/sync',
          ],
        },
        {
          type: 'category',
          label: 'Testing Workflow',
          items: [
            'commands/generate',
            'commands/test',
            'commands/criteria',
          ],
        },
        {
          type: 'category',
          label: 'Input Generation',
          items: [
            'commands/personas',
            'commands/inputs',
            'commands/bundles',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/project-config',
        'configuration/input-config',
        'configuration/runner-targets',
        {
          type: 'category',
          label: 'Runner Types',
          items: [
            'configuration/runners/python-function',
            'configuration/runners/http-sse',
            'configuration/runners/subprocess-jsonl',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/basic-workflow',
        'workflows/multi-turn-workflow',
        'workflows/pytest-integration',
        'workflows/ci-cd-integration',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/command-reference',
        'reference/exit-codes',
      ],
    },
  ],
};

export default sidebars;
