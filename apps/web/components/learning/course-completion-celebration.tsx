'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Trophy,
  CheckCircle2,
  Sparkles,
  ShieldCheck,
  ArrowRight,
  RotateCw,
  FlaskConical,
  Award,
  BookOpen,
} from 'lucide-react';
import type { RecalibrateCourseResponse } from '@pragya/types';

interface CourseCompletionCelebrationProps {
  courseTitle: string;
  provider: string;
  finalScore?: number | null;
  onRecalibrate: () => Promise<RecalibrateCourseResponse>;
}

export function CourseCompletionCelebration({
  courseTitle,
  provider,
  finalScore = 88.0,
  onRecalibrate,
}: CourseCompletionCelebrationProps) {
  const [isRecalibrating, setIsRecalibrating] = useState(false);
  const [recalibrateResult, setRecalibrateResult] = useState<RecalibrateCourseResponse | null>(null);

  const handleRecalibrate = async () => {
    setIsRecalibrating(true);
    try {
      const res = await onRecalibrate();
      setRecalibrateResult(res);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Failed to trigger competency recalibration.');
    } finally {
      setIsRecalibrating(false);
    }
  };

  return (
    <div className="rounded-3xl border border-emerald-500/30 bg-gradient-to-b from-[#0A1612] via-[#0A0E1A] to-[#0A0E1A] p-8 md:p-12 shadow-2xl space-y-8 max-w-4xl mx-auto">
      {/* Trophy & Badge */}
      <div className="flex flex-col items-center text-center space-y-4">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-emerald-600 to-teal-400 p-0.5 shadow-2xl shadow-emerald-950/60">
          <div className="w-full h-full rounded-[22px] bg-[#0A1612] flex items-center justify-center text-emerald-400">
            <Trophy className="w-10 h-10 animate-bounce" />
          </div>
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
            <Award className="w-3.5 h-3.5" />
            <span>Official Competency Evidence Certified</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Course Learning & Practical Simulation Completed!
          </h2>
          <p className="text-xs md:text-sm text-slate-300 max-w-xl mx-auto leading-relaxed">
            Congratulations! You have completed all academic learning modules for <strong className="text-white">{courseTitle}</strong> ({provider}), validated your practical analytical decisions in the Virtual Lab, and passed the final course examination.
          </p>
        </div>
      </div>

      {/* Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Academic Learning Column */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-indigo-400 font-bold uppercase tracking-wider">
            <BookOpen className="w-4 h-4" />
            <span>Academic Learning Evidence</span>
          </div>
          <ul className="space-y-2 text-slate-300">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Module 1: Foundations & Legal Protocols (Verified)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Module 2: Sampling Methodology & Practice Assignment (Passed)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Module 3: MoSPI NQAF Standards & SDMX (Verified)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Comprehensive Final Assessment (Passed: {finalScore}%)</span>
            </li>
          </ul>
        </div>

        {/* Practical Demonstration Column */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-violet-400 font-bold uppercase tracking-wider">
            <FlaskConical className="w-4 h-4" />
            <span>Practical Virtual Lab Demonstration</span>
          </div>
          <ul className="space-y-2 text-slate-300">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Step 1: Probability Sampling Method Selected</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Step 2: Sample Size Determined via Power Analysis</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Step 3: Strata Allocation Strategy Executed</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Step 4: Deterministic Simulation Verified & Passed</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Closed Loop Recalibration Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-indigo-950/40 border border-emerald-500/30 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <ShieldCheck className="w-4 h-4" />
              <span>Closed-Loop Competency Recalibration</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed max-w-xl">
              Apply this verified evidence to update your official competency profile, close the target skill gap, and unlock advanced learning recommendations.
            </p>
          </div>

          <button
            onClick={handleRecalibrate}
            disabled={isRecalibrating}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-emerald-950/50 shrink-0"
          >
            <RotateCw className={`w-4 h-4 ${isRecalibrating ? 'animate-spin' : ''}`} />
            <span>{isRecalibrating ? 'Recalibrating Profile...' : 'Recalibrate Competencies'}</span>
          </button>
        </div>

        {/* Recalibration Result if triggered */}
        {recalibrateResult && (
          <div className="pt-3 border-t border-slate-800 text-xs space-y-2">
            <div className="text-emerald-300 font-semibold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>Competency Profile Updated:</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {recalibrateResult.recalibrated_competencies.map((c, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                  <span className="text-slate-300 font-medium">{c.competency_name || c.competency_code}</span>
                  <span className="text-emerald-400 font-bold font-mono">{c.current_score?.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
        <Link
          href="/employee/gaps"
          className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition"
        >
          <span>View Updated Skill Gaps</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
        <Link
          href="/employee/learning"
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-indigo-950/50"
        >
          <span>View New AI Recommendations</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
