'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export interface ShellProps {
  children: React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({ children }) => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-text-primary">
      <Sidebar />
      <div className="flex flex-col flex-1 h-screen overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
};
