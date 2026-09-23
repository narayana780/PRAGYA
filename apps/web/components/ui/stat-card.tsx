'use client';

import React from 'react';
import { GlassCard } from './glass-card';

export interface StatCardProps {
  title: string;
  metric: string | number;
  description?: string;
  badge?: React.ReactNode;
  icon?: React.ReactNode;
  accentColor?: 'cyan' | 'violet' | 'emerald' | 'amber';
  className?: string;
}

export function StatCard({
  title,
  metric,
  description,
  badge,
  icon,
  accentColor = 'cyan',
  className = '',
}: StatCardProps) {
  const accentGlow = {
    cyan: 'border-cyan-500/20 hover:border-cyan-500/40',
    violet: 'border-violet-500/20 hover:border-violet-500/40',
    emerald: 'border-emerald-500/20 hover:border-emerald-500/40',
    amber: 'border-amber-500/20 hover:border-amber-500/40',
  };

  return (
    <GlassCard variant="default" className={`border ${accentGlow[accentColor]} ${className}`}>
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-medium text-slate-400">{title}</span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>

      <div className="flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold tracking-tight text-white font-sans">{metric}</div>
        {badge}
      </div>

      {description && <p className="text-[11px] text-slate-400 mt-2">{description}</p>}
    </GlassCard>
  );
}
