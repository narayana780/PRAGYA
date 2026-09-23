'use client';

import React from 'react';

export interface AIStatusIndicatorProps {
  status?: 'ready' | 'retrieving' | 'generating' | 'calibrating';
  label?: string;
  className?: string;
}

export function AIStatusIndicator({ status = 'ready', label, className = '' }: AIStatusIndicatorProps) {
  const configs = {
    ready: {
      text: label || 'AI Assistant Ready',
      color: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
      dot: 'bg-cyan-400',
    },
    retrieving: {
      text: label || 'Retrieving Official Evidence...',
      color: 'text-violet-300 bg-violet-500/10 border-violet-500/30',
      dot: 'bg-violet-400 animate-ping',
    },
    generating: {
      text: label || 'Synthesizing Explanation...',
      color: 'text-fuchsia-300 bg-fuchsia-500/10 border-fuchsia-500/30',
      dot: 'bg-fuchsia-400 animate-pulse',
    },
    calibrating: {
      text: label || 'Recalibrating Competency Nodes...',
      color: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
      dot: 'bg-emerald-400 animate-pulse',
    },
  };

  const config = configs[status];

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${config.color} ${className}`}>
      <span className="relative flex h-2 w-2">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${config.dot}`} />
        <span className={`relative inline-flex rounded-full h-2 w-2 ${config.dot}`} />
      </span>
      <span className="font-mono text-[11px]">{config.text}</span>
    </div>
  );
}
