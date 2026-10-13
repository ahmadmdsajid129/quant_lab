import React from 'react';
import { clsx } from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, helperText, className, ...props }) => {
  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-text-secondary">{label}</label>}
      <input
        className={clsx(
          'w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border transition-colors focus:outline-none focus:ring-1 focus:ring-accent placeholder:text-text-muted',
          error ? 'border-financial-loss' : 'border-border-strong focus:border-accent',
          className
        )}
        {...props}
      />
      {error && <span className="text-[11px] text-financial-loss">{error}</span>}
      {helperText && !error && <span className="text-[11px] text-text-muted">{helperText}</span>}
    </div>
  );
};
