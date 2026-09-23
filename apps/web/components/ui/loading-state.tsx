'use client';

import React from 'react';

export interface LoadingStateProps {
  message?: string;
  subMessage?: string;
  className?: string;
}

export function LoadingState({
  message = 'Processing intelligence data...',
  subMessage,
  className = '',
}: LoadingStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center ${className}`}>
      <div className="relative mb-4">
        <div className="w-12 h-12 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 rounded-full bg-cyan-400/20 blur-sm" />
        </div>
      </div>
      <h4 className="text-sm font-semibold text-slate-200">{message}</h4>
      {subMessage && <p className="text-xs text-slate-400 mt-1 max-w-sm">{subMessage}</p>}
    </div>
  );
}
