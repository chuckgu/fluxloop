import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import ProductShowcase from '@site/src/components/ProductShowcase';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          Build, Test, and Ship AI Agents with Confidence
        </Heading>
        <p className="hero__subtitle">AI agent testing platform that starts right from Claude Code</p>
        <p className={styles.heroDescription}>
          Simulate your agents with synthetic data and ship with confidence.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/getting-started/quick-start">
            Get Started with Claude Code 🚀
          </Link>
          <Link
            className="button button--outline button--lg"
            to="/docs/platform/platform-overview">
            Explore Web Platform
          </Link>
          <Link
            className="button button--outline button--lg"
            to="/docs">
            Read Docs
          </Link>
        </div>
        <div className={styles.codeExample}>
          <div className={styles.codeLabel}>Quick Install (Claude Code)</div>
          <pre>
            <code>
{`/fluxloop setup`}
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
      title={`${siteConfig.title} - AI Agent Testing Platform`}
      description="Build, test, and ship AI agents with confidence. Claude Code integration, synthetic testing at scale, and cloud-powered analysis.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <ProductShowcase />
      </main>
    </Layout>
  );
}
