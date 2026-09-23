import React from 'react';
import { Check } from 'lucide-react';

interface CurrentVsRequiredBarProps {
  currentScore: number;
  requiredScore: number;
  currentLevelName?: string | null;
  requiredLevelName?: string | null;
  gapScore: number;
  compact?: boolean;
}

export function CurrentVsRequiredBar({
  currentScore,
  requiredScore,
  currentLevelName,
  requiredLevelName,
  gapScore,
  compact = false,
}: CurrentVsRequiredBarProps) {
  const currentPct = Math.min(Math.max(currentScore, 0), 100);
  const requiredPct = Math.min(Math.max(requiredScore, 0), 100);
  const isSatisfied = gapScore <= 0;

  if (compact) {
    return (
      <div className="w-full space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 font-mono">
            Current: <span className="text-cyan-300 font-semibold">{currentScore}</span>
          </span>
          <span className="text-slate-400 font-mono">
            Req: <span className="text-violet-300 font-semibold">{requiredScore}</span>
          </span>
        </div>
        <div className="relative h-2 w-full bg-slate-800 rounded-full overflow-hidden">
          {/* Deficit / Target background indicator */}
          <div
            className="absolute top-0 bottom-0 bg-violet-500/20"
            style={{ width: `${requiredPct}%` }}
          />
          {/* Current Score Bar */}
          <div
            className={`absolute top-0 bottom-0 rounded-full transition-all duration-500 ${
              isSatisfied
                ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                : 'bg-gradient-to-r from-cyan-500 to-blue-500'
            }`}
            style={{ width: `${currentPct}%` }}
          />
          {/* Required Marker Pin */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-violet-400 shadow-sm"
            style={{ left: `${requiredPct}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5 space-y-2.5">
      {/* Metrics Row */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
          <span className="text-slate-300 font-medium">Current Demonstrated:</span>
          <span className="font-mono font-bold text-cyan-300 text-sm">
            {currentScore} <span className="text-slate-500 font-normal text-xs">/ 100</span>
          </span>
          {currentLevelName && (
            <span className="text-[11px] px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">
              Lvl {currentLevelName}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-violet-400" />
          <span className="text-slate-300 font-medium">Role Required:</span>
          <span className="font-mono font-bold text-violet-300 text-sm">
            {requiredScore} <span className="text-slate-500 font-normal text-xs">/ 100</span>
          </span>
          {requiredLevelName && (
            <span className="text-[11px] px-2 py-0.5 rounded bg-violet-950/60 text-violet-400 border border-violet-800/40">
              Lvl {requiredLevelName}
            </span>
          )}
        </div>
      </div>

      {/* Visual Dual Progress Track */}
      <div className="relative h-3 w-full bg-slate-800/90 rounded-full overflow-hidden">
        {/* Required Zone */}
        <div
          className="absolute top-0 bottom-0 bg-violet-500/15 border-r border-violet-500/40"
          style={{ width: `${requiredPct}%` }}
          title={`Required score: ${requiredScore}`}
        />

        {/* Current Score Progress Fill */}
        <div
          className={`absolute top-0 bottom-0 rounded-full transition-all duration-500 ${
            isSatisfied
              ? 'bg-gradient-to-r from-emerald-500 to-teal-400 shadow-md shadow-emerald-500/20'
              : 'bg-gradient-to-r from-cyan-500 to-blue-500 shadow-md shadow-cyan-500/20'
          }`}
          style={{ width: `${currentPct}%` }}
        />

        {/* Required Vertical Marker */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-violet-300 z-10 -ml-0.5 shadow-sm"
          style={{ left: `${requiredPct}%` }}
        />
      </div>

      {/* Footer Status Row */}
      <div className="flex items-center justify-between text-[11px] pt-0.5">
        <span className="text-slate-500">0</span>
        <div className="flex items-center gap-1.5">
          {isSatisfied ? (
            <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
              <Check className="w-3.5 h-3.5" />
              Role requirement met (0 gap)
            </span>
          ) : (
            <span className="font-mono text-amber-400 font-semibold">
              Gap: {gapScore} pts
            </span>
          )}
        </div>
        <span className="text-slate-500">100</span>
      </div>
    </div>
  );
}
