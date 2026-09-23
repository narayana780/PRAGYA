'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

export interface AIActionChipProps {
  label: string;
  onClick?: () => void;
  icon?: React.ReactNode;
  className?: string;
}

export function AIActionChip({ label, onClick, icon, className = '' }: AIActionChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-slate-300 bg-white/5 hover:bg-cyan-500/15 hover:text-cyan-200 border border-white/10 hover:border-cyan-500/30 transition-all duration-150 cursor-pointer select-none active:scale-[0.98] ${className}`}
    >
      {icon || <Sparkles className="w-3 h-3 text-cyan-400" />}
      <span>{label}</span>
    </button>
  );
}
