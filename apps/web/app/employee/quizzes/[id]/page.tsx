'use client';

import React, { useState, useEffect, use } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Sparkles,
  FileText,
  ArrowRight,
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  useQuiz,
  useStartQuizAttempt,
  useSubmitQuizAnswer,
  useCompleteQuizAttempt,
} from '@/hooks/use-quizzes';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';
import type { AnswerResponse } from '@pragya/types';

export default function QuizPlayerPage({
  params: paramsPromise,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: quizId } = use(paramsPromise);
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialAttemptId = searchParams.get('attemptId');

  const [attemptId, setAttemptId] = useState<string | null>(initialAttemptId);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [selectedOptionId, setSelectedOptionId] = useState<string>('');
  const [feedback, setFeedback] = useState<AnswerResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: quiz, isLoading: isLoadingQuiz } = useQuiz(quizId);
  const startAttemptMutation = useStartQuizAttempt();
  const submitAnswerMutation = useSubmitQuizAnswer(attemptId || '');
  const completeAttemptMutation = useCompleteQuizAttempt(attemptId || '');

  // Initialize attempt if not passed in search params
  useEffect(() => {
    if (!attemptId && quizId && !startAttemptMutation.isPending) {
      startAttemptMutation.mutate(quizId, {
        onSuccess: (attempt) => {
          setAttemptId(attempt.id);
        },
        onError: (err) => {
          setErrorMsg(err.message || 'Failed to start quiz attempt.');
        },
      });
    }
  }, [quizId, attemptId]);

  if (isLoadingQuiz || !quiz) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Active Quiz Assessment">
        <PageContainer>
          <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <span className="text-xs text-slate-400">Loading quiz questions...</span>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const questions = quiz.questions || [];
  const currentQuestion = questions[currentQuestionIndex];
  const totalQuestions = questions.length;
  const isLastQuestion = currentQuestionIndex === totalQuestions - 1;

  const handleOptionSelect = (optId: string) => {
    if (feedback) return; // Locked after submission
    setSelectedOptionId(optId);
  };

  const handleSubmitAnswer = () => {
    if (!selectedOptionId || !currentQuestion || !attemptId || submitAnswerMutation.isPending) return;

    setErrorMsg(null);
    submitAnswerMutation.mutate(
      {
        question_id: currentQuestion.id,
        selected_option_id: selectedOptionId,
      },
      {
        onSuccess: (res) => {
          setFeedback(res);
        },
        onError: (err) => {
          setErrorMsg(err.message || 'Failed to submit answer.');
        },
      }
    );
  };

  const handleNextQuestion = () => {
    if (!feedback) return;

    if (isLastQuestion) {
      // Complete attempt
      completeAttemptMutation.mutate(undefined, {
        onSuccess: () => {
          router.push(`/employee/quizzes/${quizId}/result?attemptId=${attemptId}`);
        },
        onError: (err) => {
          setErrorMsg(err.message || 'Failed to complete attempt.');
        },
      });
    } else {
      setCurrentQuestionIndex((prev) => prev + 1);
      setSelectedOptionId('');
      setFeedback(null);
    }
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Active Quiz Assessment">
      <PageContainer>
        <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Top Header & Progress Bar */}
      <div className="bg-[#0A0E1A]/95 border border-indigo-500/20 p-5 rounded-2xl shadow-xl backdrop-blur-md space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link
              href="/employee/quizzes"
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-base font-bold text-white tracking-tight line-clamp-1">
                {quiz.title}
              </h1>
              <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                  {currentQuestion?.difficulty || quiz.difficulty}
                </span>
                <span>•</span>
                <span>Bloom: {currentQuestion?.bloom_level || 'REMEMBER'}</span>
              </div>
            </div>
          </div>

          <div className="text-right shrink-0">
            <div className="text-xs font-mono font-semibold text-white">
              Question {currentQuestionIndex + 1} / {totalQuestions}
            </div>
            <div className="text-[10px] text-slate-400">RAG Grounded</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / totalQuestions) * 100}%` }}
          />
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Question Display Card */}
      {currentQuestion ? (
        <div className="p-6 rounded-2xl bg-[#0A0E1A]/95 border border-indigo-500/20 shadow-2xl space-y-6 backdrop-blur-md">
          {/* Question Text */}
          <div className="space-y-2">
            <div className="text-[11px] font-mono text-indigo-400 uppercase tracking-wider">
              {currentQuestion.question_type}
            </div>
            <h2 className="text-base font-semibold text-white leading-relaxed">
              {currentQuestion.question_text}
            </h2>
          </div>

          {/* Options List */}
          <div className="space-y-3">
            {currentQuestion.options.map((opt) => {
              const isSelected = selectedOptionId === opt.id;
              let optStyle =
                'bg-white/[0.03] border-white/10 text-slate-300 hover:bg-white/[0.06] hover:border-white/20';

              if (feedback) {
                if (opt.id === feedback.correct_option_id) {
                  optStyle = 'bg-emerald-500/20 border-emerald-500/50 text-emerald-200 font-medium';
                } else if (isSelected && !feedback.is_correct) {
                  optStyle = 'bg-red-500/20 border-red-500/50 text-red-200 font-medium';
                } else {
                  optStyle = 'bg-white/[0.02] border-white/5 text-slate-500 opacity-60';
                }
              } else if (isSelected) {
                optStyle = 'bg-indigo-600/25 border-indigo-500/50 text-white font-medium shadow-md';
              }

              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => handleOptionSelect(opt.id)}
                  disabled={!!feedback}
                  className={`w-full p-4 rounded-xl text-xs text-left border transition-all flex items-center justify-between group ${optStyle}`}
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full border border-white/20 flex items-center justify-center text-[11px] font-mono shrink-0 group-hover:border-indigo-400">
                      {String.fromCharCode(65 + opt.option_order - 1)}
                    </span>
                    <span>{opt.option_text}</span>
                  </div>

                  {feedback && opt.id === feedback.correct_option_id && (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  )}
                  {feedback && isSelected && !feedback.is_correct && (
                    <XCircle className="w-4 h-4 text-red-400 shrink-0" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Instant Feedback & Citation Panel */}
          {feedback && (
            <div
              className={`p-4 rounded-xl border space-y-2 ${
                feedback.is_correct
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-200'
              }`}
            >
              <div className="flex items-center gap-2 text-xs font-semibold">
                {feedback.is_correct ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Correct Answer!</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-4 h-4 text-amber-400" />
                    <span>Incorrect</span>
                  </>
                )}
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{feedback.explanation}</p>

              {feedback.citation && (
                <div className="text-[11px] text-slate-400 flex items-center gap-1.5 pt-1 border-t border-white/10">
                  <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span>
                    Source: {feedback.citation.document_title || 'Material Document'}
                    {feedback.citation.page_number ? ` — Page ${feedback.citation.page_number}` : ''}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="pt-4 border-t border-white/10 flex items-center justify-between">
            <div className="text-[11px] text-slate-500">
              {feedback ? 'Review explanation then proceed to next question' : 'Select your answer to proceed'}
            </div>

            {!feedback ? (
              <button
                type="button"
                onClick={handleSubmitAnswer}
                disabled={!selectedOptionId || submitAnswerMutation.isPending}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
              >
                {submitAnswerMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>Submit Answer</span>
                    <Sparkles className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleNextQuestion}
                disabled={completeAttemptMutation.isPending}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-semibold text-xs shadow-lg shadow-emerald-600/30 transition-all disabled:opacity-50"
              >
                {completeAttemptMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>{isLastQuestion ? 'Complete Quiz' : 'Next Question'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="p-12 text-center text-slate-400">No questions found for this quiz.</div>
      )}
        </div>
      </PageContainer>
    </AppShell>
  );
}
