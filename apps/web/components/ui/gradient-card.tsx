'use client';

import React from 'react';

export interface GradientCardProps extends React.HTMLAttributes<HTMLDivElement> {
  gradient?: 'cyan-violet' | 'violet-magenta' | 'emerald-cyan' | 'purple-coral';
  children: React.ReactNode;
}

export function GradientCard({
  gradient = 'cyan-violet',
  className = '',
  children,
  ...props
}: GradientCardProps) {
  const borderGradients = {
    'cyan-violet': 'from-cyan-500/50 to-violet-500/50',
    'violet-magenta': 'from-violet-500/50 to-fuchsia-500/50',
    'emerald-cyan': 'from-emerald-500/50 to-cyan-500/50',
    'purple-coral': 'from-violet-500/50 to-orange-500/50',
  };

  return (
    <div
      className={`relative p-[1px] rounded-xl bg-gradient-to-r ${borderGradients[gradient]} overflow-hidden ${className}`}
      {...props}
    >
      <div className="rounded-[11px] bg-[#0B1021]/95 backdrop-blur-xl p-5 text-left h-full">
        {children}
      </div>
    </div>
  );
}
