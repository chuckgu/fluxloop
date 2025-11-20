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
    title: 'Simulate at Scale',
    icon: '🎯',
    description: (
      <>
        Run thousands of realistic multi-turn scenarios in parallel. Find edge cases before production.
      </>
    ),
  },
  {
    title: 'Align to Your Standards',
    icon: '📊',
    description: (
      <>
        Capture your implicit decision criteria. Turn intuition into automated evaluation.
      </>
    ),
  },
  {
    title: 'Act on Insights',
    icon: '🚀',
    description: (
      <>
        Reports that show what to fix and how. Analysis that drives action.
      </>
    ),
  },
];

function Feature({title, icon, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
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
