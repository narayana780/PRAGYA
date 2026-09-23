import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Info, ShieldAlert } from 'lucide-react';
import type { PriorityLevel } from '@pragya/types';

interface GapPriorityBadgeProps {
  priority: PriorityLevel | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export function GapPriorityBadge({
  priority,
  size = 'md',
  showIcon = true,
}: GapPriorityBadgeProps) {
  const normPriority = (priority || '').toUpperCase();

  const getStyle = () => {
    switch (normPriority) {
      case 'CRITICAL':
        return {
          container: 'bg-rose-500/15 text-rose-300 border-rose-500/40 shadow-sm shadow-rose-950/40',
          icon: <ShieldAlert className="w-3.5 h-3.5 text-rose-400 shrink-0" />,
          label: 'CRITICAL',
        };
      case 'HIGH':
        return {
          container: 'bg-amber-500/15 text-amber-300 border-amber-500/40 shadow-sm shadow-amber-950/40',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />,
          label: 'HIGH',
        };
      case 'MEDIUM':
        return {
          container: 'bg-sky-500/15 text-sky-300 border-sky-500/40 shadow-sm shadow-sky-950/40',
          icon: <Info className="w-3.5 h-3.5 text-sky-400 shrink-0" />,
          label: 'MEDIUM',
        };
      case 'LOW':
        return {
          container: 'bg-slate-500/15 text-slate-300 border-slate-500/40 shadow-sm shadow-slate-950/40',
          icon: <AlertCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />,
          label: 'LOW',
        };
      case 'NO_GAP':
        return {
          container: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40 shadow-sm shadow-emerald-950/40',
          icon: <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />,
          label: 'NO GAP',
        };
      default:
        return {
          container: 'bg-slate-800 text-slate-400 border-slate-700',
          icon: null,
          label: normPriority || 'UNKNOWN',
        };
    }
  };

  const style = getStyle();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border tracking-wide uppercase ${style.container} ${sizeClasses}`}
    >
      {showIcon && style.icon}
      <span>{style.label}</span>
    </span>
  );
}
