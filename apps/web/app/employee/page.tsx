'use client';

import React from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { AIOrb } from '@/components/ui/ai-orb';
import { Sparkles, BookOpen, Target, Award, ArrowRight, ShieldAlert, CheckCircle, BrainCircuit, FlaskConical } from 'lucide-react';
import Link from 'next/link';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useSkillGapSummary } from '@/hooks/use-skill-gaps';
import { useRecommendations } from '@/hooks/use-recommendations';
import { useRecentQuizScore } from '@/hooks/use-quizzes';
import { useEmployeeCompetencies } from '@/hooks/use-assessment';
import { useLabScenarios, useMyLabSessions } from '@/hooks/use-labs';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { CurrentVsRequiredBar } from '@/components/gaps/current-vs-required-bar';
import { ProviderBadge } from '@/components/learning/provider-badge';

export default function EmployeeHomePage() {
  const { data: employee } = useCurrentEmployee();
  const { data: summary } = useSkillGapSummary(employee?.id);
  const { data: recommendations } = useRecommendations(employee?.id);
  const { data: recentQuizScore } = useRecentQuizScore();
  const { data: employeeCompetencies = [] } = useEmployeeCompetencies(employee?.id);
  const { data: labs = [] } = useLabScenarios();
  const { data: myLabSessions = [] } = useMyLabSessions(employee?.id);
  const completedLabs = myLabSessions.filter((s) => s.status === 'COMPLETED');
  const lastCompletedLab = completedLabs[0] || null;
  const topGap = summary?.highest_priority_gap;
  const topRec = recommendations && recommendations.length > 0 ? recommendations[0] : null;

  const targetComp = topGap
    ? {
        id: topGap.competency_id,
        name: topGap.competency_name,
        level: `Level ${topGap.current_level_number} (${topGap.current_level_name})`,
        score: topGap.current_score,
        confidence: topGap.confidence,
      }
    : employeeCompetencies.length > 0
    ? {
        id: employeeCompetencies[0].competency_id,
        name: employeeCompetencies[0].competency_name || 'Statistical Competency',
        level: employeeCompetencies[0].proficiency_level_name,
        score: employeeCompetencies[0].current_score,
        confidence: employeeCompetencies[0].confidence,
      }
    : {
        id: '',
        name: 'Official Statistics',
        level: 'Beginner',
        score: 0,
        confidence: 0.5,
      };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Learner Workspace">
      <PageContainer>
        <PageHeader
          title="Your personalized learning workspace"
          subtitle="Build the skills your role needs, one step at a time."
          badge={
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
              Active Cadre
            </span>
          }
        />

        {/* Foundation Welcome Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <GlassCard variant="glow" className="lg:col-span-2 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-medium">
                <Sparkles className="w-4 h-4" />
                <span>EVIDENCE-BASED COMPETENCY ENGINE</span>
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Capacity Building for India&apos;s Official Statistical System
              </h2>
              <p className="text-xs md:text-sm text-slate-300 leading-relaxed max-w-xl">
                PRAGYA links your daily statistical role with diagnostic assessment, verified learning from iGOT & NSSTA, and real-time recalibration to keep your competencies ahead.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-6 mt-4 border-t border-white/5">
              <Link
                href="/employee/competency"
                className="p-3 rounded-xl bg-white/5 hover:bg-cyan-500/10 border border-white/5 hover:border-cyan-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <Award className="w-4 h-4 text-cyan-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">Competency Profile</div>
                <div className="text-[11px] text-slate-400">View domains & criteria</div>
              </Link>

              <Link
                href="/employee/gaps"
                className="p-3 rounded-xl bg-white/5 hover:bg-violet-500/10 border border-white/5 hover:border-violet-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <Target className="w-4 h-4 text-violet-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">Skill Gap Analysis</div>
                <div className="text-[11px] text-slate-400">
                  {summary ? `${summary.gaps_count} active gaps` : 'Target role requirements'}
                </div>
              </Link>

              <Link
                href="/employee/learning"
                className="p-3 rounded-xl bg-white/5 hover:bg-emerald-500/10 border border-white/5 hover:border-emerald-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <BookOpen className="w-4 h-4 text-emerald-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">Learning Pathway</div>
                <div className="text-[11px] text-slate-400">Prioritized modules</div>
              </Link>

              <Link
                href="/employee/quizzes"
                className="p-3 rounded-xl bg-white/5 hover:bg-indigo-500/10 border border-white/5 hover:border-indigo-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">AI Quizzes</div>
                <div className="text-[11px] text-slate-400">Source-grounded MCQs</div>
              </Link>
            </div>
          </GlassCard>

          {/* AI Learning Assistant Teaser Card */}
          <GlassCard variant="elevated" className="flex flex-col items-center text-center justify-between p-6">
            <div className="flex flex-col items-center space-y-3">
              <AIOrb size="lg" />
              <h3 className="text-base font-bold text-white tracking-tight">
                AI Statistical Assistant
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Grounded learning assistance powered by verified official statistical guidelines, MoSPI methodologies, and survey frameworks.
              </p>
            </div>

            <Link
              href="/employee/assistant"
              className="mt-6 w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-medium text-xs shadow-lg shadow-violet-500/20 text-center transition-all"
            >
              Open Assistant Shell
            </Link>
          </GlassCard>
        </div>

        {/* AI Quizzes Card / Quick Action */}
        <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/30 p-6 shadow-xl space-y-4 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-3 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <span className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-inner">
                <BrainCircuit className="w-5 h-5 text-indigo-400" />
              </span>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                  <span>Interactive Assessment</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/25">
                    RAG Grounded
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                  AI Quizzes
                </h3>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <Link
                href="/employee/quizzes/generate"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 font-medium text-xs transition"
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                <span>Generate Quiz</span>
              </Link>
              <Link
                href="/employee/quizzes"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-xs transition shadow-md shadow-indigo-900/40"
              >
                <span>Open Quiz Hub</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
            <div className="md:col-span-8 space-y-2">
              <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                Test your understanding using your learning materials
              </p>
              <div className="text-xs text-slate-400 flex flex-wrap items-center gap-3">
                <span className="flex items-center gap-1.5 text-slate-400">
                  <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                  Generated from MoSPI & Official Survey Documents
                </span>
                <span className="text-slate-600">•</span>
                <span className="flex items-center gap-1.5 text-slate-400">
                  <Award className="w-3.5 h-3.5 text-emerald-400" />
                  Directly linked to Competency Evidence
                </span>
              </div>
            </div>

            <div className="md:col-span-4 flex md:justify-end">
              {recentQuizScore ? (
                <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-indigo-500/20 w-full md:w-auto">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-[11px] font-medium text-slate-400">Recent Quiz Score</div>
                    <div className="flex items-baseline gap-1.5">
                      <span className="text-base font-bold text-emerald-400 font-mono">
                        {recentQuizScore.percentage.toFixed(0)}%
                      </span>
                      <span className="text-[11px] text-slate-400 truncate max-w-[140px]" title={recentQuizScore.quizTitle}>
                        ({recentQuizScore.quizTitle})
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/5 w-full md:w-auto">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-[11px] font-medium text-slate-400">Recent Quiz Score</div>
                    <div className="text-xs text-slate-400 italic">
                      No attempts yet — ready for practice
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Compact Adaptive Assessment Card */}
        <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-cyan-950/25 to-slate-900 border border-cyan-500/30 p-5 shadow-xl mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-inner">
                <BrainCircuit className="w-5 h-5 text-cyan-400" />
              </span>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                  <span>Adaptive Assessment</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/25">
                    CAT Reassessment
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5 max-w-xl">
                  Reassess a competency and measure how your demonstrated level has changed.
                </p>
              </div>
            </div>

            <Link
              href={targetComp.id ? `/employee/adaptive-assessment?competencyId=${targetComp.id}` : '/employee/adaptive-assessment'}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white font-semibold text-xs transition shadow-md shadow-cyan-950/40 whitespace-nowrap self-start sm:self-auto"
            >
              <span>Start Assessment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 mt-3 border-t border-slate-800 text-xs">
            <div>
              <span className="text-slate-500 text-[10px] block uppercase font-bold">Current focus competency</span>
              <span className="font-semibold text-slate-200 truncate block" title={targetComp.name}>
                {targetComp.name}
              </span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block uppercase font-bold">Current score</span>
              <span className="font-semibold text-cyan-300 font-mono">
                {targetComp.score !== undefined ? `${targetComp.score.toFixed(1)} / 100` : 'Not yet scored'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block uppercase font-bold">Last assessment</span>
              <span className="font-semibold text-slate-300">
                Verified Evidence
              </span>
            </div>
          </div>
        </div>

        {/* Compact Virtual Labs Card */}
        <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-violet-950/30 to-slate-900 border border-violet-500/30 p-5 shadow-xl mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="p-2.5 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 shadow-inner">
                <FlaskConical className="w-5 h-5 text-violet-400" />
              </span>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-violet-400 flex items-center gap-1.5">
                  <span>Interactive Simulation</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-violet-500/10 text-violet-300 border border-violet-500/25">
                    Practice Sandbox
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-100">
                  PRAGYA Statistical Virtual Lab
                </h3>
              </div>
            </div>

            <Link
              href="/employee/labs"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs transition shadow-md shadow-violet-900/40 shrink-0"
            >
              <span>Open Virtual Labs</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-4 mt-4 border-t border-slate-800/80">
            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-[11px] font-medium text-slate-400">Available Labs</div>
              <div className="text-base font-bold text-white font-mono mt-0.5">{labs.length || 4} Scenarios</div>
              <div className="text-[11px] text-slate-500">Sampling, Quality & Stats</div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-[11px] font-medium text-slate-400">Last Completed Lab</div>
              <div className="text-xs font-semibold text-slate-200 truncate mt-1">
                {lastCompletedLab ? lastCompletedLab.scenario_title : 'None completed yet'}
              </div>
              <div className="text-[11px] text-emerald-400 font-mono">
                {lastCompletedLab ? `${lastCompletedLab.percentage}% Verified` : '0 Completed'}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-[11px] font-medium text-slate-400">Last Lab Score</div>
              <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">
                {lastCompletedLab && lastCompletedLab.score !== null ? `${lastCompletedLab.score} / 100` : '—'}
              </div>
              <div className="text-[11px] text-slate-500">
                {lastCompletedLab && lastCompletedLab.confidence ? `Confidence: ${Math.round(lastCompletedLab.confidence * 100)}%` : 'Evidence pending'}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-[11px] font-medium text-slate-400">Recommended Lab</div>
              <div className="text-xs font-semibold text-violet-300 truncate mt-1">
                {labs[1]?.title || 'Survey Sampling Design'}
              </div>
              <div className="text-[11px] text-slate-400">Target role competency</div>
            </div>
          </div>
        </div>

        {/* Top Skill Gap Priority Card */}
        {topGap && topGap.gap_score > 0 ? (
          <div className="mt-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-amber-950/20 border border-amber-500/30 p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <ShieldAlert className="w-4 h-4" />
                </span>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider text-amber-400">
                    Top Skill Gap Priority
                  </div>
                  <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                    {topGap.competency_name}
                    <span className="text-xs font-normal text-slate-400">
                      ({topGap.domain_name})
                    </span>
                  </h3>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <GapPriorityBadge priority={topGap.priority_level} size="md" />
                <Link
                  href="/employee/gaps"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition shadow-md shadow-cyan-900/40"
                >
                  Review Skill Gaps
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
              <div className="md:col-span-6 space-y-2">
                <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                  {topGap.explanation}
                </p>
                <div className="text-xs text-slate-400 flex items-center gap-2">
                  <span className="font-semibold text-slate-300">Priority Score:</span>
                  <span className="font-mono text-cyan-300 font-bold">
                    {topGap.priority_score.toFixed(1)} / 100
                  </span>
                  <span className="text-slate-600">•</span>
                  <span>Gap Deficit:</span>
                  <span className="font-mono text-amber-400 font-bold">
                    {topGap.gap_score} pts
                  </span>
                </div>
              </div>

              <div className="md:col-span-6">
                <CurrentVsRequiredBar
                  currentScore={topGap.current_score}
                  requiredScore={topGap.required_score}
                  currentLevelName={topGap.current_level_name}
                  requiredLevelName={topGap.required_level_name}
                  gapScore={topGap.gap_score}
                  compact={false}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6 rounded-2xl bg-slate-900/60 border border-slate-800 p-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-sm font-bold text-slate-100">
                  Role Requirements Satisfied
                </h3>
                <p className="text-xs text-slate-400">
                  All active role requirements are currently satisfied by your demonstrated competencies.
                </p>
              </div>
            </div>
            <Link
              href="/employee/gaps"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs transition"
            >
              <span>Review Skill Gaps</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}

        {/* Next Best Learning Action Card (Stage 7) */}
        {topRec && (
          <div className="mt-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 border border-indigo-500/30 p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                </span>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                    <span>Action: Learning Recommendation</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                    {topRec.learning_item.title}
                  </h3>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <ProviderBadge
                  provider={topRec.learning_item.provider}
                  sourceMode={topRec.learning_item.source_mode}
                  size="md"
                />
                <Link
                  href="/employee/learning"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition shadow-md shadow-indigo-900/40"
                >
                  View Learning Path
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
              <div className="md:col-span-8 space-y-2">
                <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                  {topRec.reason}
                </p>
                <div className="text-xs text-slate-400 flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-slate-300">Target Competency:</span>
                  <span className="text-amber-300 font-medium">{topRec.target_competency_name}</span>
                  <span className="text-slate-600">•</span>
                  <span>Duration:</span>
                  <span className="text-slate-200 font-medium">
                    {Math.round(topRec.learning_item.duration_minutes / 60)} hrs
                  </span>
                  <span className="text-slate-600">•</span>
                  <span>Recommendation Score:</span>
                  <span className="font-mono text-amber-400 font-bold">
                    {topRec.score.toFixed(1)} / 100
                  </span>
                </div>
              </div>

              <div className="md:col-span-4 flex justify-start md:justify-end">
                {topRec.learning_item.url && (
                  <a
                    href={topRec.learning_item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 font-medium text-xs border border-slate-700 shadow-sm transition"
                  >
                    <span>Start Module</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </PageContainer>
    </AppShell>
  );
}

