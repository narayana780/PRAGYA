'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Sparkles,
  Calculator,
  Target,
  Layers,
  Clock,
  BookOpen,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import Link from 'next/link';
import { ProviderBadge } from './provider-badge';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { getCourseLaunchUrl, isExternalLaunchUrl } from '@/lib/course-utils';
import type { LearningRecommendation } from '@pragya/types';

interface RecommendationExplanationDrawerProps {
  recommendation: LearningRecommendation | null;
  onClose: () => void;
  onStart?: (recId: string) => void;
}

export function RecommendationExplanationDrawer({
  recommendation,
  onClose,
  onStart,
}: RecommendationExplanationDrawerProps) {
  if (!recommendation) return null;

  const item = recommendation.learning_item;
  const reason = recommendation.structured_reason;
  const breakdown = recommendation.priority_breakdown;

  const factorItems = [
    {
      name: 'Skill Gap Priority',
      weight: '35%',
      score: breakdown.gap_priority_component,
      max: 35.0,
      icon: <Target className="w-4 h-4 text-rose-400" />,
      desc: 'Based on quantitative deficit, role criticality, task relevance & mission urgency',
    },
    {
      name: 'Competency & Semantic Match',
      weight: '25%',
      score: breakdown.semantic_match_component,
      max: 25.0,
      icon: <Zap className="w-4 h-4 text-amber-400" />,
      desc: 'Direct syllabus mapping + deterministic semantic relevance to official taxonomy',
    },
    {
      name: 'Proficiency Level Fit',
      weight: '15%',
      score: breakdown.level_fit_component,
      max: 15.0,
      icon: <Layers className="w-4 h-4 text-sky-400" />,
      desc: 'Next-step pedagogical progression from current demonstrated level',
    },
    {
      name: 'Learning Outcome Coverage',
      weight: '10%',
      score: breakdown.outcome_coverage_component,
      max: 10.0,
      icon: <BookOpen className="w-4 h-4 text-purple-400" />,
      desc: 'Depth of syllabus coverage (Working vs Introductory / Foundation)',
    },
    {
      name: 'Prerequisites Validation',
      weight: '5%',
      score: breakdown.prerequisite_fit_component,
      max: 5.0,
      icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
      desc: 'Verified readiness against foundational skill prerequisites',
    },
    {
      name: 'Duration & Format Fit',
      weight: '5%',
      score: breakdown.duration_fit_component,
      max: 5.0,
      icon: <Clock className="w-4 h-4 text-blue-400" />,
      desc: 'Continuing education suitability (modular vs intensive institutional)',
    },
    {
      name: 'Novelty & Non-Duplication',
      weight: '5%',
      score: breakdown.novelty_component,
      max: 5.0,
      icon: <CheckCircle2 className="w-4 h-4 text-teal-400" />,
      desc: 'Fresh learning content verified against historical training records',
    },
  ];

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
        {/* Backdrop click */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0"
          onClick={onClose}
        />

        {/* Drawer panel */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 28, stiffness: 280 }}
          className="relative w-full max-w-2xl h-full bg-slate-950 border-l border-slate-800 shadow-2xl overflow-y-auto flex flex-col z-10"
        >
          {/* Header */}
          <div className="sticky top-0 z-20 bg-slate-950/90 backdrop-blur-md border-b border-slate-800 p-6 flex items-start justify-between">
            <div className="space-y-2 pr-4">
              <div className="flex flex-wrap items-center gap-2">
                <ProviderBadge provider={item.provider} sourceMode={item.source_mode} />
                <GapPriorityBadge priority={recommendation.priority_level} size="sm" />
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  Rank #{recommendation.rank}
                </span>
              </div>
              <h2 className="text-2xl font-bold text-slate-100">{item.title}</h2>
              <p className="text-sm text-slate-400">
                Personalized Learning Recommendation for{' '}
                <span className="text-amber-400 font-medium">{recommendation.target_competency_name}</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors shrink-0"
              aria-label="Close drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="p-6 space-y-6 flex-1">
            {/* Recommendation Score Hero */}
            <div className="p-5 rounded-xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/30 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
                  <Calculator className="w-4 h-4" />
                  Deterministic Recommendation Score
                </div>
                <div className="text-3xl font-extrabold text-white flex items-baseline gap-2">
                  <span>{recommendation.score.toFixed(1)}</span>
                  <span className="text-sm font-normal text-slate-400">/ 100</span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Evaluated across 7 objective multidimensional factors
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-slate-400 mb-1">Duration</div>
                <div className="text-sm font-semibold text-slate-200">
                  {Math.round(item.duration_minutes / 60)} hrs ({item.duration_minutes}m)
                </div>
                <div className="text-xs text-slate-500 mt-0.5 capitalize">{item.format.toLowerCase().replace('_', ' ')}</div>
              </div>
            </div>

            {/* Why PRAGYA Recommended This */}
            <div className="space-y-3">
              <h3 className="text-base font-semibold text-slate-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                Why PRAGYA Recommended This
              </h3>
              <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 space-y-3">
                <p className="text-sm text-slate-200 font-medium leading-relaxed bg-slate-800/40 p-3 rounded-md border-l-4 border-amber-500">
                  {reason.summary}
                </p>
                <div className="grid grid-cols-1 gap-2.5 text-xs">
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="font-semibold text-rose-400 block mb-0.5">Skill Gap Analysis:</span>
                    <span className="text-slate-300">{reason.gap_reason}</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="font-semibold text-indigo-400 block mb-0.5">Role Cadre Alignment:</span>
                    <span className="text-slate-300">{reason.role_reason}</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="font-semibold text-amber-400 block mb-0.5">Competency Coverage:</span>
                    <span className="text-slate-300">{reason.competency_reason}</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="font-semibold text-sky-400 block mb-0.5">Level Progression:</span>
                    <span className="text-slate-300">{reason.level_reason}</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80">
                    <span className="font-semibold text-teal-400 block mb-0.5">Novelty Verification:</span>
                    <span className="text-slate-300">{reason.novelty_reason}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Factor Breakdown Table */}
            <div className="space-y-3">
              <h3 className="text-base font-semibold text-slate-200 flex items-center gap-2">
                <Calculator className="w-4 h-4 text-indigo-400" />
                Score Factor Breakdown (100% Deterministic)
              </h3>
              <div className="rounded-lg border border-slate-800 overflow-hidden bg-slate-900/60">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-900 text-slate-400 font-medium">
                      <th className="p-3">Evaluation Factor</th>
                      <th className="p-3 text-center">Weight</th>
                      <th className="p-3 text-right">Contribution</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {factorItems.map((factor, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="p-3">
                          <div className="flex items-center gap-2 font-medium text-slate-200">
                            {factor.icon}
                            {factor.name}
                          </div>
                          <div className="text-[11px] text-slate-500 mt-0.5 pl-6">{factor.desc}</div>
                        </td>
                        <td className="p-3 text-center font-mono text-slate-400">{factor.weight}</td>
                        <td className="p-3 text-right font-mono font-semibold text-slate-100">
                          <span className="text-amber-400">{factor.score.toFixed(2)}</span>
                          <span className="text-slate-500 font-normal"> / {factor.max.toFixed(1)}</span>
                        </td>
                      </tr>
                    ))}
                    <tr className="bg-slate-950/80 font-bold border-t-2 border-slate-700">
                      <td className="p-3 text-slate-100 pl-4">Final Recommendation Score</td>
                      <td className="p-3 text-center text-slate-400">100%</td>
                      <td className="p-3 text-right text-base text-amber-300 font-mono">
                        {recommendation.score.toFixed(2)} / 100.0
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Course Overview & Prerequisite Details */}
            <div className="space-y-3">
              <h3 className="text-base font-semibold text-slate-200 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-purple-400" />
                Course Curriculum Overview
              </h3>
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-3 text-xs">
                <p className="text-slate-300 leading-relaxed">{item.description}</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800">
                  <div>
                    <span className="text-slate-500 block">Difficulty</span>
                    <span className="font-semibold text-slate-200 capitalize">{item.difficulty.toLowerCase()}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Pedagogical Level</span>
                    <span className="font-semibold text-slate-200">Level {item.level} of 5</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Language</span>
                    <span className="font-semibold text-slate-200">{item.language}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Status</span>
                    <span className="font-semibold text-emerald-400">{recommendation.status}</span>
                  </div>
                </div>

                {item.competencies && item.competencies.length > 0 && (
                  <div className="pt-2 border-t border-slate-800">
                    <span className="text-slate-400 font-semibold block mb-1.5">Mapped Competencies:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {item.competencies.map((c, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] border border-slate-700"
                        >
                          {c.competency_name || c.competency_code} ({c.coverage_level})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer CTAs */}
          <div className="sticky bottom-0 z-20 bg-slate-950/95 backdrop-blur-md border-t border-slate-800 p-4 px-6 flex items-center justify-between">
            <div className="text-xs text-slate-500">
              Provider Mode:{' '}
              <span className="font-semibold text-amber-400/90">{item.source_mode} Demonstration</span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
              >
                Close
              </button>
              {(() => {
                const launchUrl = getCourseLaunchUrl(item);
                const isExternal = isExternalLaunchUrl(launchUrl);
                return isExternal ? (
                  <a
                    href={launchUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium flex items-center gap-1.5 shadow-md shadow-indigo-950/50 transition-all"
                    onClick={() => onStart && onStart(recommendation.id)}
                  >
                    <span>Start Learning</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                ) : (
                  <Link
                    href={launchUrl}
                    className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium flex items-center gap-1.5 shadow-md shadow-indigo-950/50 transition-all"
                    onClick={() => onStart && onStart(recommendation.id)}
                  >
                    <span>Start Learning</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                );
              })()}
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
