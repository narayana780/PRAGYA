'use client';

import React from 'react';
import { GlassCard } from './glass-card';

export interface MetricCardProps {
  label: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  subtitle?: string;
  className?: string;
}

export function MetricCard({
  label,
  value,
  change,
  trend = 'neutral',
  icon,
  subtitle,
  className = '',
}: MetricCardProps) {
  const trendColor = {
    up: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    down: 'text-red-400 bg-red-500/10 border-red-500/20',
    neutral: 'text-slate-400 bg-slate-800 border-white/5',
  };

  return (
    <GlassCard variant="default" className={`flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400">{label}</span>
        {icon && <div className="p-2 rounded-lg bg-white/5 text-cyan-400">{icon}</div>}
      </div>

      <div className="space-y-1">
        <div className="text-2xl md:text-3xl font-bold tracking-tight text-white font-sans">
          {value}
        </div>
        {(change || subtitle) && (
          <div className="flex items-center gap-2 text-xs">
            {change && (
              <span className={`px-1.5 py-0.5 rounded border text-[11px] font-medium ${trendColor[trend]}`}>
                {change}
              </span>
            )}
            {subtitle && <span className="text-slate-400 text-[11px]">{subtitle}</span>}
          </div>
        )}
      </div>
    </GlassCard>
  );
}
