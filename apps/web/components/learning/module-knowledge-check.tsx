'use client';

import React, { useState } from 'react';
import {
  HelpCircle,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Sparkles,
  Loader2,
} from 'lucide-react';
import type { KnowledgeCheckResultResponse } from '@pragya/types';

interface QuestionItem {
  id: string;
  question: string;
  options: string[];
}

interface ModuleKnowledgeCheckProps {
  moduleId: number;
  title: string;
  questions: QuestionItem[];
  passThresholdPercentage?: number;
  isAlreadyPassed?: boolean;
  onCheckSubmit: (answers: Record<string, number>) => Promise<KnowledgeCheckResultResponse>;
}

export function ModuleKnowledgeCheck({
  moduleId,
  title,
  questions,
  passThresholdPercentage = 75.0,
  isAlreadyPassed = false,
  onCheckSubmit,
}: ModuleKnowledgeCheckProps) {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<KnowledgeCheckResultResponse | null>(null);

  const handleOptionSelect = (qId: string, optIdx: number) => {
    setSelectedAnswers((prev) => ({ ...prev, [qId]: optIdx }));
  };

  const handleSubmit = async () => {
    if (Object.keys(selectedAnswers).length < questions.length) {
      alert('Please answer all questions before submitting your Knowledge Check.');
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await onCheckSubmit(selectedAnswers);
      setResult(res);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Failed to submit Knowledge Check. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = () => {
    setSelectedAnswers({});
    setResult(null);
  };

  const allAnswered = Object.keys(selectedAnswers).length === questions.length;

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A]/95 p-6 md:p-8 space-y-6 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1">
              <HelpCircle className="w-3 h-3" />
              <span>MODULE {moduleId} KNOWLEDGE CHECK</span>
            </span>
            <span className="text-xs text-slate-400">Passing Score: {passThresholdPercentage}%</span>
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">{title}</h3>
        </div>

        {isAlreadyPassed && !result && (
          <div className="px-3 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shrink-0">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Passed in Previous Attempt</span>
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
                  <span className="text-white">Knowledge Check Passed!</span>
                </>
              ) : (
                <>
                  <XCircle className="w-5 h-5 text-rose-400" />
                  <span className="text-white">Score: {result.percentage}% — Needs Review</span>
                </>
              )}
            </div>
            <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700">
              {result.correct_answers} / {result.total_questions} Correct ({result.percentage}%)
            </span>
          </div>

          <p className="text-xs leading-relaxed text-slate-300">
            {result.passed
              ? 'Your score meets the competency threshold. This module learning evidence has been verified.'
              : `Minimum passing threshold is ${passThresholdPercentage}%. Review the feedback explanations below and retry the knowledge check.`}
          </p>

          {!result.passed && (
            <button
              onClick={handleRetry}
              className="mt-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-2 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry Knowledge Check</span>
            </button>
          )}
        </div>
      )}

      {/* Question List */}
      <div className="space-y-6">
        {questions.map((q, qIdx) => {
          const evalResult = result?.question_results?.find((r) => r.question_id === q.id);
          const hasResult = !!evalResult;

          return (
            <div
              key={q.id}
              className={`p-5 rounded-xl border transition-all ${
                hasResult
                  ? evalResult.is_correct
                    ? 'bg-slate-950/40 border-emerald-500/30'
                    : 'bg-slate-950/40 border-rose-500/30'
                  : 'bg-slate-950/50 border-slate-800'
              } space-y-4`}
            >
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-xs font-bold flex items-center justify-center text-indigo-400 shrink-0">
                  {qIdx + 1}
                </span>
                <p className="text-xs md:text-sm font-semibold text-white leading-snug pt-0.5">
                  {q.question}
                </p>
              </div>

              {/* Options */}
              <div className="space-y-2 pl-9">
                {q.options.map((opt, optIdx) => {
                  const isSelected = selectedAnswers[q.id] === optIdx;
                  let optStyle = 'border-slate-800 bg-slate-900/60 hover:border-slate-700 text-slate-300';

                  if (hasResult) {
                    if (evalResult.correct_index === optIdx) {
                      optStyle = 'border-emerald-500/60 bg-emerald-950/30 text-emerald-200 font-semibold';
                    } else if (isSelected && !evalResult.is_correct) {
                      optStyle = 'border-rose-500/60 bg-rose-950/30 text-rose-200 line-through';
                    }
                  } else if (isSelected) {
                    optStyle = 'border-indigo-500 bg-indigo-950/30 text-indigo-200 font-semibold';
                  }

                  return (
                    <label
                      key={optIdx}
                      className={`flex items-center gap-3 p-3 rounded-xl border text-xs cursor-pointer transition ${optStyle}`}
                    >
                      <input
                        type="radio"
                        name={q.id}
                        value={optIdx}
                        checked={isSelected}
                        disabled={hasResult && !!result?.passed}
                        onChange={() => handleOptionSelect(q.id, optIdx)}
                        className="accent-indigo-500"
                      />
                      <span className="leading-snug">{opt}</span>
                    </label>
                  );
                })}
              </div>

              {/* Explanation note when evaluated */}
              {hasResult && evalResult.explanation && (
                <div className="mt-3 ml-9 p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 space-y-1">
                  <div className="font-bold flex items-center gap-1.5 text-indigo-400">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Technical Reference & Rationale</span>
                  </div>
                  <p className="leading-relaxed text-slate-400">{evalResult.explanation}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Submit Action Bar */}
      {(!result || !result.passed) && (
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-4">
          <span className="text-xs text-slate-400">
            {allAnswered ? 'All questions answered' : `${Object.keys(selectedAnswers).length} of ${questions.length} answered`}
          </span>
          <button
            onClick={handleSubmit}
            disabled={!allAnswered || isSubmitting}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-950/50"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            <span>Submit Knowledge Check</span>
          </button>
        </div>
      )}
    </div>
  );
}
