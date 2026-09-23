'use client';

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

export interface GlassCardProps extends HTMLMotionProps<'div'> {
  variant?: 'default' | 'elevated' | 'glow' | 'interactive';
  children: React.ReactNode;
}

export function GlassCard({
  variant = 'default',
  className = '',
  children,
  ...props
}: GlassCardProps) {
  const variantStyles = {
    default: 'glass-panel',
    elevated: 'glass-panel-elevated',
    glow: 'glass-panel-glow',
    interactive:
      'glass-panel hover:border-cyan-500/40 hover:bg-[#0B1021]/90 transition-all duration-200 cursor-pointer active:scale-[0.99]',
  };

  return (
    <motion.div
      className={`p-5 text-left relative overflow-hidden ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
}
