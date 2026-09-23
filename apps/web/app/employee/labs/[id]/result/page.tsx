'use client';

import React, { Suspense } from 'react';
import Link from 'next/link';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import {
  FlaskConical,
  Award,
  CheckCircle2,
  XCircle,
  RotateCcw,
  BrainCircuit,
  Sparkles,
  Loader2,
  ChevronLeft,
} from 'lucide-react';
import { useLabResult, useStartLabSession } from '@/hooks/use-labs';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';

function VirtualLabResultContent() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();

  const scenarioId = params.id as string;
  const sessionId = searchParams.get('sessionId') || '';
  const courseId = searchParams.get('courseId') || '';

  const { data: result, isLoading } = useLabResult(sessionId);
  const startSessionMutation = useStartLabSession();

  const handlePracticeAgain = () => {
    if (!scenarioId) return;
    startSessionMutation.mutate(scenarioId, {
      onSuccess: (session) => {
        const runUrl = courseId
          ? `/employee/labs/${scenarioId}/run?sessionId=${session.id}&courseId=${courseId}`
          : `/employee/labs/${scenarioId}/run?sessionId=${session.id}`;
        router.push(runUrl);
      },
    });
  };

  if (isLoading || !result) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Lab Results">
        <PageContainer>
          <div className="flex flex-col items-center justify-center p-24 space-y-3">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading lab completion results...</p>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const isPassed = result.passed;
  const actionsHistory = result.actions_history ?? [];
  const learningFeedback = result.learning_feedback ?? [];

  return (
    <AppShell role="EMPLOYEE" pageTitle={`Result: ${result.scenario_title}`}>
      <PageContainer>
        <div className="space-y-6 max-w-4xl mx-auto pb-16">
          {/* Back to Hub */}
          <Link
            href="/employee/labs"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Back to Virtual Labs Hub</span>
          </Link>

          {/* Main Title Heading */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-br from-[#0B0F19] to-slate-900 border border-violet-500/25 p-6 rounded-2xl shadow-xl">
            <div className="flex items-center gap-3">
              <div
                className={`p-3 rounded-2xl border ${
                  isPassed
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                }`}
              >
                <FlaskConical className="w-7 h-7" />
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-violet-400 font-bold">
                  Simulation Outcome
                </span>
                <h1 className="text-2xl font-bold text-white tracking-tight">
                  Virtual Lab Result
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">
                  Official statistical simulation evaluation and competency evidence assessment.
                </p>
              </div>
            </div>

            {/* Pass / Fail Status Badge */}
            <div
              className={`px-4 py-2 rounded-xl border text-sm font-bold font-mono shrink-0 flex items-center gap-2 self-start sm:self-auto ${
                isPassed
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}
            >
              {isPassed ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
              <span>{isPassed ? 'VERIFIED PASSED' : 'PRACTICE REQUIRED'}</span>
            </div>
          </div>

          {/* 1. WHAT YOU PRACTICED */}
          <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-3 shadow-lg">
            <span className="text-[10px] uppercase font-bold tracking-wider text-violet-400 block">
              WHAT YOU PRACTICED
            </span>
            <div className="space-y-1.5">
              <h2 className="text-base font-bold text-white">
                {result.scenario_title}
              </h2>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-violet-500/10 text-violet-300 border border-violet-500/25">
                  {result.scenario_type?.replace(/_/g, ' ') || 'STATISTICAL SIMULATION'}
                </span>
                <span className="text-xs text-slate-400">
                  Target Competency: <strong className="text-slate-200">{result.competency_name || 'Statistical Methodology'}</strong>
                </span>
              </div>
            </div>
          </div>

          {/* 2. YOUR PERFORMANCE & 3. YOUR SCORE */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* YOUR PERFORMANCE */}
            <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4 shadow-lg flex flex-col justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-cyan-400 block mb-3">
                  YOUR PERFORMANCE
                </span>
                <div className="space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                    <span className="text-xs text-slate-400">Simulation Status</span>
                    <span className={`text-xs font-bold font-mono ${isPassed ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isPassed ? 'PASSED (≥ 60% Benchmark)' : 'NEEDS PRACTICE (< 60%)'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                    <span className="text-xs text-slate-400">Actions Completed</span>
                    <span className="text-xs font-mono font-bold text-white">
                      {result.actions_completed} Actions
                    </span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                    <span className="text-xs text-slate-400">Accuracy Rate</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      {result.correct_actions} / {result.actions_completed} ({result.actions_completed > 0 ? ((result.correct_actions / result.actions_completed) * 100).toFixed(0) : 0}%)
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-[11px] text-slate-400 bg-slate-900/50 p-3 rounded-xl border border-slate-800">
                Evaluation computed via deterministic MoSPI validation rules against ground-truth parameters.
              </div>
            </div>

            {/* YOUR SCORE */}
            <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4 shadow-lg flex flex-col justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-amber-400 block mb-3">
                  YOUR SCORE
                </span>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                    <div className="text-[11px] font-medium text-slate-400">Lab Score</div>
                    <div className="text-2xl font-bold text-white font-mono mt-1">
                      {result.total_score.toFixed(0)} <span className="text-xs text-slate-500 font-normal">/ 100</span>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Points awarded</div>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                    <div className="text-[11px] font-medium text-slate-400">Percentage</div>
                    <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
                      {result.percentage.toFixed(0)}%
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Passing benchmark: 60%</div>
                  </div>
                </div>
              </div>
              <div className="text-[11px] text-slate-400 bg-slate-900/50 p-3 rounded-xl border border-slate-800 flex items-center justify-between">
                <span>Confidence Calibration:</span>
                <span className="font-mono font-bold text-cyan-400">{(result.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          {/* 4. YOUR COMPETENCY EVIDENCE */}
          <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4 shadow-lg">
            <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400 block">
              YOUR COMPETENCY EVIDENCE
            </span>
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">
                  <Award className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <div className="text-xs font-bold text-emerald-300">
                    {result.competency_name || 'Statistical Methodology'}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
                    {isPassed
                      ? 'Verified simulation evidence has been deposited into your PRAGYA competency profile with a 20% weighting factor.'
                      : 'Evidence recorded for practice tracking. You can repeat the simulation to meet the 60% mastery threshold.'}
                  </p>
                </div>
              </div>
              {result.evidence_id && (
                <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-[11px] font-mono text-emerald-300 shrink-0 self-start sm:self-auto">
                  Evidence ID: {result.evidence_id.slice(0, 8)}...
                </div>
              )}
            </div>

            {/* Step-by-Step Action Audit */}
            <div className="space-y-2 pt-2">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Audited Action Record:
              </div>
              <div className="space-y-2">
                {actionsHistory.length > 0 ? (
                  actionsHistory.map((act) => (
                    <div
                      key={act.id}
                      className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="w-6 h-6 rounded-md bg-slate-800 text-slate-300 flex items-center justify-center font-mono text-[11px] font-bold shrink-0">
                          {act.step_number}
                        </span>
                        <div>
                          <div className="text-xs font-semibold text-white flex items-center gap-2">
                            <span>{act.action_type.replace(/_/g, ' ')}</span>
                            {act.is_correct ? (
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <XCircle className="w-3.5 h-3.5 text-rose-400" />
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400">{act.feedback}</p>
                        </div>
                      </div>
                      <span className={`font-mono text-xs font-bold shrink-0 ${act.is_correct ? 'text-emerald-400' : 'text-rose-400'}`}>
                        +{act.score_awarded} pts
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-500 text-xs">
                    No action steps recorded in this simulation run.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 5. WHAT TO IMPROVE */}
          <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4 shadow-lg">
            <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-400 block">
              WHAT TO IMPROVE
            </span>
            {learningFeedback.length > 0 ? (
              <div className="space-y-2.5">
                {learningFeedback.map((fb, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-900/50 border border-slate-800/90 text-xs text-slate-300 flex items-start gap-3"
                  >
                    <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5 font-bold">
                      {idx + 1}
                    </span>
                    <p className="leading-relaxed">{fb}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-400">
                Continue practicing analytical workflows to maintain high consistency across complex survey domains.
              </div>
            )}
          </div>

          {/* 6. NEXT STEPS (Three Explicit Actions) */}
          <div className="space-y-3 pt-2">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
              NEXT STEPS
            </span>

            {/* Course Integration Return CTA */}
            {courseId && (
              <div className="p-4 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
                <div>
                  <div className="text-xs font-bold text-indigo-300">
                    Linked Course Practical Module
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {isPassed
                      ? 'You successfully passed this Virtual Lab! Return to your course player to update your module completion progress.'
                      : 'Lab completed. Return to the course player to review curriculum topics.'}
                  </div>
                </div>
                <Link
                  href={`/employee/courses/${courseId}/launch?labCompleted=${isPassed}`}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-2 shrink-0 justify-center"
                >
                  <span>Return to Course & Update Progress</span>
                  <ChevronLeft className="w-4 h-4 rotate-180" />
                </Link>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Action 1: Practice Again */}
              <button
                onClick={handlePracticeAgain}
                disabled={startSessionMutation.isPending}
                className="p-5 rounded-2xl bg-[#0B0F19] hover:bg-slate-900 border border-slate-800 hover:border-violet-500/40 transition flex items-start gap-3.5 text-left group shadow-lg"
              >
                <div className="p-3 rounded-xl bg-violet-600/15 text-violet-400 group-hover:bg-violet-600/25 transition shrink-0">
                  <RotateCcw className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <div className="text-xs font-bold text-white group-hover:text-violet-300 transition">
                    Practice Again
                  </div>
                  <div className="text-xs text-slate-400 leading-snug">
                    Repeat this simulation
                  </div>
                </div>
              </button>

              {/* Action 2: Test this Skill */}
              <Link
                href={`/employee/quizzes?competencyId=${result.competency_id || ''}`}
                className="p-5 rounded-2xl bg-[#0B0F19] hover:bg-slate-900 border border-slate-800 hover:border-indigo-500/40 transition flex items-start gap-3.5 text-left group shadow-lg"
              >
                <div className="p-3 rounded-xl bg-indigo-600/15 text-indigo-400 group-hover:bg-indigo-600/25 transition shrink-0">
                  <BrainCircuit className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <div className="text-xs font-bold text-white group-hover:text-indigo-300 transition">
                    Test this Skill
                  </div>
                  <div className="text-xs text-slate-400 leading-snug">
                    Take an AI quiz on this competency
                  </div>
                </div>
              </Link>

              {/* Action 3: Reassess Competency */}
              <Link
                href={`/employee/adaptive-assessment?competencyId=${result.competency_id || ''}`}
                className="p-5 rounded-2xl bg-[#0B0F19] hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 transition flex items-start gap-3.5 text-left group shadow-lg"
              >
                <div className="p-3 rounded-xl bg-cyan-600/15 text-cyan-400 group-hover:bg-cyan-600/25 transition shrink-0">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <div className="text-xs font-bold text-white group-hover:text-cyan-300 transition">
                    Reassess Competency
                  </div>
                  <div className="text-xs text-slate-400 leading-snug">
                    Measure your current demonstrated competency again
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}

export default function VirtualLabResultPage() {
  return (
    <Suspense
      fallback={
        <AppShell role="EMPLOYEE" pageTitle="Virtual Lab Results">
          <PageContainer>
            <div className="flex items-center justify-center min-h-[50vh]">
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            </div>
          </PageContainer>
        </AppShell>
      }
    >
      <VirtualLabResultContent />
    </Suspense>
  );
}

