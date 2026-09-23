'use client';

import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  Sparkles,
  RotateCcw,
  Loader2,
  Lock,
  Award,
} from 'lucide-react';
import type { FinalAssessmentResultResponse } from '@pragya/types';

interface FinalAssessmentQuestion {
  id: string;
  question: string;
  options: string[];
  explanation?: string;
}

interface FinalAssessmentData {
  title?: string;
  description?: string;
  pass_threshold_percentage?: number;
  questions?: FinalAssessmentQuestion[];
}

interface CourseFinalAssessmentProps {
  assessmentData?: FinalAssessmentData | null;
  isUnlocked: boolean;
  isAlreadyPassed?: boolean;
  score?: number | null;
  onAssessmentSubmit: (answers: Record<string, number>) => Promise<FinalAssessmentResultResponse>;
}

export function CourseFinalAssessment({
  assessmentData,
  isUnlocked,
  isAlreadyPassed = false,
  score,
  onAssessmentSubmit,
}: CourseFinalAssessmentProps) {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<FinalAssessmentResultResponse | null>(null);

  const questions = assessmentData?.questions || [];
  const threshold = assessmentData?.pass_threshold_percentage || 70.0;

  const handleOptionSelect = (qId: string, optIdx: number) => {
    setSelectedAnswers((prev) => ({ ...prev, [qId]: optIdx }));
  };

  const handleSubmit = async () => {
    if (Object.keys(selectedAnswers).length < questions.length) {
      alert('Please answer all questions before submitting the final course assessment.');
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await onAssessmentSubmit(selectedAnswers);
      setResult(res);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Failed to submit final assessment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = () => {
    setSelectedAnswers({});
    setResult(null);
  };

  if (!isUnlocked) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A]/60 p-12 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 text-slate-500 mx-auto flex items-center justify-center">
          <Lock className="w-6 h-6" />
        </div>
        <div className="space-y-1 max-w-md mx-auto">
          <h3 className="text-base font-bold text-slate-200">Final Assessment Locked</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            You must complete all foundational learning modules (Modules 1, 2, and 3) including their knowledge checks and assignments to unlock the comprehensive final assessment.
          </p>
        </div>
      </div>
    );
  }

  const allAnswered = Object.keys(selectedAnswers).length === questions.length;

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A]/95 p-6 md:p-8 space-y-6 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 flex items-center gap-1">
              <Award className="w-3 h-3" />
              <span>ACADEMIC CERTIFICATION ASSESSMENT</span>
            </span>
            <span className="text-xs text-slate-400">Pass Threshold: {threshold}%</span>
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">
            {assessmentData?.title || 'Final Course Comprehensive Assessment'}
          </h3>
          <p className="text-xs text-slate-400">
            {assessmentData?.description || 'Evaluates understanding across Foundations, Sampling Design, and Quality Assurance.'}
          </p>
        </div>

        {isAlreadyPassed && !result && (
          <div className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shrink-0">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Passed ({score ?? 100}%)</span>
          </div>
        )}
      </div>

      {/* Result Card if submitted */}
      {result && (
        <div
          className={`p-5 rounded-2xl border transition-all ${
            result.passed
              ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200'
              : 'bg-rose-950/20 border-rose-500/30 text-rose-200'
          } space-y-3`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-sm">
              {result.passed ? (
                <>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-white">Assessment Passed! Certification Credited.</span>
                </>
              ) : (
                <>
                  <XCircle className="w-5 h-5 text-rose-400" />
                  <span className="text-white">Score: {result.percentage}% — Pass Threshold Not Met</span>
                </>
              )}
            </div>
            <span className="font-mono text-xs font-bold px-3 py-1 rounded-lg bg-slate-900 border border-slate-700">
              {result.correct_answers} / {result.total_questions} Correct ({result.percentage}%)
            </span>
          </div>

          <p className="text-xs leading-relaxed text-slate-300">
            {result.passed
              ? 'You have successfully passed the final assessment! Combined with your practical Virtual Lab simulation, your course learning requirements are complete.'
              : `Minimum passing threshold is ${threshold}%. Review the questions below and retry.`}
          </p>

          {!result.passed && (
            <button
              onClick={handleRetry}
              className="mt-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-2 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry Final Assessment</span>
            </button>
          )}
        </div>
      )}

      {/* Questions */}
      <div className="space-y-6">
        {questions.map((q: FinalAssessmentQuestion, qIdx: number) => {
          const evalRes = result?.question_results?.find((r) => r.question_id === q.id);
          const hasEval = !!evalRes;

          return (
            <div
              key={q.id}
              className={`p-5 rounded-xl border transition-all ${
                hasEval
                  ? evalRes.is_correct
                    ? 'bg-slate-950/40 border-emerald-500/30'
                    : 'bg-slate-950/40 border-rose-500/30'
                  : 'bg-slate-950/50 border-slate-800'
              } space-y-4`}
            >
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-xs font-bold flex items-center justify-center text-emerald-400 shrink-0">
                  {qIdx + 1}
                </span>
                <p className="text-xs md:text-sm font-semibold text-white leading-snug pt-0.5">
                  {q.question}
                </p>
              </div>

              <div className="space-y-2 pl-9">
                {q.options.map((opt: string, optIdx: number) => {
                  const isSelected = selectedAnswers[q.id] === optIdx;
                  let optStyle = 'border-slate-800 bg-slate-900/60 hover:border-slate-700 text-slate-300';

                  if (hasEval) {
                    if (evalRes.correct_index === optIdx) {
                      optStyle = 'border-emerald-500/60 bg-emerald-950/30 text-emerald-200 font-semibold';
                    } else if (isSelected && !evalRes.is_correct) {
                      optStyle = 'border-rose-500/60 bg-rose-950/30 text-rose-200 line-through';
                    }
                  } else if (isSelected) {
                    optStyle = 'border-emerald-500 bg-emerald-950/30 text-emerald-200 font-semibold';
                  }

                  return (
                    <label
                      key={optIdx}
                      className={`flex items-center gap-3 p-3 rounded-xl border text-xs cursor-pointer transition ${optStyle}`}
                    >
                      <input
                        type="radio"
                        name={`final-${q.id}`}
                        value={optIdx}
                        checked={isSelected}
                        disabled={hasEval && !!result?.passed}
                        onChange={() => handleOptionSelect(q.id, optIdx)}
                        className="accent-emerald-500"
                      />
                      <span className="leading-snug">{opt}</span>
                    </label>
                  );
                })}
              </div>

              {hasEval && evalRes.explanation && (
                <div className="mt-3 ml-9 p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 space-y-1">
                  <div className="font-bold flex items-center gap-1.5 text-emerald-400">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Official MoSPI Methodological Reference</span>
                  </div>
                  <p className="leading-relaxed text-slate-400">{evalRes.explanation}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action Bar */}
      {(!result || !result.passed) && (
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-4">
          <span className="text-xs text-slate-400">
            {allAnswered ? 'All questions answered' : `${Object.keys(selectedAnswers).length} of ${questions.length} answered`}
          </span>
          <button
            onClick={handleSubmit}
            disabled={!allAnswered || isSubmitting}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-emerald-950/50"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            <span>Submit Final Examination</span>
          </button>
        </div>
      )}
    </div>
  );
}
