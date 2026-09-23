'use client';

import React from 'react';

export interface TimelineItem {
  id: string;
  title: string;
  description?: string;
  timestamp: string;
  status?: 'completed' | 'current' | 'upcoming';
}

export interface TimelineProps {
  items: TimelineItem[];
  className?: string;
}

export function Timeline({ items, className = '' }: TimelineProps) {
  return (
    <div className={`space-y-4 text-left ${className}`}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        const isCompleted = item.status === 'completed';
        const isCurrent = item.status === 'current';

        return (
          <div key={item.id} className="relative flex items-start gap-3">
            {!isLast && (
              <div
                className={`absolute left-[11px] top-6 bottom-0 w-0.5 ${
                  isCompleted ? 'bg-cyan-500/40' : 'bg-slate-800'
                }`}
              />
            )}
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 z-10 ${
                isCompleted
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                  : isCurrent
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-400 shadow-[0_0_10px_#8B5CF6]'
                  : 'bg-slate-800 text-slate-500 border border-white/5'
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full ${
                  isCompleted ? 'bg-cyan-400' : isCurrent ? 'bg-violet-400 animate-pulse' : 'bg-slate-600'
                }`}
              />
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center justify-between gap-2">
                <h4 className={`text-xs font-semibold ${isCurrent ? 'text-cyan-300' : 'text-slate-200'}`}>
                  {item.title}
                </h4>
                <span className="text-[10px] font-mono text-slate-500">{item.timestamp}</span>
              </div>
              {item.description && (
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{item.description}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
