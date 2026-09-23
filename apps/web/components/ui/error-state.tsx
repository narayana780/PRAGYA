'use client';

import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from './button';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = 'Service Interruption',
  message = 'Unable to complete statistical service request. Please check your connectivity and retry.',
  onRetry,
  className = '',
}: ErrorStateProps) {
  return (
    <div className={`p-8 rounded-2xl bg-red-950/20 border border-red-500/20 text-center flex flex-col items-center justify-center max-w-md mx-auto ${className}`}>
      <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-center justify-center mb-4">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-white tracking-tight mb-1">{title}</h3>
      <p className="text-xs text-slate-400 leading-relaxed max-w-xs mb-5">{message}</p>
      {onRetry && (
        <Button variant="danger" size="sm" onClick={onRetry} className="gap-2">
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Retry Operation</span>
        </Button>
      )}
    </div>
  );
}
