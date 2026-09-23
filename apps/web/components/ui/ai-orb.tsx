'use client';

import React from 'react';
import { motion } from 'framer-motion';

export interface AIOrbProps {
  size?: 'sm' | 'md' | 'lg';
  isThinking?: boolean;
  className?: string;
}

export function AIOrb({ size = 'md', isThinking = false, className = '' }: AIOrbProps) {
  const pixelSizes = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  };

  const orbGlows = {
    sm: 'blur-md',
    md: 'blur-lg',
    lg: 'blur-xl',
  };

  return (
    <div className={`relative flex items-center justify-center shrink-0 ${pixelSizes[size]} ${className}`}>
      {/* Outer ambient glow halo */}
      <motion.div
        animate={
          isThinking
            ? { scale: [1, 1.3, 1], opacity: [0.4, 0.8, 0.4] }
            : { scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3] }
        }
        transition={{
          repeat: Infinity,
          duration: isThinking ? 1.5 : 3.5,
          ease: 'easeInOut',
        }}
        className={`absolute inset-0 rounded-full bg-gradient-to-r from-cyan-400 via-violet-500 to-fuchsia-500 ${orbGlows[size]}`}
      />

      {/* Rotating core gradient */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: isThinking ? 4 : 12, ease: 'linear' }}
        className="w-full h-full rounded-full bg-gradient-to-tr from-cyan-500 via-violet-600 to-fuchsia-500 p-[1.5px] shadow-lg"
      >
        <div className="w-full h-full rounded-full bg-[#070A13] flex items-center justify-center overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/30 to-violet-600/30 backdrop-blur-sm" />
          {/* Inner luminous nucleus */}
          <div className="w-2.5 h-2.5 rounded-full bg-white shadow-[0_0_10px_#FFFFFF] relative z-10" />
        </div>
      </motion.div>
    </div>
  );
}
