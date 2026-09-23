'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Search,
  Clock,
  BookOpen,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { ProviderBadge } from '@/components/learning/provider-badge';
import { useLearningItems, useRecommendations } from '@/hooks/use-recommendations';
import { useCompetencies } from '@/hooks/use-competency';
import { useCurrentEmployee } from '@/hooks/use-employee';

export default function CourseDiscoveryPage() {
  const { data: employee } = useCurrentEmployee();
  const { data: recommendations } = useRecommendations(employee?.id);
  const { data: competenciesData } = useCompetencies({ pageSize: 100 });

  // Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [providerFilter, setProviderFilter] = useState('');
  const [competencyFilter, setCompetencyFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [formatFilter, setFormatFilter] = useState('');

  const { data: catalogue, isLoading } = useLearningItems({
    search: searchTerm || undefined,
    provider: providerFilter || undefined,
    competency_id: competencyFilter || undefined,
    difficulty: difficultyFilter || undefined,
    format: formatFilter || undefined,
    limit: 100,
  });

  // Map of recommended learning_item_id -> score
  const recScoreMap = new Map<string, number>();
  (recommendations || []).forEach((r) => {
    recScoreMap.set(r.learning_item_id, r.score);
  });

  const competencies = competenciesData?.items || [];
  const items = catalogue?.items || [];

  return (
    <AppShell role="EMPLOYEE" pageTitle="Learning Catalogue">
      <PageContainer>
        <PageHeader
          title="Statistical Learning Catalogue"
          subtitle="Discover curated courses, simulation labs, and executive programmes across iGOT Karmayogi, NSSTA/TPAC, and PRAGYA."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'Personalized Learning', href: '/employee/learning' },
            { label: 'Courses Catalogue' },
          ]}
          actions={
            <Link
              href="/employee/learning"
              className="px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Personalized Recommendations</span>
            </Link>
          }
        />

        {/* Filter Controls Bar */}
        <div className="mb-8 p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          {/* Search Row */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by course title, syllabus, or topic..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          {/* Filters Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Provider Filter */}
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Learning Provider</label>
              <select
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Providers</option>
                <option value="IGOT">iGOT Karmayogi [MOCK]</option>
                <option value="NSSTA_TPAC">NSSTA / TPAC [MOCK]</option>
                <option value="PRAGYA">PRAGYA Labs [INTERNAL]</option>
              </select>
            </div>

            {/* Competency Filter */}
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Target Competency</label>
              <select
                value={competencyFilter}
                onChange={(e) => setCompetencyFilter(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Competencies</option>
                {competencies.map((comp) => (
                  <option key={comp.id} value={comp.id}>
                    {comp.name} ({comp.code})
                  </option>
                ))}
              </select>
            </div>

            {/* Difficulty Filter */}
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Difficulty</label>
              <select
                value={difficultyFilter}
                onChange={(e) => setDifficultyFilter(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Difficulties</option>
                <option value="BEGINNER">Beginner</option>
                <option value="INTERMEDIATE">Intermediate</option>
                <option value="ADVANCED">Advanced</option>
              </select>
            </div>

            {/* Format Filter */}
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Delivery Format</label>
              <select
                value={formatFilter}
                onChange={(e) => setFormatFilter(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Formats</option>
                <option value="SELF_PACED">Self-Paced Digital</option>
                <option value="INSTRUCTOR_LED">Instructor-Led</option>
                <option value="BLENDED">Blended</option>
                <option value="INTERACTIVE_LAB">Interactive Lab</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results Counter */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs text-slate-400">
            Showing <span className="text-slate-100 font-semibold">{items.length}</span> learning items
            {catalogue?.total !== undefined && ` of ${catalogue.total} total`}
          </span>
          {(searchTerm || providerFilter || competencyFilter || difficultyFilter || formatFilter) && (
            <button
              onClick={() => {
                setSearchTerm('');
                setProviderFilter('');
                setCompetencyFilter('');
                setDifficultyFilter('');
                setFormatFilter('');
              }}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Courses Grid */}
        {isLoading ? (
          <div className="p-16 text-center text-sm text-slate-400">Loading learning catalogue...</div>
        ) : items.length === 0 ? (
          <div className="p-16 rounded-xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
            <BookOpen className="w-10 h-10 text-slate-600 mx-auto" />
            <h4 className="text-base font-semibold text-slate-200">No learning items match these filters.</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Try adjusting your search query or loosening provider and competency filters.
            </p>
            {(searchTerm || providerFilter || competencyFilter || difficultyFilter || formatFilter) && (
              <div className="pt-2">
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setProviderFilter('');
                    setCompetencyFilter('');
                    setDifficultyFilter('');
                    setFormatFilter('');
                  }}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
                >
                  Reset Filters
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item) => {
              const recScore = recScoreMap.get(item.id);
              const durationHours = Math.round(item.duration_minutes / 60);

              return (
                <div
                  key={item.id}
                  className="p-5 rounded-xl bg-slate-900/70 hover:bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4 group"
                >
                  <div className="space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <ProviderBadge provider={item.provider} sourceMode={item.source_mode} size="sm" />
                      {recScore !== undefined ? (
                        <div
                          className="flex items-center gap-1 px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px] font-bold font-mono"
                          title="Personalized Recommendation Score"
                        >
                          <Sparkles className="w-3 h-3 text-amber-400" />
                          <span>{recScore.toFixed(1)}</span>
                        </div>
                      ) : (
                        <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                          Level {item.level}
                        </span>
                      )}
                    </div>

                    <div>
                      <h3 className="text-base font-bold text-slate-100 group-hover:text-indigo-300 transition-colors line-clamp-2">
                        {item.title}
                      </h3>
                      <p className="text-xs text-slate-300 mt-1.5 line-clamp-3 leading-relaxed">
                        {item.description}
                      </p>
                    </div>

                    {/* Competency tags */}
                    {item.competencies && item.competencies.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {item.competencies.slice(0, 2).map((comp, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 text-[10px] font-medium border border-slate-700/80"
                          >
                            {comp.competency_name || comp.competency_code}
                          </span>
                        ))}
                        {item.competencies.length > 2 && (
                          <span className="text-[10px] text-slate-500 self-center">
                            +{item.competencies.length - 2} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Footer Meta & View CTA */}
                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center gap-2.5">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        {durationHours > 0 ? `${durationHours}h` : `${item.duration_minutes}m`}
                      </span>
                      <span className="capitalize text-slate-400">
                        {item.format.toLowerCase().replace('_', ' ')}
                      </span>
                    </div>

                    <Link
                      href={`/employee/courses/${item.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 hover:border-slate-600 transition-all flex items-center gap-1 group/btn"
                    >
                      <span>View</span>
                      <ArrowRight className="w-3 h-3 group-hover/btn:translate-x-0.5 transition-transform" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </PageContainer>
    </AppShell>
  );
}
