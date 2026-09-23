'use client';

import React from 'react';
import { motion } from 'framer-motion';

export interface ProgressBarProps {
  value: number; // 0 to 100
  label?: string;
  showValue?: boolean;
  color?: 'cyan' | 'violet' | 'emerald' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ProgressBar({
  value,
  label,
  showValue = false,
  color = 'cyan',
  size = 'md',
  className = '',
}: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value));

  const sizeStyles = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3.5',
  };

  const colorStyles = {
    cyan: 'bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.4)]',
    violet: 'bg-violet-500 shadow-[0_0_10px_rgba(139,92,246,0.4)]',
    emerald: 'bg-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.4)]',
    gradient: 'bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500 shadow-[0_0_12px_rgba(6,182,212,0.4)]',
  };

  return (
    <div className={`w-full space-y-1.5 ${className}`}>
      {(label || showValue) && (
        <div className="flex items-center justify-between text-xs">
          {label && <span className="font-medium text-slate-300">{label}</span>}
          {showValue && <span className="font-mono text-cyan-400 font-semibold">{clampedValue}%</span>}
        </div>
      )}
      <div className={`w-full bg-[#070A13] border border-white/5 rounded-full overflow-hidden ${sizeStyles[size]}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${clampedValue}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className={`h-full rounded-full ${colorStyles[color]}`}
        />
      </div>
    </div>
  );
}
