import React from 'react';
import type { LearningProviderType } from '@pragya/types';

interface ProviderBadgeProps {
  provider: LearningProviderType | string;
  sourceMode?: 'MOCK' | 'LIVE' | string;
  size?: 'sm' | 'md' | 'lg';
  showMockIndicator?: boolean;
}

export function ProviderBadge({
  provider,
  sourceMode = 'MOCK',
  size = 'md',
  showMockIndicator = true,
}: ProviderBadgeProps) {
  const norm = (provider || '').toUpperCase();

  const getStyle = () => {
    switch (norm) {
      case 'IGOT':
        return {
          container: 'bg-amber-500/15 text-amber-300 border-amber-500/40 shadow-sm shadow-amber-950/20',
          dot: 'bg-amber-400',
          label: 'iGOT Karmayogi',
          tag: sourceMode === 'MOCK' ? 'MOCK' : 'LIVE',
        };
      case 'NSSTA_TPAC':
      case 'NSSTA':
        return {
          container: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/40 shadow-sm shadow-indigo-950/20',
          dot: 'bg-indigo-400',
          label: 'NSSTA / TPAC',
          tag: sourceMode === 'MOCK' ? 'MOCK' : 'LIVE',
        };
      case 'PRAGYA':
        return {
          container: 'bg-teal-500/15 text-teal-300 border-teal-500/40 shadow-sm shadow-teal-950/20',
          dot: 'bg-teal-400',
          label: 'PRAGYA Labs',
          tag: 'INTERNAL',
        };
      default:
        return {
          container: 'bg-slate-700/30 text-slate-300 border-slate-600/40',
          dot: 'bg-slate-400',
          label: provider,
          tag: sourceMode,
        };
    }
  };

  const style = getStyle();

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-2',
    lg: 'text-sm px-3 py-1.5 gap-2.5',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-md border tracking-wide select-none ${sizeClasses[size]} ${style.container}`}
      title={`${style.label} (${style.tag} Integration)`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot} shrink-0 animate-pulse`} />
      <span>{style.label}</span>
      {showMockIndicator && (
        <span
          className={`text-[9px] font-bold uppercase tracking-wider px-1 py-0.2 rounded border ${
            style.tag === 'MOCK'
              ? 'bg-amber-950/60 text-amber-300/90 border-amber-700/40'
              : 'bg-teal-950/60 text-teal-300/90 border-teal-700/40'
          }`}
        >
          {style.tag}
        </span>
      )}
    </span>
  );
}
