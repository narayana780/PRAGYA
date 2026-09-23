'use client';

import React, { forwardRef } from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className = '', label, error, helperText, id, disabled, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full text-left">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-medium text-slate-300 mb-1.5">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          disabled={disabled}
          className={`w-full rounded-lg bg-[#0B1021]/80 border ${
            error ? 'border-red-500/80 focus:border-red-500' : 'border-white/10 focus:border-cyan-400'
          } p-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 ${
            error ? 'focus:ring-red-500' : 'focus:ring-cyan-400'
          } disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 resize-y min-h-[90px] ${className}`}
          {...props}
        />
        {error ? (
          <p className="mt-1 text-xs text-red-400">{error}</p>
        ) : helperText ? (
          <p className="mt-1 text-xs text-slate-400">{helperText}</p>
        ) : null}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
