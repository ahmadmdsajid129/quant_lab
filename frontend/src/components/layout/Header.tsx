'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bell, Search, Terminal } from 'lucide-react';

export const Header: React.FC = () => {
  const pathname = usePathname();

  const getBreadcrumb = () => {
    if (pathname === '/') return 'Dashboard';
    const clean = pathname.replace('/', '');
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  };

  return (
    <header className="h-12 border-b border-border-subtle bg-surface px-6 flex items-center justify-between shrink-0 sticky top-0 z-10 select-none">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-mono">
        <span className="text-text-muted">QuantLab</span>
        <span className="text-text-muted">/</span>
        <span className="text-text-primary font-semibold">{getBreadcrumb()}</span>
      </div>

      {/* Center Quick Search Button */}
      <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded bg-surface-elevated border border-border-strong text-xs text-text-muted cursor-pointer hover:border-accent transition-colors">
        <Search className="w-3.5 h-3.5" />
        <span>Search artifacts & symbols...</span>
        <kbd className="text-[10px] font-mono bg-border-subtle px-1.5 py-0.5 rounded text-text-secondary ml-4">
          Ctrl K
        </kbd>
      </div>

      {/* Right Telemetry Controls */}
      <div className="flex items-center gap-3">
        <Link
          href="/jobs"
          className="flex items-center gap-2 text-xs font-mono px-2 py-1 rounded bg-surface-elevated border border-border-strong hover:border-accent transition-colors text-text-secondary hover:text-text-primary"
        >
          <Terminal className="w-3.5 h-3.5 text-accent" />
          <span>Workers (Idle)</span>
        </Link>
        <button className="p-1.5 rounded text-text-secondary hover:text-text-primary hover:bg-surface-elevated transition-colors">
          <Bell className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
