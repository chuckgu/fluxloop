import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  claudeCodeSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/first-test',
      ],
    },
    {
      type: 'category',
      label: 'Skills Reference',
      items: [
        'commands/setup',
        'commands/test',
        'commands/status',
        'commands/criteria',
        'commands/pull',
        'commands/apikeys',
      ],
    },
    {
      type: 'category',
      label: 'Integration',
      items: [
        'integration/workflow',
        'integration/best-practices',
      ],
    },
  ],
};

export default sidebars;
