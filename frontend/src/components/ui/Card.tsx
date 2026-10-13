import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  elevated?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, elevated = false, className, ...props }) => {
  return (
    <div
      className={clsx(
        'rounded-lg border transition-all duration-150',
        elevated
          ? 'bg-surface-elevated border-border-strong shadow-lg shadow-black/20'
          : 'bg-surface border-border-subtle hover:border-border-strong',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className,
  ...props
}) => (
  <div className={clsx('p-4 border-b border-border-subtle flex items-center justify-between', className)} {...props}>
    {children}
  </div>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className,
  ...props
}) => <div className={clsx('p-4', className)} {...props}>{children}</div>;
