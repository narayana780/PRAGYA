'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  BrainCircuit,
  ArrowLeft,
  Sparkles,
  FileText,
  Sliders,
  Award,
  Layers,
  Loader2,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { useGenerateQuiz } from '@/hooks/use-quizzes';
import { useMaterials } from '@/hooks/use-materials';
import { useCompetencies } from '@/hooks/use-competency';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';
import type { QuizDifficulty, BloomLevel, UploadedMaterial, CompetencySummary } from '@pragya/types';

export default function QuizGeneratePage() {
  const router = useRouter();
  const generateQuizMutation = useGenerateQuiz();
  const { data: materialsData } = useMaterials();
  const { data: competenciesData } = useCompetencies();

  const materials: UploadedMaterial[] = materialsData?.items || [];
  const competencies: CompetencySummary[] = competenciesData?.items || [];

  const [selectedMaterialId, setSelectedMaterialId] = useState<string>('');
  const [selectedCompetencyId, setSelectedCompetencyId] = useState<string>('');
  const [difficulty, setDifficulty] = useState<QuizDifficulty>('BEGINNER');
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [bloomLevel, setBloomLevel] = useState<BloomLevel | ''>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = () => {
    setErrorMsg(null);

    generateQuizMutation.mutate(
      {
        material_id: selectedMaterialId || undefined,
        competency_id: selectedCompetencyId || undefined,
        difficulty,
        question_count: questionCount,
        bloom_level: (bloomLevel as BloomLevel) || undefined,
      },
      {
        onSuccess: (newQuiz) => {
          router.push(`/employee/quizzes/${newQuiz.id}`);
        },
        onError: (err) => {
          setErrorMsg(err.message || 'Quiz generation failed. Please try again.');
        },
      }
    );
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Generate AI Quiz">
      <PageContainer>
        <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Top Breadcrumb Header */}
      <div className="flex items-center gap-3">
        <Link
          href="/employee/quizzes"
          className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            Generate AI Learning Quiz
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </h1>
          <p className="text-xs text-slate-400">
            Create source-grounded, competency-mapped assessments from official materials.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Generation Form Card */}
      <div className="p-6 rounded-2xl bg-[#0A0E1A]/95 border border-indigo-500/20 shadow-2xl space-y-6 backdrop-blur-md">
        {/* Step 1: Select Source Material */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-white tracking-tight flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            1. Select Learning Material (RAG Source)
          </label>

          <select
            value={selectedMaterialId}
            onChange={(e) => setSelectedMaterialId(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/10 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
          >
            <option value="" className="bg-[#0A0E1A]">
              -- Select Uploaded MoSPI Material (Default to latest) --
            </option>
            {materials.map((mat) => (
              <option key={mat.id} value={mat.id} className="bg-[#0A0E1A]">
                {mat.original_filename} ({mat.status})
              </option>
            ))}
          </select>
          <p className="text-[11px] text-slate-500">
            Questions are generated strictly using retrieved content chunks from the selected document.
          </p>
        </div>

        {/* Step 2: Target Competency (Optional) */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-white tracking-tight flex items-center gap-2">
            <Award className="w-4 h-4 text-indigo-400" />
            2. Target Competency (Optional)
          </label>

          <select
            value={selectedCompetencyId}
            onChange={(e) => setSelectedCompetencyId(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/10 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
          >
            <option value="" className="bg-[#0A0E1A]">
              -- None (General Assessment) --
            </option>
            {competencies.map((c) => (
              <option key={c.id} value={c.id} className="bg-[#0A0E1A]">
                {c.name} ({c.code})
              </option>
            ))}
          </select>
        </div>

        {/* Step 3: Difficulty & Question Count */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-white/5">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white tracking-tight flex items-center gap-2">
              <Sliders className="w-4 h-4 text-emerald-400" />
              Target Difficulty
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['BEGINNER', 'INTERMEDIATE', 'ADVANCED'] as QuizDifficulty[]).map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDifficulty(d)}
                  className={`py-2 rounded-xl text-xs font-medium border transition-all ${
                    difficulty === d
                      ? 'bg-indigo-600/30 border-indigo-500 text-white shadow-md'
                      : 'bg-white/[0.02] border-white/10 text-slate-400 hover:bg-white/5'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-white tracking-tight flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-indigo-400" />
              Number of Questions
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[5, 10, 15, 20].map((count) => (
                <button
                  key={count}
                  type="button"
                  onClick={() => setQuestionCount(count)}
                  className={`py-2 rounded-xl text-xs font-medium border transition-all ${
                    questionCount === count
                      ? 'bg-indigo-600/30 border-indigo-500 text-white shadow-md'
                      : 'bg-white/[0.02] border-white/10 text-slate-400 hover:bg-white/5'
                  }`}
                >
                  {count} Qs
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Step 4: Bloom Taxonomy Level (Optional) */}
        <div className="space-y-2 pt-2 border-t border-white/5">
          <label className="text-xs font-semibold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-4 h-4 text-amber-400" />
            Bloom Taxonomy Focus (Optional)
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              { id: '', label: 'AUTO (Balanced)' },
              { id: 'REMEMBER', label: 'REMEMBER' },
              { id: 'UNDERSTAND', label: 'UNDERSTAND' },
              { id: 'APPLY', label: 'APPLY' },
            ].map((b) => (
              <button
                key={b.id}
                type="button"
                onClick={() => setBloomLevel(b.id as BloomLevel | '')}
                className={`py-2 rounded-xl text-xs font-medium border transition-all ${
                  bloomLevel === b.id
                    ? 'bg-amber-500/20 border-amber-500/50 text-amber-200'
                    : 'bg-white/[0.02] border-white/10 text-slate-400 hover:bg-white/5'
                }`}
              >
                {b.label}
              </button>
            ))}
          </div>
        </div>

        {/* Generate CTA Button */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between">
          <div className="text-[11px] text-slate-500 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Strict prompt injection defense & grounding verification active</span>
          </div>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={generateQuizMutation.isPending}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
          >
            {generateQuizMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Extracting Concepts & Generating MCQs...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Source-Grounded Quiz</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  </PageContainer>
</AppShell>
);
}
