'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, History, TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react';
import { useCompetencyHistory } from '@/hooks/use-assessment';
import type { EmployeeCompetency } from '@pragya/types';

interface ScoreHistoryDrawerProps {
  employeeId?: string;
  competency: EmployeeCompetency | null;
  onClose: () => void;
}

export function ScoreHistoryDrawer({
  employeeId,
  competency,
  onClose,
}: ScoreHistoryDrawerProps) {
  const { data: historyList = [], isLoading } = useCompetencyHistory(
    employeeId,
    competency?.competency_id || null
  );

  if (!competency) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0"
        />

        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="relative w-full max-w-xl h-full bg-[#0B1120] border-l border-cyan-500/30 shadow-2xl p-6 overflow-y-auto flex flex-col justify-between"
        >
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between pb-5 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
                  <History className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-400">
                      {competency.competency_code}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                    <span>{competency.competency_name}</span>
                    <span className="text-xs text-slate-400 font-normal">— Score History</span>
                  </h2>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Current Summary */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Current Competency Score
                </span>
                <div className="text-2xl font-bold text-cyan-300 font-mono">
                  {competency.current_score.toFixed(1)}
                  <span className="text-xs text-slate-500 font-normal ml-1">/ 100</span>
                </div>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase font-mono text-slate-400 block">
                  Confidence
                </span>
                <span className="text-xs font-bold text-slate-200 px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700">
                  {competency.confidence_label} ({(competency.confidence * 100).toFixed(0)}%)
                </span>
              </div>
            </div>

            {/* History Timeline */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Recalculation Audit Log
              </h3>

              {isLoading ? (
                <div className="py-8 text-center text-xs text-slate-500">
                  Loading score history...
                </div>
              ) : historyList.length === 0 ? (
                <div className="p-6 rounded-xl bg-slate-950/40 border border-slate-800 text-center space-y-2">
                  <Clock className="w-6 h-6 text-slate-500 mx-auto" />
                  <p className="text-xs text-slate-400">
                    No prior score modification records found for this competency.
                  </p>
                </div>
              ) : (
                <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800">
                  {historyList.map((entry) => {
                    const diff = entry.previous_score !== null
                      ? entry.new_score - entry.previous_score
                      : null;
                    const isPositive = diff !== null && diff > 0;
                    const isNegative = diff !== null && diff < 0;

                    return (
                      <div key={entry.id} className="relative group">
                        {/* Dot indicator */}
                        <div
                          className={`absolute -left-6 top-1.5 w-4 h-4 rounded-full border-2 bg-slate-950 flex items-center justify-center transition-colors ${
                            isPositive
                              ? 'border-emerald-500 text-emerald-400'
                              : isNegative
                              ? 'border-rose-500 text-rose-400'
                              : 'border-cyan-500 text-cyan-400'
                          }`}
                        >
                          <div
                            className={`w-1.5 h-1.5 rounded-full ${
                              isPositive
                                ? 'bg-emerald-400'
                                : isNegative
                                ? 'bg-rose-400'
                                : 'bg-cyan-400'
                            }`}
                          />
                        </div>

                        <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 group-hover:border-slate-700 transition-all space-y-2">
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <p className="text-xs font-semibold text-slate-200">
                                {entry.change_reason}
                              </p>
                              <span className="text-[10px] font-mono text-slate-500">
                                {new Date(entry.created_at).toLocaleString(undefined, {
                                  dateStyle: 'medium',
                                  timeStyle: 'short',
                                })}
                              </span>
                            </div>

                            {/* Score comparison pill */}
                            <div className="text-right">
                              <div className="flex items-center gap-1.5 font-mono text-xs">
                                {entry.previous_score !== null && (
                                  <>
                                    <span className="text-slate-500">
                                      {entry.previous_score.toFixed(1)}
                                    </span>
                                    <span className="text-slate-600">→</span>
                                  </>
                                )}
                                <span className="font-bold text-slate-100">
                                  {entry.new_score.toFixed(1)}
                                </span>
                              </div>

                              {diff !== null && (
                                <div
                                  className={`text-[10px] font-mono font-bold flex items-center justify-end gap-0.5 mt-0.5 ${
                                    isPositive
                                      ? 'text-emerald-400'
                                      : isNegative
                                      ? 'text-rose-400'
                                      : 'text-slate-500'
                                  }`}
                                >
                                  {isPositive && <TrendingUp className="w-3 h-3" />}
                                  {isNegative && <TrendingDown className="w-3 h-3" />}
                                  {diff === 0 && <Minus className="w-3 h-3" />}
                                  <span>
                                    {isPositive ? '+' : ''}
                                    {diff.toFixed(1)}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Confidence change info */}
                          <div className="pt-2 border-t border-slate-900/80 flex items-center justify-between text-[11px] text-slate-400">
                            <span>Confidence:</span>
                            <span className="font-mono text-slate-300">
                              {entry.previous_confidence !== null && (
                                <>
                                  {(entry.previous_confidence * 100).toFixed(0)}% →{' '}
                                </>
                              )}
                              {(entry.new_confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
            >
              Close History
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
