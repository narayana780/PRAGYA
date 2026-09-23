'use client';

import React from 'react';

export interface LegendItem {
  label: string;
  color: string;
  value?: string | number;
}

export interface ChartLegendProps {
  items: LegendItem[];
  className?: string;
}

export function ChartLegend({ items, className = '' }: ChartLegendProps) {
  return (
    <div className={`flex flex-wrap items-center gap-4 text-xs ${className}`}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          <span
            className="w-2.5 h-2.5 rounded-full shrink-0 shadow-sm"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-slate-300 font-medium">{item.label}</span>
          {item.value !== undefined && (
            <span className="font-mono text-slate-400 font-semibold">{item.value}</span>
          )}
        </div>
      ))}
    </div>
  );
}
