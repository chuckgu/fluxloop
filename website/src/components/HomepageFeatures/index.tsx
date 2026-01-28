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
    title: 'Synthetic Testing at Scale',
    icon: '🎭',
    description: (
      <>
        Generate persona-based synthetic inputs. Run hundreds of scenarios automatically. Interact with agents like real users.
      </>
    ),
  },
  {
    title: 'Seamless Claude Code Integration',
    icon: '🔗',
    description: (
      <>
        Test instantly with /fluxloop commands. View results right in your IDE. Validate without breaking your workflow.
      </>
    ),
  },
  {
    title: 'Cloud-Powered Analysis',
    icon: '📊',
    description: (
      <>
        Visualize results on the web platform. Share test data with your team. Track agent performance over time.
      </>
    ),
  },
  {
    title: 'Python-First SDK',
    icon: '🐍',
    description: (
      <>
        Simple instrumentation with @agent and @trace decorators. Native support for LangChain and LangGraph. Seamless pytest integration.
      </>
    ),
  },
];

function Feature({title, icon, description}: FeatureItem) {
  return (
    <div className={clsx('col col--3')}>
      <div className="text--center padding-horiz--md">
        <div className={styles.featureIcon} style={{fontSize: '3rem', marginBottom: '1rem'}}>{icon}</div>
        <Heading as="h3">{title}</Heading>
        <p style={{fontSize: '1.1rem'}}>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
