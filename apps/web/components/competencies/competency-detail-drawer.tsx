'use client';

import React from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Award,
  BookOpen,
  Target,
  Compass,
  AlertCircle,
  Layers,
  ShieldCheck,
  FileText,
  BrainCircuit,
} from 'lucide-react';
import type { RoleCompetencyRequirement } from '@pragya/types';
import { useCompetency } from '@/hooks/use-competency';

interface CompetencyDetailDrawerProps {
  competencyId: string | null;
  onClose: () => void;
  currentRoleRequirement?: RoleCompetencyRequirement | null;
}

export function CompetencyDetailDrawer({
  competencyId,
  onClose,
  currentRoleRequirement,
}: CompetencyDetailDrawerProps) {
  const { data: competency, isLoading } = useCompetency(competencyId || undefined);

  return (
    <AnimatePresence>
      {competencyId && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
          {/* Backdrop click to close */}
          <div className="flex-1" onClick={onClose} />

          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-full max-w-xl bg-[#0F172A] border-l border-cyan-500/20 shadow-2xl flex flex-col h-full overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-slate-800/80 bg-slate-900/60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Award className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                      {competency?.code || '...'}
                    </span>
                    <span className="text-xs text-slate-400">
                      v{competency?.version || '1.0'}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-100 mt-1">
                    {competency?.name || 'Loading Competency...'}
                  </h2>
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content Body */}
            {isLoading || !competency ? (
              <div className="p-8 space-y-4 animate-pulse">
                <div className="h-6 w-48 bg-slate-800 rounded" />
                <div className="h-24 w-full bg-slate-900 rounded-xl" />
                <div className="h-32 w-full bg-slate-900 rounded-xl" />
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-slate-300">
                {/* Domain & Source Badge */}
                <div className="flex flex-wrap items-center justify-between gap-2 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">Domain:</span>
                    <span className="font-semibold text-cyan-300">
                      {competency.domain_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-400">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>Source:</span>
                    <span className="font-mono text-slate-200">
                      {competency.source_reference}
                    </span>
                  </div>
                </div>

                {/* Role Requirement Callout (If required for current role) */}
                {currentRoleRequirement ? (
                  <div className="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/40 via-slate-900/80 to-slate-900 border border-cyan-500/30 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-mono text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                        <Target className="w-3.5 h-3.5 text-cyan-400" />
                        Cadre Role Requirement
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          currentRoleRequirement.criticality === 'CRITICAL'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : currentRoleRequirement.criticality === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        }`}
                      >
                        {currentRoleRequirement.criticality} Criticality
                      </span>
                    </div>

                    <div className="flex items-baseline justify-between pt-1">
                      <div>
                        <div className="text-sm font-bold text-slate-100">
                          {currentRoleRequirement.job_role_name}
                        </div>
                        <div className="text-xs text-slate-400">
                          Required Level: <strong className="text-cyan-300">Level {currentRoleRequirement.required_level_number} — {currentRoleRequirement.required_level_name}</strong>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-extrabold text-cyan-300 font-mono">
                          {currentRoleRequirement.required_score}/100
                        </div>
                        <div className="text-[10px] text-slate-400">Target Score</div>
                      </div>
                    </div>

                    {currentRoleRequirement.rationale && (
                      <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 text-[11px] text-slate-300 space-y-1">
                        <span className="font-semibold text-cyan-300 block">
                          Why this competency matters for your role:
                        </span>
                        <p className="leading-relaxed text-slate-300">
                          {currentRoleRequirement.rationale}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-400 flex items-center gap-2.5">
                    <AlertCircle className="w-4 h-4 text-slate-500 shrink-0" />
                    <span>
                      This competency is part of the general statistical framework and not currently marked as a primary requirement for your role.
                    </span>
                  </div>
                )}

                {/* Description */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                    <FileText className="w-4 h-4 text-cyan-400" />
                    Competency Definition
                  </h4>
                  <p className="text-sm leading-relaxed text-slate-300 p-4 rounded-xl bg-slate-900/50 border border-slate-800/80">
                    {competency.description}
                  </p>
                </div>

                {/* Learning Objectives */}
                {competency.learning_objectives && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <BookOpen className="w-4 h-4 text-violet-400" />
                      Key Learning Objectives
                    </h4>
                    <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 text-xs leading-relaxed text-slate-300">
                      {competency.learning_objectives}
                    </div>
                  </div>
                )}

                {/* Measurement Guidance */}
                {competency.measurement_guidance && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <Compass className="w-4 h-4 text-emerald-400" />
                      Measurement & Assessment Guidance
                    </h4>
                    <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 text-xs leading-relaxed text-slate-300">
                      {competency.measurement_guidance}
                    </div>
                  </div>
                )}

                {/* Prerequisites */}
                {competency.prerequisites && competency.prerequisites.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      Prerequisite & Related Capabilities
                    </h4>
                    <div className="space-y-2">
                      {competency.prerequisites.map((rel) => (
                        <div
                          key={rel.id}
                          className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-slate-800"
                        >
                          <div>
                            <span className="font-semibold text-slate-200">
                              {rel.source_competency_name}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono ml-2">
                              ({rel.source_competency_code})
                            </span>
                          </div>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                            {rel.relationship_type}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Demanding Roles */}
                {competency.requiring_roles && competency.requiring_roles.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <Award className="w-4 h-4 text-amber-400" />
                      Cadre Roles Requiring this Competency
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                      {competency.requiring_roles.map((r, idx) => (
                        <div
                          key={idx}
                          className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1"
                        >
                          <div className="font-semibold text-slate-200">{r.job_role_name}</div>
                          <div className="flex items-center justify-between text-[11px] text-slate-400">
                            <span>Level {r.required_level_number}</span>
                            <span className="text-cyan-300">{r.criticality}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reassess Competency CTA */}
                <div className="pt-2 border-t border-slate-800">
                  <Link
                    href={`/employee/adaptive-assessment?competencyId=${competency.id}`}
                    className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-md shadow-indigo-950/40 transition"
                  >
                    <BrainCircuit className="w-4 h-4" />
                    <span>Reassess Competency</span>
                  </Link>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
