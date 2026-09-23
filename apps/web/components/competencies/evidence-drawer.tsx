'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Award,
  Layers,
  BookOpen,
  Briefcase,
  UserCheck,
  Info,
  Sliders,
} from 'lucide-react';
import { useCompetencyEvidence } from '@/hooks/use-assessment';
import type { EmployeeCompetency } from '@pragya/types';

interface EvidenceDrawerProps {
  employeeId?: string;
  competency: EmployeeCompetency | null;
  onClose: () => void;
}

export function EvidenceDrawer({
  employeeId,
  competency,
  onClose,
}: EvidenceDrawerProps) {
  const { data: evidenceList = [], isLoading } = useCompetencyEvidence(
    employeeId,
    competency?.competency_id || null
  );

  if (!competency) return null;

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'DIAGNOSTIC':
      case 'RECENT_ASSESSMENT':
        return <Award className="w-4 h-4 text-cyan-400" />;
      case 'TRAINING':
        return <BookOpen className="w-4 h-4 text-violet-400" />;
      case 'EXPERIENCE':
        return <Briefcase className="w-4 h-4 text-emerald-400" />;
      case 'SELF_ASSESSMENT':
        return <UserCheck className="w-4 h-4 text-amber-400" />;
      default:
        return <Layers className="w-4 h-4 text-slate-400" />;
    }
  };

  const getSourceBadge = (type: string) => {
    switch (type) {
      case 'DIAGNOSTIC':
        return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
      case 'RECENT_ASSESSMENT':
        return 'bg-blue-500/15 text-blue-300 border-blue-500/30';
      case 'TRAINING':
        return 'bg-violet-500/15 text-violet-300 border-violet-500/30';
      case 'EXPERIENCE':
        return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
      case 'SELF_ASSESSMENT':
        return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

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
          className="relative w-full max-w-2xl h-full bg-[#0B1120] border-l border-cyan-500/30 shadow-2xl p-6 overflow-y-auto flex flex-col justify-between"
        >
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between pb-5 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-400">
                    {competency.competency_code}
                  </span>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {competency.domain_name}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                  <span>{competency.competency_name}</span>
                  <span className="text-xs text-slate-400 font-normal">
                    — Evidence Portfolio
                  </span>
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Score & Confidence Summary Card */}
            <div className="p-5 rounded-2xl bg-gradient-to-br from-[#0F172A] via-[#0D1527] to-[#090D18] border border-cyan-500/30 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                  Demonstrated Score
                </span>
                <div className="text-2xl font-bold text-cyan-300 font-mono flex items-baseline gap-1">
                  {competency.current_score.toFixed(1)}
                  <span className="text-xs text-slate-500">/ 100</span>
                </div>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                  Proficiency Level
                </span>
                <div className="text-sm font-bold text-slate-100">
                  Level {competency.proficiency_level_number}
                </div>
                <div className="text-[10px] text-cyan-400 font-medium">
                  {competency.proficiency_level_name}
                </div>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                  Confidence Rating
                </span>
                <span
                  className={`inline-block text-[11px] font-bold px-2 py-0.5 rounded border uppercase ${
                    competency.confidence_label === 'VERY_HIGH'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : competency.confidence_label === 'HIGH'
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                      : competency.confidence_label === 'MEDIUM'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                  }`}
                >
                  {competency.confidence_label} ({(competency.confidence * 100).toFixed(0)}%)
                </span>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                  Evidence Sources
                </span>
                <div className="text-2xl font-bold text-slate-100 font-mono">
                  {evidenceList.length}
                </div>
              </div>
            </div>

            {/* Methodology Explainer */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 font-semibold">
                <Sliders className="w-4 h-4" />
                <span>Available-Evidence Renormalization Model</span>
              </div>
              <p className="text-slate-400 leading-relaxed">
                PRAGYA computes demonstrated competency by aggregating multiple empirical evidence
                channels (Diagnostic Assessments, Verified Training, Cadre Experience, and Self-Assessment).
                When specific evidence channels are not yet recorded, weights are automatically
                renormalized so missing evidence does not penalize your score.
              </p>
            </div>

            {/* Evidence Items Breakdown */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center justify-between">
                <span>Empirical Evidence Records</span>
                <span className="text-xs text-slate-500 font-normal">
                  Chronological audit
                </span>
              </h3>

              {isLoading ? (
                <div className="py-8 text-center text-xs text-slate-500">
                  Loading evidence portfolio...
                </div>
              ) : evidenceList.length === 0 ? (
                <div className="p-6 rounded-xl bg-slate-950/40 border border-slate-800 text-center space-y-2">
                  <Info className="w-6 h-6 text-slate-500 mx-auto" />
                  <p className="text-xs text-slate-400">
                    No empirical evidence recorded for this competency yet.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {evidenceList.map((ev) => (
                    <div
                      key={ev.id}
                      className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition-all space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                            {getSourceIcon(ev.evidence_type)}
                          </div>
                          <span
                            className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${getSourceBadge(
                              ev.evidence_type
                            )}`}
                          >
                            {ev.evidence_type.replace('_', ' ')}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-500">
                          {new Date(ev.recorded_at).toLocaleDateString(undefined, {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                      </div>

                      {/* Metrics Grid */}
                      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-900 text-xs">
                        <div>
                          <span className="text-[10px] text-slate-500 block">
                            Normalized Score
                          </span>
                          <span className="font-bold text-slate-200 font-mono">
                            {ev.normalized_score.toFixed(1)} / 100
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 block">
                            Weight Applied
                          </span>
                          <span className="font-bold text-cyan-400 font-mono">
                            {(ev.weight_used * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 block">
                            Contribution
                          </span>
                          <span className="font-bold text-emerald-400 font-mono">
                            +{ev.contribution.toFixed(1)} pts
                          </span>
                        </div>
                      </div>

                      {/* Metadata Description */}
                      {ev.metadata && (
                        <div className="text-[11px] text-slate-400 bg-slate-900/60 p-2 rounded border border-slate-800/60">
                          {ev.metadata.training_title && (
                            <div>Course: {ev.metadata.training_title} ({ev.metadata.provider})</div>
                          )}
                          {ev.metadata.experience_years !== undefined && (
                            <div>Cadre Experience: {ev.metadata.experience_years} years completed</div>
                          )}
                          {ev.metadata.level_label && (
                            <div>Self Rating: Level {ev.metadata.self_assessment_level} ({ev.metadata.level_label})</div>
                          )}
                          {ev.metadata.questions_tested && (
                            <div>Diagnostic Test: {ev.metadata.correct_count} / {ev.metadata.questions_tested} correct ({ev.normalized_score}%)</div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
            >
              Close Portfolio
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
