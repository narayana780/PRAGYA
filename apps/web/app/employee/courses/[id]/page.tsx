'use client';

import React, { use } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle2,
  ExternalLink,
  Sparkles,
  Target,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';
import { ProviderBadge } from '@/components/learning/provider-badge';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { useLearningItem, useRecommendations, useStartRecommendation } from '@/hooks/use-recommendations';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { getCourseLaunchUrl, isExternalLaunchUrl } from '@/lib/course-utils';

interface CourseDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function CourseDetailPage({ params }: CourseDetailPageProps) {
  const { id } = use(params);
  const { data: employee } = useCurrentEmployee();
  const { data: item, isLoading, error } = useLearningItem(id);
  const { data: recommendations } = useRecommendations(employee?.id);
  const { mutate: startRec } = useStartRecommendation(employee?.id);

  // Check if this item is currently recommended for this employee
  const matchingRec = (recommendations || []).find((r) => r.learning_item_id === id);

  if (isLoading) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Course Detail">
        <PageContainer>
          <div className="p-16 text-center text-sm text-slate-400">Loading module syllabus...</div>
        </PageContainer>
      </AppShell>
    );
  }

  if (error || !item) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Course Not Found">
        <PageContainer>
          <div className="p-12 text-center space-y-4">
            <h2 className="text-xl font-bold text-slate-100">Learning Item Not Found</h2>
            <p className="text-xs text-slate-400">The requested learning module could not be retrieved.</p>
            <Link
              href="/employee/courses"
              className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Catalogue</span>
            </Link>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const durationHours = Math.round(item.duration_minutes / 60);

  return (
    <AppShell role="EMPLOYEE" pageTitle={item.title}>
      <PageContainer>
        {/* Navigation Breadcrumb */}
        <div className="mb-4">
          <Link
            href="/employee/courses"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Courses Catalogue</span>
          </Link>
        </div>

        {/* Hero Banner */}
        <div className="mb-8 p-6 md:p-8 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <ProviderBadge provider={item.provider} sourceMode={item.source_mode} size="md" />
              <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Level {item.level} of 5
              </span>
              <span className="text-xs font-mono text-slate-500">
                {item.provider_item_id}
              </span>
            </div>

            {matchingRec && (
              <div className="flex items-center gap-2">
                <GapPriorityBadge priority={matchingRec.priority_level} size="sm" />
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/30 text-xs font-bold font-mono">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Recommendation Score: {matchingRec.score.toFixed(1)}</span>
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3 max-w-3xl">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {item.title}
            </h1>
            <p className="text-sm md:text-base text-slate-300 leading-relaxed">
              {item.description}
            </p>
          </div>

          {/* Key Attributes Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-800 text-xs">
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-500 block mb-0.5">Duration</span>
              <span className="font-bold text-slate-200">
                {durationHours > 0 ? `${durationHours} hours` : `${item.duration_minutes} mins`}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-500 block mb-0.5">Difficulty</span>
              <span className="font-bold text-slate-200 capitalize">
                {item.difficulty.toLowerCase()}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-500 block mb-0.5">Format</span>
              <span className="font-bold text-slate-200 capitalize">
                {item.format.toLowerCase().replace('_', ' ')}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-500 block mb-0.5">Language</span>
              <span className="font-bold text-slate-200">{item.language}</span>
            </div>
          </div>

          {/* Action Row */}
          {(() => {
            const launchUrl = getCourseLaunchUrl(item);
            const isExternal = isExternalLaunchUrl(launchUrl);
            return (
              <div className="pt-2 flex flex-wrap items-center gap-3">
                {isExternal ? (
                  <a
                    href={launchUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-lg shadow-indigo-950/50 flex items-center gap-2 transition-all"
                    onClick={() => matchingRec && startRec(matchingRec.id)}
                  >
                    <span>Launch Official Module</span>
                    <ExternalLink className="w-4 h-4" />
                  </a>
                ) : (
                  <Link
                    href={launchUrl}
                    className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-lg shadow-indigo-950/50 flex items-center gap-2 transition-all"
                    onClick={() => matchingRec && startRec(matchingRec.id)}
                  >
                    <span>Launch Official Module</span>
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                )}
                <span className="text-xs text-slate-500">
                  Provider integration status: <span className="text-amber-400 font-medium">{item.source_mode} Prototype</span>
                </span>
              </div>
            );
          })()}
        </div>

        {/* SECTION: WHY PRAGYA RECOMMENDED THIS (IF RECOMMENDED) */}
        {matchingRec && (
          <div className="mb-8 p-6 rounded-xl bg-gradient-to-br from-indigo-950/30 via-slate-900 to-slate-900 border border-indigo-500/30 space-y-4">
            <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              Why PRAGYA Recommended This To You
            </div>
            <p className="text-sm font-medium text-slate-200 leading-relaxed bg-slate-950/60 p-4 rounded-lg border-l-4 border-amber-500">
              {matchingRec.structured_reason.summary}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="font-bold text-rose-400 block mb-1">Target Skill Gap:</span>
                <span className="text-slate-300">{matchingRec.structured_reason.gap_reason}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="font-bold text-indigo-400 block mb-1">Role Cadre Fit:</span>
                <span className="text-slate-300">{matchingRec.structured_reason.role_reason}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="font-bold text-sky-400 block mb-1">Pedagogical Progression:</span>
                <span className="text-slate-300">{matchingRec.structured_reason.level_reason}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <span className="font-bold text-teal-400 block mb-1">Novelty Verification:</span>
                <span className="text-slate-300">{matchingRec.structured_reason.novelty_reason}</span>
              </div>
            </div>
          </div>
        )}

        {/* SECTION: COMPETENCIES & LEARNING OUTCOMES */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Target className="w-4 h-4 text-indigo-400" />
              Syllabus Competency Coverage & Learning Outcomes
            </h3>

            {item.competencies && item.competencies.length > 0 ? (
              <div className="space-y-3">
                {item.competencies.map((comp, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-100 text-sm">
                          {comp.competency_name || comp.competency_code}
                        </span>
                        {comp.domain_name && (
                          <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                            {comp.domain_name}
                          </span>
                        )}
                      </div>
                      <span className="font-semibold text-indigo-300 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/30">
                        Coverage: {comp.coverage_level}
                      </span>
                    </div>
                    {comp.learning_outcome && (
                      <p className="text-slate-300 leading-relaxed pl-2 border-l-2 border-slate-700">
                        {comp.learning_outcome}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No competency mappings specified for this module.</p>
            )}
          </div>

          {/* Prerequisites & Verification Panel */}
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Prerequisites & Readiness
            </h3>

            {item.prerequisites && item.prerequisites.length > 0 ? (
              <div className="space-y-2.5 text-xs">
                {item.prerequisites.map((prereq: Record<string, unknown>, i: number) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 space-y-1"
                  >
                    <div className="font-semibold text-slate-200">
                      Required: {(prereq.competency_code as string) || 'Foundational Competency'}
                    </div>
                    <div className="text-slate-400 text-[11px]">
                      Minimum proficiency score: {(prereq.min_score as number) || 30.0}/100
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-slate-950/40 border border-slate-800 text-xs text-slate-300 space-y-1">
                <span className="text-emerald-400 font-semibold block">Open Enrollment</span>
                <p className="text-slate-400 leading-relaxed">
                  No prior competency prerequisites enforced. Ideal for direct onboarding or foundational refresh.
                </p>
              </div>
            )}
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}
