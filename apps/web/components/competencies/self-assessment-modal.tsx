'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, UserCheck, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { useSubmitSelfAssessment } from '@/hooks/use-assessment';
import type { EmployeeCompetency } from '@pragya/types';

interface SelfAssessmentModalProps {
  employeeId?: string;
  competency: EmployeeCompetency | null;
  onClose: () => void;
  onSuccess?: () => void;
}

const PROFICIENCY_CHOICES = [
  {
    level: 1,
    label: 'Beginner',
    score: 20,
    desc: 'Basic awareness and initial conceptual understanding. Requires direct supervision.',
  },
  {
    level: 2,
    label: 'Basic',
    score: 40,
    desc: 'Understands core principles and performs standard routine steps with periodic guidance.',
  },
  {
    level: 3,
    label: 'Working',
    score: 60,
    desc: 'Autonomous execution in standard statistical/technical scenarios with sound quality.',
  },
  {
    level: 4,
    label: 'Proficient',
    score: 80,
    desc: 'Advanced practical fluency, handles complex edge cases, and guides junior cadre officers.',
  },
  {
    level: 5,
    label: 'Advanced',
    score: 100,
    desc: 'Authoritative subject-matter mastery, defines ministry methodologies and standards.',
  },
];

export function SelfAssessmentModal({
  employeeId,
  competency,
  onClose,
  onSuccess,
}: SelfAssessmentModalProps) {
  const [selectedLevel, setSelectedLevel] = useState<number | null>(null);
  const submitMutation = useSubmitSelfAssessment();

  if (!competency) return null;

  const handleSubmit = async () => {
    if (!selectedLevel || !employeeId) return;

    try {
      await submitMutation.mutateAsync({
        employeeId,
        payload: {
          competency_id: competency.competency_id,
          level: selectedLevel,
        },
      });
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      console.error('Failed to submit self assessment:', err);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0"
        />

        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', duration: 0.3 }}
          className="relative w-full max-w-lg bg-[#0B1120] border border-cyan-500/30 shadow-2xl rounded-2xl p-6 overflow-hidden space-y-5"
        >
          {/* Header */}
          <div className="flex items-start justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-400">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-cyan-400 block">
                  {competency.competency_code}
                </span>
                <h3 className="text-lg font-bold text-slate-100">
                  Self Assessment: {competency.competency_name}
                </h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Prototype weighting notice */}
          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p className="leading-relaxed text-[11px]">
              Self-evaluation contributes <strong className="font-semibold text-amber-200">5% weight</strong> to your overall demonstrated competency score in PRAGYA. Choose the level that most accurately reflects your daily practical capability.
            </p>
          </div>

          {/* Level Selection */}
          <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
            {PROFICIENCY_CHOICES.map((choice) => {
              const isSelected = selectedLevel === choice.level;
              return (
                <button
                  key={choice.level}
                  type="button"
                  onClick={() => setSelectedLevel(choice.level)}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-start gap-3.5 ${
                    isSelected
                      ? 'bg-gradient-to-r from-cyan-950/40 to-blue-950/40 border-cyan-500 shadow-lg shadow-cyan-950/50'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center border mt-0.5 flex-shrink-0 transition-colors ${
                      isSelected
                        ? 'bg-cyan-500 border-cyan-400 text-slate-950'
                        : 'border-slate-700 bg-slate-950'
                    }`}
                  >
                    {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-bold text-slate-200 flex items-center gap-2">
                        <span>Level {choice.level}</span>
                        <span className="text-xs font-semibold text-cyan-400">— {choice.label}</span>
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">
                        Normalized: {choice.score}/100
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-snug">{choice.desc}</p>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Actions */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
            <button
              onClick={onClose}
              disabled={submitMutation.isPending}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!selectedLevel || submitMutation.isPending}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all"
            >
              {submitMutation.isPending ? (
                <>Submitting...</>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Submit & Recalculate</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
