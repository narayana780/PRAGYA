'use client';

import React, { useState, useEffect, useMemo, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Send,
  AlertCircle,
  CheckCircle2,
  Layers,
  ArrowRight,
  Award,
  ShieldCheck,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';
import {
  useAssessmentAttempt,
  useRecordResponse,
  useCompleteAttempt,
} from '@/hooks/use-assessment';
import type { QuestionPublic, CompleteAttemptResult } from '@pragya/types';

const OPTION_LETTERS = ['A', 'B', 'C', 'D'];

function DiagnosticRunnerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const attemptId = searchParams.get('attemptId');

  const { data: attempt, isLoading: attemptLoading } = useAssessmentAttempt(
    attemptId || null
  );

  const recordResponseMutation = useRecordResponse();
  const completeAttemptMutation = useCompleteAttempt();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [submissionResult, setSubmissionResult] = useState<CompleteAttemptResult | null>(null);

  const questions: QuestionPublic[] = useMemo(() => {
    return attempt?.questions || [];
  }, [attempt]);

  // Track already answered question IDs
  useEffect(() => {
    if (attempt?.answered_question_ids && attempt.answered_question_ids.length > 0) {
      // Mark as answered if resuming
    }
  }, [attempt]);

  const currentQuestion = questions[currentIndex];
  const totalQuestions = questions.length;
  const progressPercent = totalQuestions > 0 ? ((currentIndex + 1) / totalQuestions) * 100 : 0;

  const handleSelectOption = async (optionIdx: number) => {
    if (!currentQuestion || !attemptId || !attempt) return;

    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionIdx,
    }));

    try {
      await recordResponseMutation.mutateAsync({
        attemptId,
        questionId: currentQuestion.id,
        selectedOption: optionIdx,
        employeeId: attempt.employee_id,
      });
    } catch (err) {
      console.error('Auto-save response failed:', err);
    }
  };

  const handleNext = () => {
    if (currentIndex < totalQuestions - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!attemptId) return;

    try {
      const result = await completeAttemptMutation.mutateAsync({
        attemptId,
        employeeId: attempt?.employee_id,
      });
      setSubmissionResult(result);
    } catch (err) {
      console.error('Failed to complete assessment:', err);
    }
  };

  if (attemptLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#070B14] text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-mono">Initializing Psychometric Diagnostic Engine...</span>
        </div>
      </div>
    );
  }

  if (!attempt || questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#070B14] text-slate-400 p-6">
        <div className="max-w-md p-6 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
          <h2 className="text-lg font-bold text-slate-100">Assessment Session Unavailable</h2>
          <p className="text-xs text-slate-400">
            Could not find an active session for this diagnostic test. Please initiate a new attempt.
          </p>
          <button
            onClick={() => router.push('/employee/assessments')}
            className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold"
          >
            Return to Assessments Dashboard
          </button>
        </div>
      </div>
    );
  }

  // SUBMISSION SUCCESS EVALUATION SUMMARY SCREEN
  if (submissionResult) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Assessment Results">
        <PageContainer>
          <div className="max-w-3xl mx-auto py-8 space-y-6">
            <div className="p-8 rounded-3xl bg-gradient-to-br from-[#0B172A] via-[#0D1933] to-[#080E1D] border border-cyan-500/40 shadow-2xl space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-cyan-400">
                    Evaluation Complete • Server Verified Psychometrics
                  </span>
                  <h1 className="text-2xl font-black text-slate-100">
                    {attempt.assessment_title}
                  </h1>
                </div>
              </div>

              {/* Score Highlight Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                    Diagnostic Score
                  </span>
                  <div className="text-3xl font-black text-cyan-300 font-mono">
                    {submissionResult.percentage.toFixed(1)}%
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                    Points Earned
                  </span>
                  <div className="text-3xl font-black text-emerald-300 font-mono">
                    {submissionResult.raw_score} / {submissionResult.max_score}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 block mb-1">
                    Demonstrated Evidence
                  </span>
                  <div className="text-sm font-bold text-slate-200 mt-2 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-cyan-400" />
                    <span>Evidence Recorded</span>
                  </div>
                </div>
              </div>

              {/* Competency Breakdown */}
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  <span>Demonstrated Competency Breakdown</span>
                </h3>

                <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                  {submissionResult.competency_breakdown?.map((item) => (
                    <div
                      key={item.competency_id}
                      className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between gap-4"
                    >
                      <div>
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-[10px] font-mono text-cyan-400 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800">
                            {item.competency_code}
                          </span>
                          <span className="text-xs font-bold text-slate-200">
                            {item.competency_name}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400">
                          {item.correct_count} of {item.questions_tested} questions correct
                        </span>
                      </div>

                      <div className="text-right">
                        <span className="text-sm font-bold font-mono text-cyan-300">
                          {item.score_percentage.toFixed(0)}%
                        </span>
                        <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                            style={{ width: `${item.score_percentage}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Next Action */}
              <div className="pt-4 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => router.push('/employee/competency')}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition-all"
                >
                  <span>View Updated Competency Profile</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const answeredCount = Object.keys(selectedAnswers).length;

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col justify-between">
      {/* TOP HEADER */}
      <header className="border-b border-slate-800/80 bg-[#090E1A]/90 backdrop-blur-md sticky top-0 z-30 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-mono uppercase tracking-widest text-cyan-400">
                PRAGYA Diagnostic Engine
              </div>
              <h1 className="text-base font-bold text-slate-100">
                {attempt.assessment_title}
              </h1>
            </div>
          </div>

          {/* Quick Counter */}
          <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
            <span className="hidden sm:inline">
              Answered: {answeredCount} / {totalQuestions}
            </span>
            <button
              onClick={() => {
                if (confirm('Are you sure you want to pause and return to the dashboard? Your progress is saved.')) {
                  router.push('/employee/assessments');
                }
              }}
              className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs transition-colors"
            >
              Save & Exit
            </button>
          </div>
        </div>

        {/* PROGRESS BAR */}
        <div className="max-w-5xl mx-auto mt-3">
          <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 shadow-sm shadow-cyan-500"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ duration: 0.2 }}
            />
          </div>
        </div>
      </header>

      {/* QUESTION BODY */}
      <main className="max-w-4xl w-full mx-auto px-6 py-8 flex-1 flex flex-col justify-center">
        <div className="space-y-6">
          {/* Question Metadata Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 font-mono text-cyan-400 font-semibold">
                Question {currentIndex + 1} of {totalQuestions}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                  currentQuestion.difficulty === 'HARD'
                    ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                    : currentQuestion.difficulty === 'MEDIUM'
                    ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                    : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                }`}
              >
                {currentQuestion.difficulty}
              </span>
              <span className="text-slate-500 font-mono text-[11px]">
                {currentQuestion.points} {currentQuestion.points === 1 ? 'pt' : 'pts'}
              </span>
            </div>
          </div>

          {/* Question Text */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-[#0F172A] to-[#0A101D] border border-cyan-500/30 shadow-xl">
            <h2 className="text-lg sm:text-xl font-bold text-slate-100 leading-relaxed">
              {currentQuestion.question_text}
            </h2>
          </div>

          {/* Answer Options */}
          <div className="space-y-3">
            {currentQuestion.options.map((optionText, optionIdx) => {
              const active = selectedAnswers[currentQuestion.id] === optionIdx;
              const letter = OPTION_LETTERS[optionIdx] || `${optionIdx + 1}`;
              return (
                <button
                  key={optionIdx}
                  type="button"
                  onClick={() => handleSelectOption(optionIdx)}
                  className={`w-full text-left p-4 rounded-xl border transition-all flex items-center gap-4 ${
                    active
                      ? 'bg-gradient-to-r from-cyan-950/50 to-blue-950/50 border-cyan-400 shadow-lg shadow-cyan-950/40'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono font-bold text-xs border transition-colors ${
                      active
                        ? 'bg-cyan-500 border-cyan-400 text-slate-950'
                        : 'bg-slate-950 border-slate-800 text-slate-400'
                    }`}
                  >
                    {letter}
                  </div>
                  <span
                    className={`text-sm leading-relaxed flex-1 ${
                      active ? 'font-semibold text-cyan-200' : 'text-slate-300'
                    }`}
                  >
                    {optionText}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </main>

      {/* BOTTOM NAVIGATION FOOTER */}
      <footer className="border-t border-slate-800/80 bg-[#090E1A]/90 backdrop-blur-md px-6 py-4 sticky bottom-0 z-30">
        <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-30 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex items-center gap-3">
            {currentIndex === totalQuestions - 1 ? (
              <button
                onClick={handleSubmit}
                disabled={completeAttemptMutation.isPending}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-slate-950 font-black text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition-all"
              >
                {completeAttemptMutation.isPending ? (
                  <span>Evaluating Results...</span>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>Submit Assessment</span>
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 transition-all"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function DiagnosticRunnerPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#070B14] text-slate-400">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <DiagnosticRunnerContent />
    </Suspense>
  );
}
