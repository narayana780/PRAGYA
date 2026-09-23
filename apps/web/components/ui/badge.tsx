'use client';

import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'success' | 'warning' | 'danger' | 'gradient';
  size?: 'sm' | 'md';
}

export function Badge({ className = '', variant = 'primary', size = 'md', children, ...props }: BadgeProps) {
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-0.5 text-xs',
  };

  const variantStyles = {
    primary: 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30',
    secondary: 'bg-slate-800 text-slate-300 border border-white/10',
    outline: 'border border-slate-700 text-slate-300',
    success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
    warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
    danger: 'bg-red-500/10 text-red-400 border border-red-500/30',
    gradient: 'bg-gradient-to-r from-cyan-500/20 to-violet-500/20 text-cyan-200 border border-cyan-500/40',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
