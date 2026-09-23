'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

export interface InsightCardProps {
  title: string;
  explanation: string;
  sourceContext?: string;
  tag?: string;
  className?: string;
}

export function InsightCard({
  title,
  explanation,
  sourceContext,
  tag = 'AI Intelligence',
  className = '',
}: InsightCardProps) {
  return (
    <div className={`p-4 rounded-xl bg-gradient-to-br from-violet-950/30 to-indigo-950/30 border border-violet-500/20 backdrop-blur-md text-left ${className}`}>
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 text-xs text-violet-300 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>{tag}</span>
        </div>
      </div>

      <h4 className="text-sm font-semibold text-slate-100 mb-1">{title}</h4>
      <p className="text-xs text-slate-300 leading-relaxed">{explanation}</p>

      {sourceContext && (
        <div className="mt-3 pt-2.5 border-t border-white/5 text-[11px] font-mono text-slate-400 flex items-center gap-1">
          <span className="text-cyan-400">Context:</span>
          <span>{sourceContext}</span>
        </div>
      )}
    </div>
  );
}
