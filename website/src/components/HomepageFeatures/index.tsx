import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  icon: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: '🎯 Simple Decorator-Based Setup',
    icon: '🎯',
    description: (
      <>
        Instrument existing agent code with minimal changes—just add <code>@fluxloop.agent()</code> and you're tracing.
        Works with any Python framework or custom agent implementation.
      </>
    ),
  },
  {
    title: '🔄 Argument Replay System',
    icon: '🔄',
    description: (
      <>
        Record complex function arguments (WebSocket callbacks, session data, etc.) from staging, 
        then replay them locally with different content. No manual mocking required.
      </>
    ),
  },
  {
    title: '🧪 Offline-First Simulation',
    icon: '🧪',
    description: (
      <>
        Run experiments on your machine without cloud dependencies. Generate structured artifacts 
        that work with any evaluation backend.
      </>
    ),
  },
  {
    title: '📊 Structured JSON Output',
    icon: '📊',
    description: (
      <>
        Every simulation produces reproducible, auditable artifacts: summary stats, per-trace records, 
        detailed execution traces, and observation streams.
      </>
    ),
  },
  {
    title: '🚀 CLI Orchestration',
    icon: '🚀',
    description: (
      <>
        Define complex experiments in YAML, generate input variations with LLM, and run batch 
        simulations—all from the command line.
      </>
    ),
  },
  {
    title: '🔌 VSCode Extension',
    icon: '🔌',
    description: (
      <>
        Manage projects, generate inputs, run experiments, and explore results—all from your IDE 
        with visual project management and configuration editing.
      </>
    ),
  },
];

function Feature({title, icon, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <div className={styles.featureIcon}>{icon}</div>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="text--center margin-bottom--xl">
          <Heading as="h2">Why FluxLoop?</Heading>
          <p className={styles.subtitle}>
            Building trustworthy AI requires systematic testing and evaluation. 
            FluxLoop provides the foundational tooling.
          </p>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
