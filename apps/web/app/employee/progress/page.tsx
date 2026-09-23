'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  TrendingUp,
  Award,
  Target,
  Zap,
  Layers,
  ArrowUpRight,
  ArrowRight,
  Minus,
  Sparkles,
  AlertTriangle,
  BookOpen,
  Brain,
  FlaskConical,
  GraduationCap,
  Activity,
  CheckCircle2,
  HelpCircle,
  Search,
  RefreshCw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip as RechartsTooltip,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee } from '@/hooks/use-employee';
import {
  useEmployeePerformance,
  useEmployeePerformanceTimeline,
} from '@/hooks/use-performance';

export default function EmployeeProgressPage() {
  const { data: employee, isLoading: empLoading } = useCurrentEmployee();
  const {
    data: performance,
    isLoading: perfLoading,
    error: perfError,
    refetch: refetchPerf,
  } = useEmployeePerformance(employee?.id);
  const {
    data: timelineData,
    isLoading: timelineLoading,
  } = useEmployeePerformanceTimeline(employee?.id);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedTrajectoryComp, setSelectedTrajectoryComp] = useState<string>('ALL');

  const isLoading = empLoading || perfLoading || timelineLoading;

  // Extract unique domains for filter
  const domains = (() => {
    if (!performance?.competencies) return [];
    const set = new Set<string>();
    performance.competencies.forEach((c) => {
      if (c.domain_name) set.add(c.domain_name);
    });
    return Array.from(set).sort();
  })();

  // Filter competencies
  const filteredCompetencies = (() => {
    if (!performance?.competencies) return [];
    return performance.competencies.filter((c) => {
      const matchesSearch =
        searchQuery === '' ||
        c.competency_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.competency_code.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesDomain =
        selectedDomain === 'ALL' || c.domain_name === selectedDomain;
      const matchesStatus =
        selectedStatus === 'ALL' || c.status === selectedStatus;
      return matchesSearch && matchesDomain && matchesStatus;
    });
  })();

  // Before vs After Radar Data
  const radarData = (() => {
    if (!performance?.competencies) return [];
    // Select competencies with demonstrated score or baseline
    const candidates = performance.competencies.filter(
      (c) => (c.baseline_score !== null && c.baseline_score !== undefined) || c.current_score > 0
    );
    // Limit to top 8 for clean radar polygon visualization
    return candidates.slice(0, 8).map((c) => ({
      competency: c.competency_code || c.competency_name.slice(0, 14),
      fullName: c.competency_name,
      Baseline: c.baseline_score ?? 0,
      Current: c.current_score,
      Target: c.target_score ?? 75,
    }));
  })();

  // Longitudinal Trajectory Data from Timeline events
  const trajectoryData = (() => {
    if (!timelineData?.events || timelineData.events.length === 0) return [];
    // Events are newest first; reverse for chronological left-to-right chart
    const chronological = [...timelineData.events].reverse();

    // Filter by competency if selected
    const relevant =
      selectedTrajectoryComp === 'ALL'
        ? chronological
        : chronological.filter(
            (e) =>
              e.competency_id === selectedTrajectoryComp ||
              e.competency_name === selectedTrajectoryComp
          );

    return relevant
      .filter((e) => e.percentage !== null && e.percentage !== undefined)
      .map((e, idx) => {
        const dateObj = new Date(e.timestamp);
        const formattedDate = !isNaN(dateObj.getTime())
          ? dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
          : `Point ${idx + 1}`;
        return {
          date: formattedDate,
          score: Math.round((e.percentage ?? 0) * 10) / 10,
          title: e.title,
          type: e.type,
        };
      });
  })();

  // Helper for Status Badge styling
  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'MASTERED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" /> Mastered
          </span>
        );
      case 'IMPROVING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-500/15 text-teal-300 border border-teal-500/30">
            <ArrowUpRight className="w-3 h-3" /> Improving
          </span>
        );
      case 'NEEDS_FOCUS':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertTriangle className="w-3 h-3" /> Needs Focus
          </span>
        );
      case 'STABLE':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-500/15 text-slate-300 border border-slate-600/30">
            <Minus className="w-3 h-3" /> Stable
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <HelpCircle className="w-3 h-3" /> No Baseline
          </span>
        );
    }
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Performance & Progress">
      <PageContainer>
        <PageHeader
          title="Performance & Competency Progress"
          subtitle="Track how your competencies have evolved through assessments, learning and practical evidence."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'Performance & Progress' },
          ]}
          actions={
            <button
              onClick={() => refetchPerf()}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
              title="Refresh performance analytics"
            >
              <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
              Sync Data
            </button>
          }
        />

        {isLoading ? (
          <div className="py-20 flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
            <p className="text-sm text-slate-400 font-mono">
              Loading authoritative performance analytics...
            </p>
          </div>
        ) : perfError ? (
          <div className="p-8 rounded-xl bg-rose-950/20 border border-rose-800/40 text-center max-w-lg mx-auto my-12">
            <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-rose-200 mb-1">
              Unable to Load Performance Analytics
            </h3>
            <p className="text-sm text-rose-300/80 mb-4">
              An error occurred while deriving competency progression from backend evidence.
            </p>
            <button
              onClick={() => refetchPerf()}
              className="px-4 py-2 text-xs font-medium rounded-lg bg-rose-600 hover:bg-rose-500 text-white transition"
            >
              Retry
            </button>
          </div>
        ) : !performance ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 my-10 max-w-lg mx-auto">
            <HelpCircle className="w-12 h-12 text-slate-500 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-200">
              No Performance History Yet
            </h3>
            <p className="text-sm text-slate-400 mt-1 mb-6">
              Complete your initial diagnostic assessment to establish your baseline competency score.
            </p>
            <Link
              href="/employee/assessments"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20 hover:brightness-110 transition"
            >
              Take Diagnostic Assessment
            </Link>
          </div>
        ) : (
          <div className="space-y-8 pb-12">
            {/* Top Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Card 1: Baseline Competency */}
              <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-900/40 border border-slate-800/80 shadow-lg relative overflow-hidden">
                <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
                  <span>Diagnostic Baseline</span>
                  <div className="p-1.5 rounded-lg bg-slate-800 text-cyan-400">
                    <Activity className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {performance.overall.baseline_score !== null &&
                  performance.overall.baseline_score !== undefined ? (
                    <span>{performance.overall.baseline_score.toFixed(1)}</span>
                  ) : (
                    <span className="text-slate-500 text-base font-normal">
                      No Baseline
                    </span>
                  )}
                  <span className="text-xs text-slate-400 font-normal ml-1">/ 100</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
                  <span>{performance.overall.competencies_with_baseline}</span> competencies measured initially
                </div>
              </div>

              {/* Card 2: Current Competency */}
              <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-900/40 border border-slate-800/80 shadow-lg relative overflow-hidden">
                <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
                  <span>Current Competency</span>
                  <div className="p-1.5 rounded-lg bg-slate-800 text-teal-400">
                    <Award className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {performance.overall.current_score.toFixed(1)}
                  <span className="text-xs text-slate-400 font-normal ml-1">/ 100</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
                  <span>{performance.overall.competencies_evaluated}</span> active competencies demonstrated
                </div>
              </div>

              {/* Card 3: Overall Improvement */}
              <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-900/40 border border-slate-800/80 shadow-lg relative overflow-hidden">
                <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
                  <span>Overall Capability Growth</span>
                  <div
                    className={`p-1.5 rounded-lg ${
                      performance.overall.improvement_points >= 0
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'bg-rose-500/10 text-rose-400'
                    }`}
                  >
                    <TrendingUp className="w-4 h-4" />
                  </div>
                </div>
                <div className="flex items-baseline gap-2">
                  <span
                    className={`text-2xl font-bold ${
                      performance.overall.improvement_points >= 0
                        ? 'text-emerald-400'
                        : 'text-rose-400'
                    }`}
                  >
                    {performance.overall.improvement_points >= 0 ? '+' : ''}
                    {performance.overall.improvement_points.toFixed(1)}
                  </span>
                  <span className="text-xs text-slate-400 font-medium">pts</span>
                  <span
                    className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
                      performance.overall.improvement_percentage >= 0
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-rose-500/20 text-rose-300'
                    }`}
                  >
                    {performance.overall.improvement_percentage >= 0 ? '+' : ''}
                    {performance.overall.improvement_percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
                  <span>{performance.summary.competencies_improved}</span> competencies improved
                </div>
              </div>

              {/* Card 4: Role Readiness / Target */}
              <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-900/40 border border-slate-800/80 shadow-lg relative overflow-hidden">
                <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-3">
                  <span>Role Target Readiness</span>
                  <div className="p-1.5 rounded-lg bg-slate-800 text-violet-400">
                    <Target className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-slate-100">
                  {performance.overall.target_readiness_percentage !== null &&
                  performance.overall.target_readiness_percentage !== undefined ? (
                    `${performance.overall.target_readiness_percentage.toFixed(1)}%`
                  ) : (
                    <span className="text-slate-500 text-base font-normal">
                      No Target Set
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-400 mt-2 truncate">
                  Role: <span className="text-slate-300">{performance.job_role_name || 'Assigned Role'}</span>
                </div>
              </div>
            </div>

            {/* Visual Analytics: Before vs After & Longitudinal Trajectory */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Radar: Diagnostic Baseline vs Current */}
              <div className="p-6 rounded-2xl bg-[#0B1120] border border-slate-800 shadow-xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      Baseline vs. Current Recalibrated State
                    </h3>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">
                    Comparison across evaluated competencies showing growth from initial diagnostic.
                  </p>
                </div>

                <div className="w-full h-72 flex items-center justify-center">
                  {radarData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis
                          dataKey="competency"
                          tick={{ fill: '#94a3b8', fontSize: 11 }}
                        />
                        <PolarRadiusAxis
                          angle={30}
                          domain={[0, 100]}
                          tick={{ fill: '#64748b', fontSize: 10 }}
                        />
                        <Radar
                          name="Diagnostic Baseline"
                          dataKey="Baseline"
                          stroke="#64748b"
                          fill="#64748b"
                          fillOpacity={0.25}
                        />
                        <Radar
                          name="Current Demonstrated"
                          dataKey="Current"
                          stroke="#06b6d4"
                          fill="#06b6d4"
                          fillOpacity={0.4}
                        />
                        <Radar
                          name="Role Target"
                          dataKey="Target"
                          stroke="#a855f7"
                          fill="transparent"
                          strokeDasharray="4 4"
                        />
                        <Legend
                          wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                        />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderRadius: '8px',
                            color: '#f8fafc',
                            fontSize: '12px',
                          }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-center text-xs text-slate-500">
                      Insufficient competency baseline data to generate radar comparison.
                    </div>
                  )}
                </div>
              </div>

              {/* Trajectory: Longitudinal Progression Over Time */}
              <div className="p-6 rounded-2xl bg-[#0B1120] border border-slate-800 shadow-xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                      Longitudinal Competency Trajectory
                    </h3>
                    {performance.competencies.length > 0 && (
                      <select
                        value={selectedTrajectoryComp}
                        onChange={(e) => setSelectedTrajectoryComp(e.target.value)}
                        className="text-[11px] rounded-lg bg-slate-900 border border-slate-800 text-slate-300 px-2 py-1 focus:outline-none focus:border-emerald-500/50"
                      >
                        <option value="ALL">Aggregate Overview</option>
                        {performance.competencies.map((c) => (
                          <option key={c.competency_id} value={c.competency_id}>
                            {c.competency_name}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mb-4">
                    Score progression chronologically verified across all assessments and learning milestones.
                  </p>
                </div>

                <div className="w-full h-72 flex items-center justify-center">
                  {trajectoryData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={trajectoryData}
                        margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                      >
                        <defs>
                          <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis
                          dataKey="date"
                          tick={{ fill: '#64748b', fontSize: 11 }}
                          stroke="#334155"
                        />
                        <YAxis
                          domain={[0, 100]}
                          tick={{ fill: '#64748b', fontSize: 11 }}
                          stroke="#334155"
                        />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderRadius: '8px',
                            color: '#f8fafc',
                            fontSize: '12px',
                          }}
                          formatter={(val: unknown) => [`${val}%`, 'Score']}
                        />
                        <Area
                          type="monotone"
                          dataKey="score"
                          stroke="#10b981"
                          strokeWidth={2}
                          fillOpacity={1}
                          fill="url(#scoreGrad)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-center text-xs text-slate-500">
                      No longitudinal milestones recorded yet. Complete assessments or labs to establish history.
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Strengths & Priority Focus Areas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Strengths Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-emerald-950/20 via-slate-900 to-slate-900 border border-emerald-900/30 shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-emerald-400" />
                    Top Demonstrated Strengths
                  </h3>
                  <span className="text-xs text-emerald-400/80 font-mono">
                    Highest Proficiency
                  </span>
                </div>

                {performance.strongest_competencies.length > 0 ? (
                  <div className="space-y-3">
                    {performance.strongest_competencies.map((st) => (
                      <div
                        key={st.competency_id}
                        className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs font-mono">
                            {st.rank}
                          </span>
                          <div>
                            <div className="text-sm font-semibold text-slate-200">
                              {st.competency_name}
                            </div>
                            <div className="text-[11px] text-slate-400">
                              {st.domain_name || 'Core Competency'} • {st.highlight}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-base font-bold text-emerald-400 font-mono">
                            {st.current_score.toFixed(1)}
                          </div>
                          {st.improvement_points > 0 && (
                            <div className="text-[10px] text-emerald-400/80">
                              +{st.improvement_points.toFixed(1)} growth
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="py-6 text-center text-xs text-slate-500">
                    Complete learning evaluations to identify demonstrated strengths.
                  </div>
                )}
              </div>

              {/* Focus Areas Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-rose-950/20 via-slate-900 to-slate-900 border border-rose-900/30 shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    Priority Focus Areas
                  </h3>
                  <Link
                    href="/employee/gaps"
                    className="text-xs text-rose-400 hover:text-rose-300 font-medium transition flex items-center gap-1"
                  >
                    View All Gaps <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>

                {performance.focus_competencies.length > 0 ? (
                  <div className="space-y-3">
                    {performance.focus_competencies.map((fc) => (
                      <div
                        key={fc.competency_id}
                        className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/90 flex items-center justify-between"
                      >
                        <div>
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-sm font-semibold text-slate-200">
                              {fc.competency_name}
                            </span>
                            <span
                              className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                                fc.priority_level === 'CRITICAL'
                                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                                  : fc.priority_level === 'HIGH'
                                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                                  : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                              }`}
                            >
                              {fc.priority_level}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 max-w-sm line-clamp-1">
                            {fc.explanation}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-mono text-slate-300 font-medium">
                            <span className="text-cyan-400 font-bold">{fc.current_score.toFixed(1)}</span>
                            {fc.target_score && (
                              <span className="text-slate-500"> / {fc.target_score.toFixed(1)}</span>
                            )}
                          </div>
                          <div className="text-[10px] text-rose-400 font-medium">
                            Gap: -{fc.gap_score.toFixed(1)} pts
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="py-6 text-center text-xs text-slate-500">
                    No active critical or high priority skill gaps detected.
                  </div>
                )}
              </div>
            </div>

            {/* Modality Performance Matrix */}
            <div>
              <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2 mb-3">
                <Zap className="w-4 h-4 text-cyan-400" />
                Performance Across Learning Modalities
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                {/* 1. Diagnostic */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 shadow-md">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5 text-cyan-400" /> Diagnostic
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        performance.modalities.diagnostic.status === 'COMPLETED'
                          ? 'bg-emerald-500/15 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {performance.modalities.diagnostic.status}
                    </span>
                  </div>
                  <div className="text-xl font-bold text-slate-100 font-mono">
                    {performance.modalities.diagnostic.latest_score !== null &&
                    performance.modalities.diagnostic.latest_score !== undefined
                      ? `${performance.modalities.diagnostic.latest_score.toFixed(1)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {performance.modalities.diagnostic.completed_count} completed /{' '}
                    {performance.modalities.diagnostic.attempts_count} attempted
                  </div>
                </div>

                {/* 2. Quizzes */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 shadow-md">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <Brain className="w-3.5 h-3.5 text-purple-400" /> AI Quizzes
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        performance.modalities.quizzes.status === 'COMPLETED'
                          ? 'bg-emerald-500/15 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {performance.modalities.quizzes.status}
                    </span>
                  </div>
                  <div className="text-xl font-bold text-slate-100 font-mono">
                    {performance.modalities.quizzes.average_percentage !== null &&
                    performance.modalities.quizzes.average_percentage !== undefined
                      ? `${performance.modalities.quizzes.average_percentage.toFixed(1)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    Pass rate:{' '}
                    {performance.modalities.quizzes.pass_rate !== null &&
                    performance.modalities.quizzes.pass_rate !== undefined
                      ? `${performance.modalities.quizzes.pass_rate.toFixed(0)}%`
                      : 'N/A'}{' '}
                    ({performance.modalities.quizzes.completed_count} quizzes)
                  </div>
                </div>

                {/* 3. Adaptive CAT */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 shadow-md">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <GraduationCap className="w-3.5 h-3.5 text-blue-400" /> Adaptive CAT
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        performance.modalities.adaptive_assessment.status === 'COMPLETED'
                          ? 'bg-emerald-500/15 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {performance.modalities.adaptive_assessment.status}
                    </span>
                  </div>
                  <div className="text-xl font-bold text-slate-100 font-mono">
                    {performance.modalities.adaptive_assessment.average_confidence !== null &&
                    performance.modalities.adaptive_assessment.average_confidence !== undefined
                      ? `${(performance.modalities.adaptive_assessment.average_confidence * 100).toFixed(0)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {performance.modalities.adaptive_assessment.competencies_evaluated_count} competencies recalibrated
                  </div>
                </div>

                {/* 4. Virtual Labs */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 shadow-md">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <FlaskConical className="w-3.5 h-3.5 text-teal-400" /> Virtual Labs
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        performance.modalities.virtual_labs.status === 'COMPLETED'
                          ? 'bg-emerald-500/15 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {performance.modalities.virtual_labs.status}
                    </span>
                  </div>
                  <div className="text-xl font-bold text-slate-100 font-mono">
                    {performance.modalities.virtual_labs.average_score !== null &&
                    performance.modalities.virtual_labs.average_score !== undefined
                      ? `${performance.modalities.virtual_labs.average_score.toFixed(1)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {performance.modalities.virtual_labs.completed_scenarios_count} scenarios verified
                  </div>
                </div>

                {/* 5. Courses */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 shadow-md">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-amber-400" /> Courses
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        performance.modalities.courses.status === 'COMPLETED'
                          ? 'bg-emerald-500/15 text-emerald-400'
                          : performance.modalities.courses.status === 'IN_PROGRESS'
                          ? 'bg-blue-500/15 text-blue-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {performance.modalities.courses.status}
                    </span>
                  </div>
                  <div className="text-xl font-bold text-slate-100 font-mono">
                    {performance.modalities.courses.average_progress_percentage !== null &&
                    performance.modalities.courses.average_progress_percentage !== undefined
                      ? `${performance.modalities.courses.average_progress_percentage.toFixed(0)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {performance.modalities.courses.completed_modules_count} modules completed
                  </div>
                </div>
              </div>
            </div>

            {/* Competency Level Progress Breakdown Table */}
            <div className="p-6 rounded-2xl bg-[#0B1120] border border-slate-800 shadow-xl space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Target className="w-4 h-4 text-cyan-400" />
                    Competency Evolution & Growth
                  </h3>
                  <p className="text-xs text-slate-400">
                    Comprehensive baseline vs current score comparison with role target alignment.
                  </p>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap items-center gap-2.5">
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search competencies..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-48"
                    />
                  </div>

                  {domains.length > 0 && (
                    <select
                      value={selectedDomain}
                      onChange={(e) => setSelectedDomain(e.target.value)}
                      className="text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-300 px-3 py-1.5 focus:outline-none focus:border-cyan-500/50"
                    >
                      <option value="ALL">All Domains</option>
                      {domains.map((d) => (
                        <option key={d} value={d}>
                          {d}
                        </option>
                      ))}
                    </select>
                  )}

                  <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-300 px-3 py-1.5 focus:outline-none focus:border-cyan-500/50"
                  >
                    <option value="ALL">All Statuses</option>
                    <option value="MASTERED">Mastered</option>
                    <option value="IMPROVING">Improving</option>
                    <option value="NEEDS_FOCUS">Needs Focus</option>
                    <option value="STABLE">Stable</option>
                    <option value="NO_BASELINE">No Baseline</option>
                  </select>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                      <th className="py-3 px-3">Competency</th>
                      <th className="py-3 px-3">Domain</th>
                      <th className="py-3 px-3 text-center">Baseline</th>
                      <th className="py-3 px-3 text-center">Current</th>
                      <th className="py-3 px-3 text-center">Role Target</th>
                      <th className="py-3 px-3 text-center">Improvement</th>
                      <th className="py-3 px-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredCompetencies.map((comp) => (
                      <tr
                        key={comp.competency_id}
                        className="hover:bg-slate-800/40 transition-colors"
                      >
                        <td className="py-3.5 px-3">
                          <div className="font-semibold text-slate-200">
                            {comp.competency_name}
                          </div>
                          <div className="text-[10px] font-mono text-cyan-400">
                            {comp.competency_code}
                          </div>
                        </td>
                        <td className="py-3.5 px-3 text-slate-400">
                          {comp.domain_name || 'Core'}
                        </td>
                        <td className="py-3.5 px-3 text-center font-mono text-slate-400">
                          {comp.baseline_score !== null && comp.baseline_score !== undefined
                            ? comp.baseline_score.toFixed(1)
                            : '—'}
                        </td>
                        <td className="py-3.5 px-3 text-center">
                          <span className="font-mono font-bold text-cyan-400 text-sm">
                            {comp.current_score.toFixed(1)}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-center font-mono text-violet-400">
                          {comp.target_score !== null && comp.target_score !== undefined
                            ? comp.target_score.toFixed(1)
                            : '—'}
                        </td>
                        <td className="py-3.5 px-3 text-center">
                          {comp.baseline_score !== null && comp.baseline_score !== undefined ? (
                            <span
                              className={`font-mono font-medium ${
                                comp.improvement_points > 0
                                  ? 'text-emerald-400'
                                  : comp.improvement_points < 0
                                  ? 'text-rose-400'
                                  : 'text-slate-400'
                              }`}
                            >
                              {comp.improvement_points > 0 ? '+' : ''}
                              {comp.improvement_points.toFixed(1)}
                              <span className="text-[10px] text-slate-500 ml-1">
                                ({comp.improvement_percentage > 0 ? '+' : ''}
                                {comp.improvement_percentage.toFixed(0)}%)
                              </span>
                            </span>
                          ) : (
                            <span className="text-slate-600 font-mono text-[10px]">
                              N/A
                            </span>
                          )}
                        </td>
                        <td className="py-3.5 px-3 text-center">
                          {renderStatusBadge(comp.status)}
                        </td>
                      </tr>
                    ))}
                    {filteredCompetencies.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-8 text-center text-slate-500">
                          No competencies matching the active search or filters.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </PageContainer>
    </AppShell>
  );
}
