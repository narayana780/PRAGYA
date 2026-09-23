'use client';

import React, { use } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  Award,
  CheckCircle2,
  XCircle,
  Sparkles,
  FileText,
  ArrowLeft,
  ArrowRight,
  RotateCcw,
  Loader2,
  BrainCircuit,
} from 'lucide-react';
import { useQuizResult, useQuizReview } from '@/hooks/use-quizzes';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';

export default function QuizResultPage({
  params: paramsPromise,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: quizId } = use(paramsPromise);
  const searchParams = useSearchParams();
  const attemptId = searchParams.get('attemptId') || '';

  const { data: result, isLoading: isLoadingResult } = useQuizResult(attemptId);
  const { data: review, isLoading: isLoadingReview } = useQuizReview(attemptId);

  if (isLoadingResult || isLoadingReview || !result || !review) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Quiz Results & Analytics">
        <PageContainer>
          <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <span className="text-xs text-slate-400">Calculating assessment results & citations...</span>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const isPassed = result.percentage >= 70;

  return (
    <AppShell role="EMPLOYEE" pageTitle="Quiz Results & Analytics">
      <PageContainer>
        <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex items-center justify-between gap-4">
        <Link
          href="/employee/quizzes"
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-medium transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Quizzes</span>
        </Link>

        <Link
          href={`/employee/quizzes/${quizId}`}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Retake Quiz</span>
        </Link>
      </div>

      {/* Score Overview Card */}
      <div className="p-6 rounded-2xl bg-[#0A0E1A]/95 border border-indigo-500/20 shadow-2xl space-y-6 backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-white/10">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Quiz Assessment Result</h1>
                <p className="text-xs text-slate-400">
                  Performance recorded into Stage 5 Assessment Evidence history.
                </p>
              </div>
            </div>

            {result.competencies_tested.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap pt-2">
                <span className="text-[11px] text-slate-400">Competencies Tested:</span>
                {result.competencies_tested.map((c) => (
                  <span
                    key={c}
                    className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-[10px] font-mono text-cyan-300"
                  >
                    {c}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className={`text-3xl font-black ${isPassed ? 'text-emerald-400' : 'text-amber-400'}`}>
                {result.percentage}%
              </div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
                Final Score
              </div>
            </div>

            <div className="h-10 w-px bg-white/10" />

            <div className="text-center">
              <div className="text-2xl font-bold text-white">
                {result.score} / {result.total_questions}
              </div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
                Correct Answers
              </div>
            </div>
          </div>
        </div>

        {/* Stage 11: Adaptive Reassessment CTA Banner */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-950/30 via-slate-900 to-indigo-950/30 border border-cyan-500/30 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <BrainCircuit className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-cyan-300">Ready to recalibrate your competency score?</div>
              <div className="text-[11px] text-slate-400">Validate and update your demonstrated level with multi-difficulty adaptive testing.</div>
            </div>
          </div>
          <Link
            href="/employee/adaptive-assessment"
            className="px-3.5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs flex items-center gap-1.5 transition whitespace-nowrap shadow-md shadow-cyan-950/40"
          >
            <span>Start Adaptive Reassessment</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Detailed Question Review */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Detailed Question Review & Material Citations
          </h2>

          <div className="space-y-4">
            {review.items.map((item, idx) => {
              const selectedOpt = item.options.find((o) => o.id === item.selected_option_id);
              const correctOpt = item.options.find((o) => o.id === item.correct_option_id);

              return (
                <div
                  key={item.question_id}
                  className="p-5 rounded-xl bg-white/[0.02] border border-white/10 space-y-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-white/10 text-white text-xs font-mono flex items-center justify-center shrink-0">
                        {idx + 1}
                      </span>
                      <h3 className="text-xs font-semibold text-white leading-relaxed">
                        {item.question_text}
                      </h3>
                    </div>

                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-medium flex items-center gap-1 shrink-0 ${
                        item.is_correct
                          ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                          : 'bg-red-500/10 border border-red-500/20 text-red-400'
                      }`}
                    >
                      {item.is_correct ? (
                        <>
                          <CheckCircle2 className="w-3 h-3" /> Correct
                        </>
                      ) : (
                        <>
                          <XCircle className="w-3 h-3" /> Incorrect
                        </>
                      )}
                    </span>
                  </div>

                  {/* Answers summary */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">
                    <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/5">
                      <span className="text-[10px] text-slate-400 block font-mono">YOUR ANSWER</span>
                      <span className={item.is_correct ? 'text-emerald-300 font-medium' : 'text-red-300 font-medium'}>
                        {selectedOpt?.option_text || 'None selected'}
                      </span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-emerald-500/[0.05] border border-emerald-500/20">
                      <span className="text-[10px] text-emerald-400 block font-mono">CORRECT ANSWER</span>
                      <span className="text-emerald-200 font-medium">
                        {correctOpt?.option_text || 'Correct Option'}
                      </span>
                    </div>
                  </div>

                  {/* Grounded Explanation */}
                  <div className="p-3 rounded-lg bg-indigo-500/5 border border-indigo-500/20 text-xs text-slate-300 leading-relaxed">
                    <span className="font-semibold text-indigo-300 block mb-0.5">Explanation:</span>
                    {item.explanation}
                  </div>

                  {/* Citation Footer */}
                  {item.source_document_title && (
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5 pt-1">
                      <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <span>
                        Source Material: {item.source_document_title}
                        {item.source_page_number ? ` — Page ${item.source_page_number}` : ''}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  </PageContainer>
</AppShell>
);
}
