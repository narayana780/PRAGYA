'use client';

import React from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Target,
  Sparkles,
  Calculator,
  Clock,
  CheckCircle,
  AlertTriangle,
  BrainCircuit,
  FlaskConical,
} from 'lucide-react';
import { GapPriorityBadge } from './gap-priority-badge';
import { CurrentVsRequiredBar } from './current-vs-required-bar';
import type { SkillGap } from '@pragya/types';

interface GapDetailDrawerProps {
  gap: SkillGap | null;
  onClose: () => void;
}

export function GapDetailDrawer({ gap, onClose }: GapDetailDrawerProps) {
  if (!gap) return null;

  const isNoGap = gap.gap_score <= 0;
  const isLowConfidence = gap.confidence_flag === 'LOW_CONFIDENCE';

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
        {/* Backdrop click to close */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0"
          onClick={onClose}
        />

        {/* Drawer content */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 28, stiffness: 280 }}
          className="relative w-full max-w-2xl h-full bg-slate-950 border-l border-slate-800 shadow-2xl overflow-y-auto flex flex-col z-10"
        >
          {/* Drawer Header */}
          <div className="sticky top-0 z-20 bg-slate-950/90 backdrop-blur-md border-b border-slate-800 p-6 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {gap.domain_name}
                </span>
                <span className="text-xs font-mono text-slate-500">
                  {gap.competency_code}
                </span>
              </div>
              <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
                {gap.competency_name}
                <GapPriorityBadge priority={gap.priority_level} size="md" />
              </h2>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-900 text-slate-400 hover:text-slate-100 hover:bg-slate-800 border border-slate-800 transition"
              aria-label="Close drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="p-6 space-y-6 flex-1">
            {/* Low Confidence Advisory Banner */}
            {isLowConfidence && (
              <div className="bg-amber-950/30 border border-amber-500/40 rounded-xl p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="text-sm font-semibold text-amber-300">
                    Potential Gap — Low Confidence Rating
                  </div>
                  <p className="text-xs text-amber-200/80 leading-relaxed">
                    Current evidence is sparse or preliminary (confidence:{' '}
                    {(gap.confidence * 100).toFixed(0)}%). More empirical evidence or formal
                    assessment is recommended before finalizing significant training commitments.
                  </p>
                </div>
              </div>
            )}

            {/* No Gap Success Banner */}
            {isNoGap && (
              <div className="bg-emerald-950/30 border border-emerald-500/40 rounded-xl p-4 flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="text-sm font-semibold text-emerald-300">
                    Role Requirement Fully Satisfied
                  </div>
                  <p className="text-xs text-emerald-200/80 leading-relaxed">
                    Demonstrated competency meets or exceeds role requirements. No immediate
                    remedial training required.
                  </p>
                </div>
              </div>
            )}

            {/* Current vs Required Visual */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Target className="w-3.5 h-3.5 text-cyan-400" />
                Score Comparison
              </h3>
              <CurrentVsRequiredBar
                currentScore={gap.current_score}
                requiredScore={gap.required_score}
                currentLevelName={gap.current_level_name}
                requiredLevelName={gap.required_level_name}
                gapScore={gap.gap_score}
              />
            </div>

            {/* Why This Gap Matters (Explainable Narrative) */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                Why This Gap Matters
              </h3>
              <p className="text-sm text-slate-200 leading-relaxed">
                {gap.explanation}
              </p>
              {gap.role_relevance && (
                <div className="pt-2 border-t border-slate-800/80 text-xs text-slate-400 flex items-start gap-2">
                  <span className="font-semibold text-slate-300">Role Context:</span>
                  <span>{gap.role_relevance}</span>
                </div>
              )}
            </div>

            {/* Deterministic Priority Score Calculation Breakdown */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Calculator className="w-3.5 h-3.5 text-cyan-400" />
                  Priority Calculation Breakdown
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 font-mono">Priority Score:</span>
                  <span className="text-base font-bold font-mono text-cyan-300">
                    {gap.priority_score.toFixed(2)}
                  </span>
                  <span className="text-xs text-slate-500">/ 100</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="grid grid-cols-12 text-[11px] font-semibold text-slate-400 uppercase tracking-wider pb-1 border-b border-slate-800">
                  <div className="col-span-4">Factor</div>
                  <div className="col-span-3 text-right">Value / Weight</div>
                  <div className="col-span-5 text-right">Points Added</div>
                </div>

                {/* Gap Magnitude */}
                <div className="grid grid-cols-12 text-xs py-1.5 border-b border-slate-800/50 items-center">
                  <div className="col-span-4 font-medium text-slate-300">Gap Magnitude</div>
                  <div className="col-span-3 text-right font-mono text-slate-400">
                    {gap.gap_score} pts (40%)
                  </div>
                  <div className="col-span-5 text-right font-mono font-bold text-cyan-400">
                    +{gap.priority_breakdown.gap_component.toFixed(2)}
                  </div>
                </div>

                {/* Role Criticality */}
                <div className="grid grid-cols-12 text-xs py-1.5 border-b border-slate-800/50 items-center">
                  <div className="col-span-4 font-medium text-slate-300">Role Criticality</div>
                  <div className="col-span-3 text-right font-mono text-slate-400">
                    {gap.criticality} (25%)
                  </div>
                  <div className="col-span-5 text-right font-mono font-bold text-cyan-400">
                    +{gap.priority_breakdown.criticality_component.toFixed(2)}
                  </div>
                </div>

                {/* Task Relevance */}
                <div className="grid grid-cols-12 text-xs py-1.5 border-b border-slate-800/50 items-center">
                  <div className="col-span-4 font-medium text-slate-300">Task Relevance</div>
                  <div className="col-span-3 text-right font-mono text-slate-400">
                    {gap.task_relevance} (15%)
                  </div>
                  <div className="col-span-5 text-right font-mono font-bold text-cyan-400">
                    +{gap.priority_breakdown.task_relevance_component.toFixed(2)}
                  </div>
                </div>

                {/* Mission Urgency */}
                <div className="grid grid-cols-12 text-xs py-1.5 border-b border-slate-800/50 items-center">
                  <div className="col-span-4 font-medium text-slate-300">Mission Urgency</div>
                  <div className="col-span-3 text-right font-mono text-slate-400">
                    {gap.mission_urgency} (10%)
                  </div>
                  <div className="col-span-5 text-right font-mono font-bold text-cyan-400">
                    +{gap.priority_breakdown.mission_urgency_component.toFixed(2)}
                  </div>
                </div>

                {/* Confidence */}
                <div className="grid grid-cols-12 text-xs py-1.5 border-b border-slate-800/50 items-center">
                  <div className="col-span-4 font-medium text-slate-300">Confidence Factor</div>
                  <div className="col-span-3 text-right font-mono text-slate-400">
                    {(gap.confidence * 100).toFixed(0)}% (10%)
                  </div>
                  <div className="col-span-5 text-right font-mono font-bold text-cyan-400">
                    +{gap.priority_breakdown.confidence_component.toFixed(2)}
                  </div>
                </div>

                {/* Total Priority Score Row */}
                <div className="grid grid-cols-12 text-sm pt-2 items-center">
                  <div className="col-span-7 font-bold text-slate-200">
                    Total Weighted Priority Score:
                  </div>
                  <div className="col-span-5 text-right font-mono font-extrabold text-amber-300 text-base">
                    {gap.priority_score.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>

            {/* Context & Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3 space-y-1">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">
                  Criticality
                </span>
                <div className="text-sm font-semibold text-slate-200">
                  {gap.criticality}
                </div>
              </div>

              <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3 space-y-1">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">
                  Task Relevance
                </span>
                <div className="text-sm font-semibold text-slate-200">
                  {gap.task_relevance}
                </div>
              </div>

              <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3 space-y-1">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">
                  Mission Urgency
                </span>
                <div className="text-sm font-semibold text-slate-200">
                  {gap.mission_urgency}
                </div>
              </div>

              <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3 space-y-1">
                <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">
                  Confidence
                </span>
                <div className="text-sm font-semibold text-slate-200">
                  {(gap.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Calculation Timestamp */}
            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-900">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                Calculated:{' '}
                {new Date(gap.calculated_at).toLocaleString('en-IN', {
                  dateStyle: 'medium',
                  timeStyle: 'short',
                })}
              </span>
              <span className="italic text-[11px]">
                Deterministic Gap Intelligence
              </span>
            </div>

            {/* Stage 7: Recommended Learning CTA & Stage 11: Reassess CTA */}
            <div className="pt-3 border-t border-slate-900 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
              <Link
                href={`/employee/labs?competencyId=${gap.competency_id}`}
                className="px-3.5 py-1.5 rounded-xl bg-violet-600/20 hover:bg-violet-600/30 border border-violet-500/30 text-violet-300 font-semibold text-xs flex items-center justify-center gap-1.5 transition"
              >
                <FlaskConical className="w-3.5 h-3.5 text-violet-400" />
                <span>Practice in Lab</span>
              </Link>
              <Link
                href={`/employee/adaptive-assessment?competencyId=${gap.competency_id}`}
                className="px-3.5 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 text-cyan-300 font-semibold text-xs flex items-center justify-center gap-1.5 transition"
              >
                <BrainCircuit className="w-3.5 h-3.5 text-cyan-400" />
                <span>Reassess this skill</span>
              </Link>
              {!isNoGap && (
                <Link
                  href="/employee/learning"
                  className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-indigo-950/40 transition"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  <span>Learning</span>
                </Link>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
