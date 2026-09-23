'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  BrainCircuit,
  Plus,
  Sparkles,
  BookOpen,
  CheckCircle2,
  Clock,
  ArrowRight,
  HelpCircle,
  Award,
  FileText,
  Loader2,
} from 'lucide-react';
import { useQuizzes, useStartQuizAttempt } from '@/hooks/use-quizzes';
import { useMaterials } from '@/hooks/use-materials';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';

export default function QuizHubPage() {
  const router = useRouter();
  const { data: quizzes = [], isLoading: isLoadingQuizzes } = useQuizzes();
  const { data: materialsData } = useMaterials();
  const startAttempt = useStartQuizAttempt();

  const materials = materialsData?.items || [];

  const handleStartQuiz = (quizId: string) => {
    startAttempt.mutate(quizId, {
      onSuccess: (attempt) => {
        router.push(`/employee/quizzes/${quizId}?attemptId=${attempt.id}`);
      },
    });
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="AI Quizzes">
      <PageContainer>
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0A0E1A]/90 border border-indigo-500/20 p-6 rounded-2xl shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                PRAGYA AI Quiz Engine
                <span className="px-2.5 py-0.5 text-[10px] font-mono rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                  RAG Grounded
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Generate source-grounded MCQ assessments directly from MoSPI learning materials.
              </p>
            </div>
          </div>
        </div>

        <Link
          href="/employee/quizzes/generate"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-medium text-xs shadow-lg shadow-indigo-600/25 transition-all shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Generate New Quiz</span>
        </Link>
      </div>

      {/* Stats Overview Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Available Quizzes</div>
            <div className="text-lg font-bold text-white mt-0.5">{quizzes.length}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Source Materials</div>
            <div className="text-lg font-bold text-white mt-0.5">{materials.length}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Evidence Integration</div>
            <div className="text-lg font-bold text-white mt-0.5">Stage 5 Linked</div>
          </div>
        </div>
      </div>

      {/* Available Quizzes Grid */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          Ready Assessment Quizzes
        </h2>

        {isLoadingQuizzes ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-44 rounded-2xl bg-white/5 animate-pulse" />
            ))}
          </div>
        ) : quizzes.length === 0 ? (
          <div className="p-12 rounded-2xl bg-[#0A0E1A]/80 border border-white/10 text-center space-y-3">
            <HelpCircle className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-sm font-semibold text-white">No Quizzes Generated Yet</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Select an uploaded MoSPI document and generate custom competency-linked MCQs.
            </p>
            <Link
              href="/employee/quizzes/generate"
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create Your First Quiz</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quizzes.map((quiz) => (
              <div
                key={quiz.id}
                className="group relative flex flex-col justify-between p-5 rounded-2xl bg-[#0A0E1A]/90 border border-indigo-500/20 hover:border-indigo-500/50 transition-all hover:shadow-xl hover:shadow-indigo-500/10"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[10px] font-mono text-indigo-300">
                      {quiz.difficulty}
                    </span>
                    <span className="text-[11px] text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {quiz.question_count * 2} mins
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors line-clamp-1">
                      {quiz.title}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-2 mt-1 leading-relaxed">
                      {quiz.description || 'Grounded MCQ assessment derived from official materials.'}
                    </p>
                  </div>

                  {quiz.document_title && (
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-400 pt-1">
                      <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <span className="truncate">{quiz.document_title}</span>
                    </div>
                  )}
                </div>

                <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400 font-medium">
                    {quiz.question_count} Questions
                  </span>

                  <button
                    onClick={() => handleStartQuiz(quiz.id)}
                    disabled={startAttempt.isPending}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 border border-indigo-500/40 text-white text-xs font-medium transition-all disabled:opacity-50"
                  >
                    {startAttempt.isPending ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <>
                        <span>Start Practice</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}
