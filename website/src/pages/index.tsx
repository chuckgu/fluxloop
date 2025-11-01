import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <p className={styles.heroDescription}>
          Stop guessing, start simulating. Test your AI agents rigorously with reproducible, 
          offline-first experiments before shipping to production.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/">
            Get Started 🚀
          </Link>
          <Link
            className="button button--outline button--lg"
            to="https://github.com/chuckgu/fluxloop"
            style={{marginLeft: '1rem'}}>
            View on GitHub
          </Link>
        </div>
        <div className={styles.codeExample}>
          <pre>
            <code>
{`pip install fluxloop-cli fluxloop
fluxloop init project --name my-agent
fluxloop run experiment`}
            </code>
          </pre>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title} - AI Agent Simulation & Testing`}
      description="Open-source toolkit for running reproducible, offline-first simulations of AI agents. Test agent behavior, evaluate performance, and build confidence before production.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
