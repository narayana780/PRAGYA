'use client';

import React from 'react';

export interface StatusBadgeProps {
  status: 'active' | 'completed' | 'in-progress' | 'pending' | 'critical' | 'verified';
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className = '' }: StatusBadgeProps) {
  const configs = {
    active: {
      color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      dot: 'bg-emerald-400 shadow-[0_0_6px_#10B981]',
      text: label || 'Active',
    },
    completed: {
      color: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30',
      dot: 'bg-cyan-400 shadow-[0_0_6px_#06B6D4]',
      text: label || 'Completed',
    },
    'in-progress': {
      color: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
      dot: 'bg-blue-400 shadow-[0_0_6px_#3B82F6]',
      text: label || 'In Progress',
    },
    pending: {
      color: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
      dot: 'bg-amber-400 shadow-[0_0_6px_#F59E0B]',
      text: label || 'Pending Review',
    },
    critical: {
      color: 'bg-red-500/10 text-red-400 border-red-500/30',
      dot: 'bg-red-400 shadow-[0_0_6px_#EF4444]',
      text: label || 'High Priority Gap',
    },
    verified: {
      color: 'bg-violet-500/10 text-violet-300 border-violet-500/30',
      dot: 'bg-violet-400 shadow-[0_0_6px_#8B5CF6]',
      text: label || 'Evidence Verified',
    },
  };

  const config = configs[status];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.color} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      <span>{config.text}</span>
    </span>
  );
}
