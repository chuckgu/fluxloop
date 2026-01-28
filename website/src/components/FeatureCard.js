import React from 'react';
import Link from '@docusaurus/Link';

export default function FeatureCard({title, description, icon, to}) {
  return (
    <Link to={to} className="feature-card">
      <div className="icon-wrapper">
        {icon}
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
    </Link>
  );
}

export function CardGrid({children}) {
  return (
    <div className="card-grid">
      {children}
    </div>
  );
}
