'use client';

import React from 'react';
import { Calendar, ShieldCheck } from 'lucide-react';
import { GlassCard } from './glass-card';
import { Badge } from './badge';

export interface EvidenceCardProps {
  title: string;
  sourceType: 'Diagnostic' | 'Recent Assessment' | 'Verified Training' | 'Experience' | 'Self Assessment';
  date: string;
  weight: number;
  scoreContribution?: string;
  className?: string;
}

export function EvidenceCard({
  title,
  sourceType,
  date,
  weight,
  scoreContribution,
  className = '',
}: EvidenceCardProps) {
  const typeVariants: Record<string, 'primary' | 'secondary' | 'success' | 'warning' | 'outline'> = {
    'Diagnostic': 'primary',
    'Recent Assessment': 'success',
    'Verified Training': 'warning',
    'Experience': 'secondary',
    'Self Assessment': 'outline',
  };

  return (
    <GlassCard variant="default" className={`flex flex-col justify-between gap-3 ${className}`}>
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <Badge variant={typeVariants[sourceType] || 'primary'}>{sourceType}</Badge>
          <span className="text-[11px] font-mono text-cyan-400 font-semibold">{weight}% Weight</span>
        </div>

        <h4 className="text-sm font-medium text-white">{title}</h4>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-500" />
            {date}
          </span>
          {scoreContribution && (
            <span className="flex items-center gap-1 text-slate-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Impact: {scoreContribution}
            </span>
          )}
        </div>
      </div>
    </GlassCard>
  );
}
