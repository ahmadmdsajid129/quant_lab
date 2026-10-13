'use client';

import React, { useEffect, useState } from 'react';
import {
  Activity,
  BarChart3,
  BookOpen,
  BrainCircuit,
  Cpu,
  Layers,
  LineChart,
  PieChart,
  ShieldAlert,
  Terminal,
  TrendingUp,
  Zap
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';

interface SystemHealth {
  status: string;
  service: string;
  version: string;
  environment: string;
  database: string;
}

export default function DashboardPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => res.json())
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch health status:', err);
        setLoading(false);
      });
  }, []);

  const workstations = [
    {
      title: 'Research Projects & Hypotheses',
      desc: 'Formulate hypotheses, specify market mechanisms, track falsification criteria, and log research notes.',
      icon: BookOpen,
      href: '/projects',
      badge: 'Scientific Inception',
    },
    {
      title: 'Market Data & Synthetic Generator',
      desc: 'Ingest historical OHLCV data, run 5-point data quality audits, or generate jump-diffusion synthetic bars.',
      icon: LineChart,
      href: '/data',
      badge: 'Data Layer',
    },
    {
      title: 'Exploratory Data Analytics',
      desc: 'Analyze return distributions, rolling volatility, autocorrelation, and Augmented Dickey-Fuller stationarity.',
      icon: BarChart3,
      href: '/analytics',
      badge: 'Statistical EDA',
    },
    {
      title: 'Strategy & Event Backtester',
      desc: 'Simulate bar-by-bar execution with strict time semantics, next-bar open fills, commissions, and slippage.',
      icon: TrendingUp,
      href: '/backtests',
      badge: 'Execution Simulation',
    },
    {
      title: 'Statistical Validation Lab',
      desc: 'Execute walk-forward analysis, Purged K-Fold with embargo, and calculate the Deflated Sharpe Ratio (DSR).',
      icon: Activity,
      href: '/validation',
      badge: 'Bias & P-Hacking Guard',
    },
    {
      title: 'Machine Learning Laboratory',
      desc: 'Train GBDT and Ridge models on financial features with zero-leakage chronological preprocessing.',
      icon: BrainCircuit,
      href: '/ml',
      badge: 'Time-Series ML',
    },
    {
      title: 'Portfolio Optimization & Risk',
      desc: 'Mean-Variance, Equal Risk Parity, and Ledoit-Wolf shrinkage with marginal risk contribution decomposition.',
      icon: PieChart,
      href: '/portfolio',
      badge: 'Asset Allocation',
    },
    {
      title: 'Limit Order Book (LOB) Simulator',
      desc: 'Interactive double-auction matching engine with price-time priority, queue tracking, and microprice stats.',
      icon: Layers,
      href: '/microstructure',
      badge: 'Microstructure Lab',
    },
    {
      title: 'Options & Derivatives Lab',
      desc: 'Analytical Black-Scholes pricing, exact Greeks, Put-Call parity verification, and multi-leg payoff diagrams.',
      icon: Cpu,
      href: '/options',
      badge: 'Derivatives Math',
    },
    {
      title: 'AI Research Copilot',
      desc: 'Artifact-grounded research assistant providing methodology reviews and failure diagnostics without hallucinations.',
      icon: Zap,
      href: '/copilot',
      badge: 'Grounded Assistant',
    },
    {
      title: 'Paper Trading Engine',
      desc: 'Simulate live order execution, track virtual cash, margin usage, and enforce pre-trade risk controls.',
      icon: Terminal,
      href: '/paper-trading',
      badge: 'Virtual Broker',
    },
    {
      title: 'Job Observability & Telemetry',
      desc: 'Monitor background worker pool, track live compute progress percentages, and inspect task execution logs.',
      icon: ShieldAlert,
      href: '/jobs',
      badge: 'System Operations',
    },
  ];

  return (
    <Shell>
      <div className="space-y-8">
        {/* Top Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between border-b border-border-subtle pb-6 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent/20 border border-accent flex items-center justify-center text-accent font-bold font-mono">
                QL
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-text-primary">
                  QuantLab Workstation
                </h1>
                <p className="text-xs text-text-secondary">
                  Production-Oriented Quantitative Research & Experimentation Platform
                </p>
              </div>
            </div>
          </div>

        {/* System Telemetry Badge */}
        <div className="flex items-center gap-3 bg-surface-elevated px-4 py-2 rounded-md border border-border-strong text-xs font-mono">
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                health?.status === 'healthy' ? 'bg-financial-profit animate-pulse' : 'bg-financial-warning'
              }`}
            />
            <span className="text-text-secondary">Engine:</span>
            <span className="font-semibold text-text-primary">
              {loading ? 'Connecting...' : health?.status === 'healthy' ? 'Active (FastAPI)' : 'Offline / Standalone'}
            </span>
          </div>
          <span className="text-border-strong">|</span>
          <div className="text-text-secondary">
            Version: <span className="text-accent">{health?.version || '1.0.0'}</span>
          </div>
        </div>
      </header>

      {/* Hero Overview Grid */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-surface p-4 rounded-lg border border-border-subtle">
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-1">Architecture</div>
          <div className="text-xl font-bold font-mono text-accent">Decoupled</div>
          <div className="text-[11px] text-text-muted mt-1">Next.js + FastAPI + Parquet</div>
        </div>
        <div className="bg-surface p-4 rounded-lg border border-border-subtle">
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-1">Time Semantics</div>
          <div className="text-xl font-bold font-mono text-financial-profit">Zero Leakage</div>
          <div className="text-[11px] text-text-muted mt-1">Strict t+1 Open Execution</div>
        </div>
        <div className="bg-surface p-4 rounded-lg border border-border-subtle">
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-1">Validation</div>
          <div className="text-xl font-bold font-mono text-financial-info">Deflated Sharpe</div>
          <div className="text-[11px] text-text-muted mt-1">Purged K-Fold & Embargo</div>
        </div>
        <div className="bg-surface p-4 rounded-lg border border-border-subtle">
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-1">Microstructure</div>
          <div className="text-xl font-bold font-mono text-text-primary">LOB Double-Auction</div>
          <div className="text-[11px] text-text-muted mt-1">Price-Time Priority Queue</div>
        </div>
      </section>

      {/* Main Workstation Modules Grid */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-text-secondary mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-accent" /> Quantitative Workstation Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workstations.map((ws) => {
            const Icon = ws.icon;
            return (
              <a
                key={ws.title}
                href={ws.href}
                className="group bg-surface hover:bg-surface-elevated p-5 rounded-lg border border-border-subtle hover:border-accent transition-all duration-150 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-md bg-surface-elevated group-hover:bg-accent/15 text-accent transition-colors">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-border-subtle text-text-secondary group-hover:text-accent group-hover:bg-accent/10 transition-colors">
                      {ws.badge}
                    </span>
                  </div>
                  <h3 className="text-base font-semibold text-text-primary group-hover:text-accent transition-colors mb-1.5">
                    {ws.title}
                  </h3>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    {ws.desc}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-border-subtle/50 flex items-center justify-between text-xs text-text-muted group-hover:text-accent transition-colors">
                  <span>Launch Module</span>
                  <span className="font-mono">→</span>
                </div>
              </a>
            );
          })}
        </div>
      </section>
      </div>
    </Shell>
  );
}
