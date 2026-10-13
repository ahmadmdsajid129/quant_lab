import React from 'react';
import { clsx } from 'clsx';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'neutral' | 'accent' | 'profit' | 'loss' | 'warning' | 'info';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center font-mono font-medium rounded';

  const sizeStyles = {
    sm: 'text-[10px] px-1.5 py-0.5 leading-none',
    md: 'text-xs px-2 py-0.5',
  };

  const variantStyles = {
    neutral: 'bg-border-subtle text-text-secondary border border-border-strong',
    accent: 'bg-accent/15 text-accent border border-accent/30',
    profit: 'bg-financial-profitMuted text-financial-profit border border-financial-profit/30',
    loss: 'bg-financial-lossMuted text-financial-loss border border-financial-loss/30',
    warning: 'bg-financial-warning/15 text-financial-warning border border-financial-warning/30',
    info: 'bg-financial-info/15 text-financial-info border border-financial-info/30',
  };

  return (
    <span className={clsx(baseStyles, sizeStyles[size], variantStyles[variant], className)} {...props}>
      {children}
    </span>
  );
};
