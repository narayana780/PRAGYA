'use client';

import React from 'react';
import { motion } from 'framer-motion';

export interface SkillBarProps {
  skillName: string;
  currentScore: number;  // 0 to 100
  requiredLevel: number; // 0 to 100
  domain?: string;
  className?: string;
}

export function SkillBar({
  skillName,
  currentScore,
  requiredLevel,
  domain,
  className = '',
}: SkillBarProps) {
  const gap = Math.max(0, requiredLevel - currentScore);

  return (
    <div className={`space-y-1.5 p-3 rounded-lg bg-[#070A13]/60 border border-white/5 ${className}`}>
      <div className="flex items-center justify-between text-xs">
        <div>
          <span className="font-semibold text-slate-200">{skillName}</span>
          {domain && <span className="ml-2 text-[10px] text-slate-500 font-mono">({domain})</span>}
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-cyan-400">Score: {currentScore}</span>
          <span className="text-slate-500">/</span>
          <span className="text-violet-400">Req: {requiredLevel}</span>
        </div>
      </div>

      {/* Overlaid track showing current score and required level */}
      <div className="relative h-2 rounded-full bg-slate-900 overflow-hidden">
        {/* Required Level target marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-violet-400 z-10 shadow-[0_0_8px_#8B5CF6]"
          style={{ left: `${requiredLevel}%` }}
          title={`Target: ${requiredLevel}`}
        />
        {/* Current Score fill */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${currentScore}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 shadow-[0_0_8px_rgba(6,182,212,0.4)]"
        />
      </div>

      {gap > 0 && (
        <div className="text-right">
          <span className="text-[10px] font-mono text-amber-400 font-medium">
            Gap: {gap} pts
          </span>
        </div>
      )}
    </div>
  );
}
