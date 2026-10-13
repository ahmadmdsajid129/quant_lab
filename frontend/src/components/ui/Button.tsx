import React from 'react';
import { clsx } from 'clsx';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className,
  disabled,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-md transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed';

  const sizeStyles = {
    sm: 'text-xs px-2.5 py-1.5 h-7',
    md: 'text-xs px-3.5 py-2 h-9',
    lg: 'text-sm px-4 py-2.5 h-10',
  };

  const variantStyles = {
    primary:
      'bg-accent hover:bg-accent-hover text-background font-semibold shadow-sm active:scale-[0.98]',
    secondary:
      'bg-surface-elevated hover:bg-border-strong text-text-primary border border-border-strong',
    destructive:
      'bg-financial-loss/15 hover:bg-financial-loss/25 text-financial-loss border border-financial-loss/30',
    outline:
      'bg-transparent hover:bg-surface-elevated text-text-primary border border-border-strong',
    ghost: 'bg-transparent hover:bg-surface-elevated text-text-secondary hover:text-text-primary',
  };

  return (
    <button
      className={clsx(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <span className="w-3.5 h-3.5 mr-2 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
};
