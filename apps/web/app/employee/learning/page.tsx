'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  BookOpen,
  Compass,
  ArrowRight,
  Calculator,
  Layers,
  History,
  CheckCircle2,
  ExternalLink,
  Target,
  Zap,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { ProviderBadge } from '@/components/learning/provider-badge';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { RecommendationCard } from '@/components/learning/recommendation-card';
import { LearningPathTimeline } from '@/components/learning/learning-path-timeline';
import { RecommendationExplanationDrawer } from '@/components/learning/recommendation-explanation-drawer';
import { getCourseLaunchUrl, isExternalLaunchUrl } from '@/lib/course-utils';
import { useCurrentEmployee, useEmployeeTrainingHistory } from '@/hooks/use-employee';
import {
  useRecommendations,
  useLearningPath,
  useGenerateRecommendations,
  useGenerateLearningPath,
  useStartRecommendation,
} from '@/hooks/use-recommendations';
import type { LearningRecommendation } from '@pragya/types';

export default function PersonalizedLearningPage() {
  const { data: employee } = useCurrentEmployee();
  const { data: trainingHistory } = useEmployeeTrainingHistory(employee?.id);
  const { data: recommendations, isLoading: recsLoading } = useRecommendations(employee?.id);
  const { data: learningPath } = useLearningPath(employee?.id);

  const { mutate: refreshRecs, isPending: isRefreshingRecs } = useGenerateRecommendations(employee?.id);
  const { mutate: refreshPath, isPending: isRefreshingPath } = useGenerateLearningPath(employee?.id);
  const { mutate: startRec } = useStartRecommendation(employee?.id);

  const [providerFilter, setProviderFilter] = useState<'ALL' | 'IGOT' | 'NSSTA_TPAC' | 'PRAGYA'>('ALL');
  const [activeExplanationRec, setActiveExplanationRec] = useState<LearningRecommendation | null>(null);

  const topRec = recommendations && recommendations.length > 0 ? recommendations[0] : null;

  const filteredRecs = (recommendations || []).filter((r) => {
    if (providerFilter === 'ALL') return true;
    return r.learning_item.provider === providerFilter;
  });

  const handleRefreshAll = () => {
    refreshRecs();
    refreshPath();
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Personalized Learning">
      <PageContainer>
        <PageHeader
          title="Your Personalized Learning"
          subtitle="Direct pedagogical recommendations addressing your prioritized skill gaps across official and internal learning providers."
          badge={
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Multi-Provider Intelligence
            </span>
          }
          actions={
            <div className="flex items-center gap-2">
              <Link
                href="/employee/courses"
                className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 flex items-center gap-1.5 transition-colors"
              >
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>Explore Catalogue</span>
              </Link>
              <button
                onClick={handleRefreshAll}
                disabled={isRefreshingRecs || isRefreshingPath}
                className="px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm transition-all flex items-center gap-1.5"
              >
                <Sparkles className="w-4 h-4 text-amber-300" />
                <span>{isRefreshingRecs ? 'Recalculating...' : 'Regenerate Recommendations'}</span>
              </button>
            </div>
          }
        />

        {/* Priority Insight Banner */}
        <div className="mb-8 p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Calibrated to Your Statistical Cadre Gaps
              </h3>
              <p className="text-xs text-slate-400">
                Prioritizing critical role requirements for{' '}
                <span className="text-slate-200 font-medium">
                  {employee?.designation || 'Statistical Officer'}
                </span>
                {employee?.target_role_name && (
                  <>
                    {' '}
                    with cadre advancement towards{' '}
                    <span className="text-indigo-400 font-medium">{employee.target_role_name}</span>
                  </>
                )}
                .
              </p>
            </div>
          </div>
          <Link
            href="/employee/gaps"
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 shrink-0 transition-colors"
          >
            <span>Review Skill Gaps</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* SECTION 1: TOP RECOMMENDATION (NEXT BEST LEARNING ACTION) */}
        {topRec && (
          <div className="mb-10">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                <Zap className="w-4 h-4 fill-amber-400 text-amber-400" />
                Next Best Learning Action
              </h2>
              <span className="text-xs text-slate-500">Highest Deterministic Ranking</span>
            </div>

            <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-br from-indigo-950/50 via-slate-900 to-slate-950 border-2 border-indigo-500/40 shadow-xl shadow-indigo-950/40 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />

              <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div className="space-y-4 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <ProviderBadge
                      provider={topRec.learning_item.provider}
                      sourceMode={topRec.learning_item.source_mode}
                      size="md"
                    />
                    <GapPriorityBadge priority={topRec.priority_level} size="md" />
                    <span className="text-xs px-2.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">
                      Level {topRec.learning_item.level} of 5
                    </span>
                  </div>

                  <div>
                    <h3 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                      {topRec.learning_item.title}
                    </h3>
                    <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                      {topRec.learning_item.description}
                    </p>
                  </div>

                  {/* Why recommended highlight */}
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/90 text-xs space-y-1.5">
                    <div className="text-amber-400 font-semibold flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      PRAGYA Deterministic Match Rationale:
                    </div>
                    <p className="text-slate-200 font-medium leading-relaxed">
                      {topRec.reason}
                    </p>
                  </div>

                  {/* Metrics Row */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-slate-500 block">Target Competency</span>
                      <span className="font-bold text-slate-200">{topRec.target_competency_name}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-slate-500 block">Estimated Time</span>
                      <span className="font-bold text-slate-200">
                        {Math.round(topRec.learning_item.duration_minutes / 60)} hrs
                      </span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-slate-500 block">Course Format</span>
                      <span className="font-bold text-slate-200 capitalize">
                        {topRec.learning_item.format.toLowerCase().replace('_', ' ')}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-slate-500 block">Recommendation Score</span>
                      <span className="font-bold text-amber-300 font-mono text-sm">
                        {topRec.score.toFixed(1)} / 100
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right side CTA Column */}
                <div className="lg:border-l lg:border-slate-800 lg:pl-8 flex flex-col justify-center space-y-3 min-w-[220px]">
                  {(() => {
                    const launchUrl = getCourseLaunchUrl(topRec.learning_item);
                    const isExternal = isExternalLaunchUrl(launchUrl);
                    return isExternal ? (
                      <a
                        href={launchUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-950/60 flex items-center justify-center gap-2 transition-all"
                        onClick={() => startRec(topRec.id)}
                      >
                        <span>Start Learning</span>
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    ) : (
                      <Link
                        href={launchUrl}
                        className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-950/60 flex items-center justify-center gap-2 transition-all"
                        onClick={() => startRec(topRec.id)}
                      >
                        <span>Start Learning</span>
                        <ExternalLink className="w-4 h-4" />
                      </Link>
                    );
                  })()}
                  <button
                    onClick={() => setActiveExplanationRec(topRec)}
                    className="w-full py-2.5 px-4 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 text-xs font-medium border border-slate-700 flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Calculator className="w-3.5 h-3.5 text-indigo-400" />
                    <span>View Factor Breakdown</span>
                  </button>
                  <Link
                    href={`/employee/courses/${topRec.learning_item.id}`}
                    className="text-center text-xs text-slate-400 hover:text-slate-200 py-1 transition-colors"
                  >
                    Full Syllabus & Details
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 2: RECOMMENDED FOR YOU (RANKED CATALOGUE) */}
        <div className="mb-12 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-indigo-400" />
                Recommended For You
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Top learning content curated across iGOT Karmayogi, NSSTA/TPAC, and PRAGYA Labs.
              </p>
            </div>

            {/* Provider Filter Tabs */}
            <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs self-start sm:self-auto">
              <button
                onClick={() => setProviderFilter('ALL')}
                className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                  providerFilter === 'ALL'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All Providers
              </button>
              <button
                onClick={() => setProviderFilter('IGOT')}
                className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                  providerFilter === 'IGOT'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                iGOT [MOCK]
              </button>
              <button
                onClick={() => setProviderFilter('NSSTA_TPAC')}
                className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                  providerFilter === 'NSSTA_TPAC'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                NSSTA/TPAC [MOCK]
              </button>
              <button
                onClick={() => setProviderFilter('PRAGYA')}
                className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                  providerFilter === 'PRAGYA'
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                PRAGYA Labs
              </button>
            </div>
          </div>

          {recsLoading ? (
            <div className="p-12 text-center text-sm text-slate-400">Loading recommendations...</div>
          ) : filteredRecs.length === 0 ? (
            <div className="p-8 rounded-xl bg-slate-900/60 border border-slate-800 text-center text-xs text-slate-400">
              No recommendations found matching this provider filter.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredRecs.map((rec, idx) => (
                <RecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  isTopRank={idx === 0 && providerFilter === 'ALL'}
                  onStart={(recId) => startRec(recId)}
                />
              ))}
            </div>
          )}
        </div>

        {/* SECTION 3: PROGRESSIVE CADRE LEARNING PATH */}
        <div className="mb-12 space-y-4">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Your Cadre Learning Pathway
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Structured multi-step progression advancing from foundational digital modules to hands-on PRAGYA simulation labs and institutional certifications.
            </p>
          </div>

          <LearningPathTimeline
            learningPath={learningPath || null}
            onRefresh={() => refreshPath()}
            isRefreshing={isRefreshingPath}
          />
        </div>

        {/* SECTION 4: WHY THESE RECOMMENDATIONS? (EXPLANATION ARCHITECTURE) */}
        <div className="mb-12 p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
            <Calculator className="w-4 h-4" />
            Deterministic Recommendation Engine Architecture
          </div>
          <h3 className="text-lg font-bold text-slate-100">
            How PRAGYA Evaluates & Ranks Learning Recommendations
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
            PRAGYA operates on an explainable, deterministic multi-factor model. Rather than relying on generic black-box suggestions, every recommendation is computed directly from your verified Stage 5 competency scores, Stage 6 priority skill gaps, and official curriculum requirements:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
              <span className="font-bold text-rose-400 block mb-1">35% Gap Priority</span>
              <span className="text-slate-400">
                Directly rewards content addressing CRITICAL and HIGH priority role requirements.
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
              <span className="font-bold text-amber-400 block mb-1">25% Competency Match</span>
              <span className="text-slate-400">
                Verified against official SIH26101 statistical competency taxonomy and syllabus overlap.
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
              <span className="font-bold text-sky-400 block mb-1">15% Level Fit</span>
              <span className="text-slate-400">
                Selects the optimal pedagogical next step based on your current demonstrated proficiency.
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
              <span className="font-bold text-purple-400 block mb-1">25% Outcomes & Novelty</span>
              <span className="text-slate-400">
                Accounts for syllabus coverage depth (10%), prerequisite readiness (5%), duration fit (5%), and non-duplication (5%).
              </span>
            </div>
          </div>
        </div>

        {/* SECTION 5: RECENTLY COMPLETED TRAINING */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-400" />
              Recently Completed Training History
            </h2>
            <Link
              href="/employee/profile"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 transition-colors"
            >
              <span>View Full History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {trainingHistory && trainingHistory.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trainingHistory.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-medium text-[11px]">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Completed</span>
                      {item.completed_at && (
                        <span className="text-slate-500 font-mono">
                          • {new Date(item.completed_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <h4 className="text-sm font-semibold text-slate-100">{item.title}</h4>
                    <div className="text-slate-400 flex items-center gap-2 pt-1">
                      <span>Provider: {item.provider}</span>
                      {item.duration_hours && <span>• {item.duration_hours} hrs</span>}
                    </div>
                  </div>
                  {item.score && (
                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-slate-500 block">Score</span>
                      <span className="text-sm font-bold font-mono text-emerald-400">
                        {item.score.toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-400">
              No historical training records found.
            </div>
          )}
        </div>
      </PageContainer>

      {/* Interactive Explanation Drawer */}
      <RecommendationExplanationDrawer
        recommendation={activeExplanationRec}
        onClose={() => setActiveExplanationRec(null)}
        onStart={(id) => startRec(id)}
      />
    </AppShell>
  );
}
