import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type ProductItem = {
  title: string;
  subtitle: string;
  icon: string;
  example: string;
  link: string;
};

const ProductList: ProductItem[] = [
  {
    title: 'Claude Code Plugin',
    subtitle: 'Run tests instantly with skills',
    icon: '⚡',
    example: '/fluxloop test',
    link: '/docs/getting-started/quick-start',
  },
  {
    title: 'CLI Tool',
    subtitle: 'Local command-line interface',
    icon: '⌨️',
    example: 'fluxloop test',
    link: '/cli',
  },
  {
    title: 'Web Platform',
    subtitle: 'Cloud dashboard for results',
    icon: '☁️',
    example: 'results.fluxloop.ai',
    link: '/docs/platform/platform-overview',
  },
];

function Product({title, subtitle, icon, example, link}: ProductItem) {
  return (
    <div className={clsx('col col--4')}>
      <Link to={link} className={styles.productCard}>
        <div className={styles.productIcon}>{icon}</div>
        <Heading as="h3" className={styles.productTitle}>{title}</Heading>
        <p className={styles.productSubtitle}>{subtitle}</p>
        <div className={styles.productExample}>
          <code>{example}</code>
        </div>
      </Link>
    </div>
  );
}

export default function ProductShowcase(): ReactNode {
  return (
    <section className={styles.showcase}>
      <div className="container">
        <div className="text--center margin-bottom--lg">
          <Heading as="h2">Three Ways to Use FluxLoop</Heading>
          <p className={styles.showcaseSubtitle}>
            Choose the workflow that fits your development process
          </p>
        </div>
        <div className="row">
          {ProductList.map((props, idx) => (
            <Product key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
