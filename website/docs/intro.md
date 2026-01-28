---
sidebar_position: 1
slug: /
---

import FeatureCard, {CardGrid} from '@site/src/components/FeatureCard';

# Welcome to FluxLoop

> Build, Test, and Ship AI Agents with Confidence

FluxLoop is a cloud-powered platform for testing AI agents at scale with synthetic data. From rapid prototyping in Claude Code to team-wide testing in the cloud, FluxLoop helps you validate agent behavior before shipping to production.

:::info
To create a new account or login to your existing one, visit your [dashboard](https://app.fluxloop.ai).
:::

## Documentation

FluxLoop offers a suite of tools to help you build and test robust AI agents. You can find the documentation for each component in the following sections.

<CardGrid>
  <FeatureCard 
    title="Claude Code Plugin" 
    description="Test agents directly in your IDE. Perfect for rapid iteration." 
    icon="⚡" 
    to="/claude-code/"
  />
  <FeatureCard 
    title="CLI Tool" 
    description="Local testing and automation for CI/CD pipelines." 
    icon="🖥️" 
    to="/cli/"
  />
  <FeatureCard 
    title="Python SDK" 
    description="Instrument your agents with powerful decorators." 
    icon="📦" 
    to="/sdk/"
  />
  <FeatureCard 
    title="Web Platform" 
    description="Cloud-powered analysis, visualization, and collaboration." 
    icon="☁️" 
    to="/platform/platform-overview"
  />
</CardGrid>

## Core Concepts

Understand what makes FluxLoop unique.

<CardGrid>
  <FeatureCard 
    title="Synthetic Personas" 
    description="Generate realistic test scenarios using diverse user archetypes." 
    icon="🎭" 
    to="/getting-started/core-concepts#persona"
  />
  <FeatureCard 
    title="Framework Agnostic" 
    description="Works with LangChain, LangGraph, or any Python code." 
    icon="🔌" 
    to="/getting-started/core-concepts#framework-agnostic"
  />
</CardGrid>

:::tip Can't find what you're looking for?
Check our [Github Discussions](https://github.com/chuckgu/fluxloop/discussions) or [Issues](https://github.com/chuckgu/fluxloop/issues).
:::
