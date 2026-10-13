'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import {
  Activity,
  BarChart3,
  BookOpen,
  BrainCircuit,
  Cpu,
  FileText,
  Layers,
  LayoutDashboard,
  LineChart,
  PieChart,
  ShieldAlert,
  Terminal,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { useAppStore } from '@/lib/store';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const activeWorkspace = useAppStore((state) => state.activeWorkspace);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Research Projects', href: '/projects', icon: BookOpen },
    { name: 'Market Data & QA', href: '/data', icon: LineChart },
    { name: 'Exploratory Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Strategy Backtester', href: '/backtests', icon: TrendingUp },
    { name: 'Statistical Validation', href: '/validation', icon: Activity },
    { name: 'Machine Learning Lab', href: '/ml', icon: BrainCircuit },
    { name: 'Portfolio & Risk', href: '/portfolio', icon: PieChart },
    { name: 'Microstructure & LOB', href: '/microstructure', icon: Layers },
    { name: 'Options & Derivatives', href: '/options', icon: Cpu },
    { name: 'AI Research Copilot', href: '/copilot', icon: Zap },
    { name: 'Paper Trading', href: '/paper-trading', icon: Terminal },
    { name: 'Research Reports', href: '/reports', icon: FileText },
    { name: 'Job Telemetry', href: '/jobs', icon: ShieldAlert },
  ];

  return (
    <aside className="w-60 bg-surface border-r border-border-subtle flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none">
      <div>
        {/* Brand & Workspace Header */}
        <div className="p-4 border-b border-border-subtle">
          <Link href="/" className="flex items-center gap-2.5 mb-3">
            <div className="w-7 h-7 rounded bg-accent/20 border border-accent flex items-center justify-center text-accent font-bold font-mono text-xs">
              QL
            </div>
            <span className="font-bold text-sm tracking-tight text-text-primary">
              QuantLab
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-accent/15 text-accent ml-auto">
              PRO
            </span>
          </Link>

          {/* Active Workspace Selector */}
          <div className="bg-surface-elevated px-2.5 py-1.5 rounded border border-border-strong flex items-center justify-between text-xs">
            <span className="text-text-secondary truncate max-w-[150px]">
              {activeWorkspace?.name || 'Default Workspace'}
            </span>
            <span className="text-[10px] text-text-muted font-mono uppercase">
              {activeWorkspace?.role || 'LOCAL'}
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-2 space-y-0.5 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(
                  'flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors',
                  isActive
                    ? 'bg-accent/15 text-accent border border-accent/30 font-semibold'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated'
                )}
              >
                <Icon className={clsx('w-4 h-4', isActive ? 'text-accent' : 'text-text-muted')} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-border-subtle bg-surface-elevated/40">
        <div className="flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-financial-profit inline-block animate-pulse" />
            ENGINE OK
          </span>
          <span>v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};
