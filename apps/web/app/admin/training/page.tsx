'use client';

import React, { useState, useMemo } from 'react';
import {
  CheckCircle2,
  Info,
  RefreshCw,
  AlertTriangle,
  TrendingUp,
  Award,
  Target,
  Sparkles,
  Search,
  Filter,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { useWorkforceTrainingAnalytics } from '@/hooks/use-admin-workforce';
import {
  useOverallTrainingEffectiveness,
  useCourseEffectiveness,
  useRecommendationEffectiveness,
} from '@/hooks/use-training-effectiveness';

export default function AdminTrainingPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Stage 14 baseline hook
  const {
    data: trainingData,
    isLoading: isBaselineLoading,
    error: baselineError,
    refetch: refetchBaseline,
  } = useWorkforceTrainingAnalytics();

  // Stage 15 effectiveness hooks
  const {
    data: overallData,
    isLoading: isOverallLoading,
    error: overallError,
    refetch: refetchOverall,
  } = useOverallTrainingEffectiveness();

  const {
    data: coursesData,
    isLoading: isCoursesLoading,
    error: coursesError,
    refetch: refetchCourses,
  } = useCourseEffectiveness();

  const {
    data: recommendationData,
    isLoading: isRecLoading,
    error: recError,
    refetch: refetchRec,
  } = useRecommendationEffectiveness();

  const isLoading = isBaselineLoading || isOverallLoading || isCoursesLoading || isRecLoading;
  const hasError = baselineError || overallError || coursesError || recError;

  const handleRefreshAll = () => {
    refetchBaseline();
    refetchOverall();
    refetchCourses();
    refetchRec();
  };

  // Filtered courses
  const filteredCourses = useMemo(() => {
    if (!coursesData?.courses) return [];
    return coursesData.courses.filter((course) => {
      const matchesSearch =
        course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.course_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.provider.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus =
        statusFilter === 'ALL' || course.effectiveness_status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [coursesData, searchTerm, statusFilter]);

  // Chart data: Pre vs Post for top measurable courses
  const chartData = useMemo(() => {
    if (!coursesData?.courses) return [];
    return coursesData.courses
      .filter((c) => c.measurable_learners > 0 && c.average_pre_score !== null && c.average_post_score !== null)
      .slice(0, 6)
      .map((c) => ({
        name: c.title.length > 20 ? c.title.substring(0, 18) + '...' : c.title,
        PreScore: c.average_pre_score,
        PostScore: c.average_post_score,
        Improvement: c.average_improvement,
      }));
  }, [coursesData]);

  return (
    <AppShell role="ADMIN" pageTitle="Training Effectiveness & Outcomes">
      <PageContainer>
        {/* HEADER */}
        <PageHeader
          title="Training Effectiveness & Recommendation Analytics"
          subtitle="Empirical pre- vs. post-training competency score differentials, course outcome benchmarks, and recommendation lifecycle conversion."
          badge={
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Stage 15 Intelligence</span>
            </div>
          }
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Training Effectiveness' },
          ]}
        />

        {/* ERROR BANNER */}
        {hasError && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-rose-300 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Failed to load some training effectiveness metrics.</span>
            </div>
            <button
              onClick={handleRefreshAll}
              className="px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-200 text-xs font-semibold flex items-center gap-1.5 hover:bg-rose-500/30 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry All</span>
            </button>
          </div>
        )}

        {/* SECTION 1: EFFECTIVENESS KPI CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <GlassCard variant="elevated" className="p-5 border-emerald-500/20 bg-emerald-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>TRAINING COMPLETION</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-white font-mono">
              {isLoading ? '...' : `${overallData?.completion_rate?.toFixed(1) ?? '0.0'}%`}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {overallData?.completed_enrollments ?? 0} of {overallData?.total_enrollments ?? 0} enrolled courses completed
            </div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5 border-cyan-500/20 bg-cyan-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>MEASURABLE INTERVENTIONS</span>
              <Award className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-cyan-300 font-mono">
              {isLoading ? '...' : overallData?.measurable_interventions ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Learners with verified baseline & subsequent scores
            </div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5 border-violet-500/20 bg-violet-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>AVG OBSERVED IMPROVEMENT</span>
              <TrendingUp className="w-4 h-4 text-violet-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-violet-300 font-mono">
              {isLoading
                ? '...'
                : overallData?.average_observed_improvement !== null && overallData?.average_observed_improvement !== undefined
                ? `+${overallData.average_observed_improvement.toFixed(2)} pts`
                : 'NO_DATA'}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {overallData?.average_improvement_percentage !== null && overallData?.average_improvement_percentage !== undefined
                ? `+${overallData.average_improvement_percentage.toFixed(1)}% observed score change`
                : 'Across verified training completions'}
            </div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5 border-amber-500/20 bg-amber-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>EFFECTIVE INTERVENTIONS</span>
              <Target className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-amber-300 font-mono">
              {isLoading ? '...' : overallData?.effective_interventions ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {overallData?.competencies_improved_count ?? 0} distinct competencies improved
            </div>
          </GlassCard>
        </div>

        {/* METHODOLOGICAL TRANSPARENCY NOTICE */}
        <div className="mb-8 p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-start gap-3 text-xs text-slate-300">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-semibold text-white">Empirical Competency Measurement Policy</div>
            <p>
              Pre-training scores represent the latest authoritative diagnostic or evidence score prior to enrollment. Post-training scores reflect evidence recorded after course completion. In accordance with PRAGYA analytics standards, metrics indicate <span className="text-cyan-300 font-medium">observed improvement associated with training</span> rather than unproven causal attribution. Courses without pre-training evidence are categorized as <span className="text-amber-300 font-mono">INSUFFICIENT_DATA</span>.
            </p>
          </div>
        </div>

        {/* SECTION 2: CHARTS & VISUALIZATIONS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* CHART: PRE VS POST SCORES */}
          <GlassCard variant="elevated" className="p-6 lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">
                  Competency Score Comparison (Pre- vs Post-Training)
                </h3>
                <p className="text-xs text-slate-400">
                  Authoritative score shift for measurable training interventions
                </p>
              </div>
              <div className="text-xs font-mono text-cyan-400">
                Top Measurable Programmes
              </div>
            </div>

            {isLoading ? (
              <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
                Loading score comparison...
              </div>
            ) : chartData.length > 0 ? (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} angle={-15} textAnchor="end" />
                    <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        borderColor: '#334155',
                        borderRadius: '0.5rem',
                        fontSize: '12px',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Bar dataKey="PreScore" name="Pre-Training Score" fill="#64748b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="PostScore" name="Post-Training Score" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs">
                <AlertTriangle className="w-6 h-6 text-amber-400/60 mb-2" />
                <span>No courses with verified pre- and post-evidence pairs recorded yet.</span>
                <span className="text-[11px] text-slate-500 mt-1">Complete courses and take subsequent assessments to populate.</span>
              </div>
            )}
          </GlassCard>

          {/* RECOMMENDATION OUTCOME FUNNEL */}
          <GlassCard variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">
                  Recommendation Funnel
                </h3>
                <p className="text-xs text-slate-400">
                  Recommendation conversion lifecycle
                </p>
              </div>
              <Target className="w-4 h-4 text-violet-400" />
            </div>

            {isLoading ? (
              <div className="py-12 text-center text-slate-400 text-xs">Loading recommendation analytics...</div>
            ) : (
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Recommendations Issued</span>
                    <span className="font-mono font-bold text-white">
                      {recommendationData?.summary?.recommendations_issued ?? 0}
                    </span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2">
                    <div className="bg-cyan-500 h-2 rounded-full w-full" />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Started by Officers</span>
                    <span className="font-mono font-bold text-cyan-300">
                      {recommendationData?.summary?.recommendations_started ?? 0} (
                      {recommendationData?.summary?.start_rate?.toFixed(1) ?? '0.0'}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2">
                    <div
                      className="bg-cyan-400 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(recommendationData?.summary?.start_rate ?? 0, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Completed Training</span>
                    <span className="font-mono font-bold text-emerald-300">
                      {recommendationData?.summary?.recommendations_completed ?? 0} (
                      {recommendationData?.summary?.completion_rate?.toFixed(1) ?? '0.0'}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(recommendationData?.summary?.completion_rate ?? 0, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Observed Competency Growth</span>
                    <span className="font-mono font-bold text-violet-300">
                      {recommendationData?.summary?.recommendations_with_improvement ?? 0} (
                      {recommendationData?.summary?.improvement_rate?.toFixed(1) ?? '0.0'}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2">
                    <div
                      className="bg-violet-500 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min(recommendationData?.summary?.improvement_rate ?? 0, 100)}%` }}
                    />
                  </div>
                </div>

                {recommendationData?.summary?.average_observed_improvement !== null &&
                  recommendationData?.summary?.average_observed_improvement !== undefined && (
                    <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between text-xs">
                      <span className="text-slate-400">Avg Growth for Completed Recs:</span>
                      <span className="font-mono font-bold text-emerald-400">
                        +{recommendationData.summary.average_observed_improvement.toFixed(2)} pts
                      </span>
                    </div>
                  )}
              </div>
            )}
          </GlassCard>
        </div>

        {/* SECTION 3: COURSE EFFECTIVENESS TABLE */}
        <GlassCard variant="elevated" className="p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Course & Intervention Effectiveness Benchmarks
              </h3>
              <p className="text-xs text-slate-400">
                Pre- and post-training scores, observed differentials, and duration-normalized effectiveness index
              </p>
            </div>

            {/* SEARCH & FILTERS */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search course or provider..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-900/60 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-48 sm:w-60"
                />
              </div>

              <div className="flex items-center gap-1 bg-slate-900/60 border border-slate-700 rounded-lg p-1 text-xs">
                <Filter className="w-3.5 h-3.5 text-slate-400 ml-1.5" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="bg-transparent text-slate-200 text-xs py-0.5 px-2 focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-slate-900">All Statuses</option>
                  <option value="HIGH_EFFECTIVENESS" className="bg-slate-900">High (&gt;15 pts)</option>
                  <option value="MODERATE_EFFECTIVENESS" className="bg-slate-900">Moderate (5-15 pts)</option>
                  <option value="LOW_EFFECTIVENESS" className="bg-slate-900">Low (&lt;5 pts)</option>
                  <option value="INSUFFICIENT_DATA" className="bg-slate-900">Insufficient Data</option>
                </select>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-slate-400 text-xs">Loading course benchmarks...</div>
          ) : filteredCourses.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                    <th className="py-2.5 px-3">Course / Programme</th>
                    <th className="py-2.5 px-3">Provider</th>
                    <th className="py-2.5 px-3 text-center">Enrolled</th>
                    <th className="py-2.5 px-3 text-center">Completed</th>
                    <th className="py-2.5 px-3 text-center">Measurable</th>
                    <th className="py-2.5 px-3 text-center">Pre Score</th>
                    <th className="py-2.5 px-3 text-center">Post Score</th>
                    <th className="py-2.5 px-3 text-center">Observed Improvement</th>
                    <th className="py-2.5 px-3 text-center">Effectiveness Index</th>
                    <th className="py-2.5 px-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredCourses.map((course) => {
                    const hasImprovement =
                      course.average_improvement !== null && course.average_improvement !== undefined;
                    return (
                      <tr key={course.course_id} className="hover:bg-white/5 transition-colors">
                        <td className="py-3 px-3 max-w-xs">
                          <div className="font-semibold text-white truncate">{course.title}</div>
                          <div className="text-[10px] font-mono text-slate-400">
                            {course.course_code}
                            {course.duration_hours ? ` • ${course.duration_hours} hrs` : ''}
                          </div>
                          {course.competencies_affected.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {course.competencies_affected.slice(0, 2).map((c, i) => (
                                <span
                                  key={i}
                                  className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 font-mono"
                                >
                                  {c}
                                </span>
                              ))}
                              {course.competencies_affected.length > 2 && (
                                <span className="text-[9px] text-slate-400">
                                  +{course.competencies_affected.length - 2} more
                                </span>
                              )}
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 font-mono text-[10px]">
                            {course.provider}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-center font-mono text-slate-200">
                          {course.enrolled_count}
                        </td>
                        <td className="py-3 px-3 text-center font-mono">
                          <span className="text-emerald-400 font-medium">{course.completed_count}</span>
                          <span className="text-[10px] text-slate-400 ml-1">
                            ({course.completion_rate.toFixed(0)}%)
                          </span>
                        </td>
                        <td className="py-3 px-3 text-center font-mono font-medium text-cyan-300">
                          {course.measurable_learners}
                        </td>
                        <td className="py-3 px-3 text-center font-mono text-slate-300">
                          {course.average_pre_score !== null && course.average_pre_score !== undefined
                            ? course.average_pre_score.toFixed(1)
                            : '—'}
                        </td>
                        <td className="py-3 px-3 text-center font-mono text-slate-300">
                          {course.average_post_score !== null && course.average_post_score !== undefined
                            ? course.average_post_score.toFixed(1)
                            : '—'}
                        </td>
                        <td className="py-3 px-3 text-center font-mono">
                          {hasImprovement ? (
                            <div
                              className={`font-bold ${
                                course.average_improvement! > 0
                                  ? 'text-emerald-400'
                                  : course.average_improvement! === 0
                                  ? 'text-slate-400'
                                  : 'text-rose-400'
                              }`}
                            >
                              {course.average_improvement! > 0 ? '+' : ''}
                              {course.average_improvement!.toFixed(2)} pts
                              {course.improvement_percentage !== null && (
                                <span className="text-[10px] block opacity-80">
                                  ({course.improvement_percentage > 0 ? '+' : ''}
                                  {course.improvement_percentage.toFixed(1)}%)
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-slate-500 font-mono text-[10px]">NO_DATA</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center font-mono">
                          {course.effectiveness_index !== null && course.effectiveness_index !== undefined ? (
                            <span className="font-semibold text-cyan-300">
                              {course.effectiveness_index.toFixed(2)} pts/hr
                            </span>
                          ) : (
                            <span className="text-slate-500 text-[10px]">NOT_AVAILABLE</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                              course.effectiveness_status === 'HIGH_EFFECTIVENESS'
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                : course.effectiveness_status === 'MODERATE_EFFECTIVENESS'
                                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                : course.effectiveness_status === 'LOW_EFFECTIVENESS'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-slate-700/40 text-slate-400 border border-slate-700'
                            }`}
                          >
                            {course.effectiveness_status.replace('_', ' ')}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-400 text-xs">
              No course benchmarks matching filter criteria.
            </div>
          )}
        </GlassCard>

        {/* SECTION 4: COMPETENCY IMPROVEMENT BREAKDOWN */}
        <GlassCard variant="elevated" className="p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Competencies with Observed Post-Training Improvement
              </h3>
              <p className="text-xs text-slate-400">
                Official statistical competencies showing measurable score changes following learning interventions
              </p>
            </div>
            <div className="text-xs font-mono text-emerald-400">
              {overallData?.competencies_improved_count ?? 0} Competencies Showing Growth
            </div>
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-slate-400 text-xs">Loading competency metrics...</div>
          ) : overallData?.competency_improvements && overallData.competency_improvements.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {overallData.competency_improvements.slice(0, 9).map((comp) => {
                const hasDelta = comp.average_improvement !== null && comp.average_improvement !== undefined;
                return (
                  <div
                    key={comp.competency_id}
                    className="p-4 rounded-xl bg-slate-900/60 border border-white/5 hover:border-white/10 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <div className="font-semibold text-white text-xs">{comp.competency_name}</div>
                        <div className="text-[10px] font-mono text-slate-400">
                          {comp.competency_code} • {comp.domain_name}
                        </div>
                      </div>
                      {hasDelta && (
                        <span
                          className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                            comp.average_improvement! > 0
                              ? 'bg-emerald-500/20 text-emerald-300'
                              : 'bg-slate-700/40 text-slate-400'
                          }`}
                        >
                          {comp.average_improvement! > 0 ? '+' : ''}
                          {comp.average_improvement!.toFixed(2)} pts
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-white/5 text-[11px] font-mono">
                      <div>
                        <div className="text-[10px] text-slate-400">PRE</div>
                        <div className="font-bold text-slate-300">
                          {comp.average_pre_score !== null ? comp.average_pre_score.toFixed(1) : '—'}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-400">POST</div>
                        <div className="font-bold text-emerald-400">
                          {comp.average_post_score !== null ? comp.average_post_score.toFixed(1) : '—'}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-400">LEARNERS</div>
                        <div className="font-bold text-cyan-300">{comp.measurable_learners}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-400 text-xs">
              No competency improvements recorded yet.
            </div>
          )}
        </GlassCard>

        {/* SECTION 5: STAGE 14 OPERATIONAL ACTIVE PROGRAMMES TABLE (PRESERVED) */}
        <GlassCard variant="elevated" className="p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Workforce Learning Operations & Catalogue Overview
              </h3>
              <p className="text-xs text-slate-400">
                Participation rates, module completion benchmarks, and activity attempts (Stage 14 Baseline)
              </p>
            </div>
            <div className="text-xs font-mono text-cyan-400">
              {trainingData?.total_learners ?? 0} Active Officers Enrolled
            </div>
          </div>

          {isBaselineLoading ? (
            <div className="py-12 text-center text-slate-400 text-xs">Loading operational overview...</div>
          ) : trainingData?.top_courses && trainingData.top_courses.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                    <th className="py-2.5 px-3">Programme Title</th>
                    <th className="py-2.5 px-3">Provider</th>
                    <th className="py-2.5 px-3 text-center">Enrolled</th>
                    <th className="py-2.5 px-3 text-center">Completed</th>
                    <th className="py-2.5 px-3 text-center">Completion Rate</th>
                    <th className="py-2.5 px-3 text-center">Avg Progress</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {trainingData.top_courses.map((course) => (
                    <tr key={course.course_id} className="hover:bg-white/5 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-semibold text-white">{course.title}</div>
                        <div className="text-[10px] font-mono text-slate-400">{course.course_code}</div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 font-mono text-[10px]">
                          {course.provider}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-medium text-slate-200">
                        {course.enrolled_count}
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-medium text-emerald-400">
                        {course.completed_count}
                      </td>
                      <td className="py-3 px-3 text-center font-mono">
                        <span className="font-bold text-white">{course.completion_rate.toFixed(1)}%</span>
                      </td>
                      <td className="py-3 px-3 text-center font-mono text-cyan-300 font-bold">
                        {course.average_progress.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-400 text-xs">
              No active learning course progress recorded yet.
            </div>
          )}
        </GlassCard>
      </PageContainer>
    </AppShell>
  );
}
