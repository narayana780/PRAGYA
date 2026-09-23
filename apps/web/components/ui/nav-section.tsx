'use client';

import React from 'react';

export interface NavSectionProps {
  title?: string;
  collapsed?: boolean;
  children: React.ReactNode;
}

export function NavSection({ title, collapsed = false, children }: NavSectionProps) {
  return (
    <div className="space-y-1 py-1">
      {title && !collapsed && (
        <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
          {title}
        </div>
      )}
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}
