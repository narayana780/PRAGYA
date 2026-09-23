'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Users,
  Target,
  AlertTriangle,
  Search,
  RefreshCw,
  Award,
  Layers,
  BarChart3,
  Shield,
  ChevronRight,
  Briefcase,
  X,
  ExternalLink,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Cell,
} from 'recharts';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import {
  useWorkforceOverview,
  useWorkforceCompetencies,
  useDepartmentAnalytics,
  useDepartmentHeatmap,
  useWorkforceGaps,
  useRoleAnalytics,
  useAdminEmployeeList,
} from '@/hooks/use-admin-workforce';
import { useEmployeePerformance, useEmployeePerformanceTimeline } from '@/hooks/use-performance';

type TabType = 'overview' | 'competencies' | 'gaps' | 'heatmap' | 'roles' | 'roster';

export default function AdminWorkforcePage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);

  // Queries
  const {
    data: overview,
    isLoading: overviewLoading,
    error: overviewError,
    refetch: refetchOverview,
  } = useWorkforceOverview();

  const {
    data: competenciesData,
    isLoading: compLoading,
  } = useWorkforceCompetencies();

  const {
    data: deptData,
    isLoading: deptLoading,
  } = useDepartmentAnalytics();

  const {
    data: heatmapData,
    isLoading: heatmapLoading,
  } = useDepartmentHeatmap();

  const {
    data: gapsData,
    isLoading: gapsLoading,
  } = useWorkforceGaps();

  const {
    data: rolesData,
    isLoading: rolesLoading,
  } = useRoleAnalytics();

  const {
    data: rosterData,
    isLoading: rosterLoading,
  } = useAdminEmployeeList();

  // Selected employee performance for drilldown
  const {
    data: drilldownPerf,
    isLoading: drilldownLoading,
  } = useEmployeePerformance(selectedEmployeeId || undefined);

  const {
    data: drilldownTimeline,
  } = useEmployeePerformanceTimeline(selectedEmployeeId || undefined, 'ALL', 10);

  // Filtered employees for drilldown roster
  const filteredEmployees = useMemo(() => {
    if (!rosterData?.employees) return [];
    if (!searchQuery.trim()) return rosterData.employees;
    const q = searchQuery.toLowerCase();
    return rosterData.employees.filter(
      (e) =>
        e.full_name.toLowerCase().includes(q) ||
        e.employee_code.toLowerCase().includes(q) ||
        e.department_name.toLowerCase().includes(q) ||
        e.role_name.toLowerCase().includes(q)
    );
  }, [rosterData, searchQuery]);

  // Chart data for top competencies
  const chartCompetencies = useMemo(() => {
    if (!competenciesData?.competencies) return [];
    return competenciesData.competencies.slice(0, 8).map((c) => ({
      name: c.name.length > 22 ? c.name.slice(0, 20) + '...' : c.name,
      fullName: c.name,
      average: c.average_score,
      officers: c.employee_count,
      domain: c.domain,
    }));
  }, [competenciesData]);

  return (
    <AppShell role="ADMIN" pageTitle="Workforce Intelligence">
      <PageContainer>
        {/* HEADER */}
        <PageHeader
          title="Workforce Intelligence & Cadre Analytics"
          subtitle="Real-time capability benchmarks, competency distributions, and departmental skill gaps across official statistical cadres."
          badge={
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-violet-500/10 text-violet-300 border border-violet-500/30 font-mono">
              <Shield className="w-3.5 h-3.5 text-violet-400" />
              <span>MoSPI Headquarters View</span>
            </div>
          }
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Workforce Intelligence' },
          ]}
        />

        {/* REFRESH & ERROR BANNER */}
        {overviewError && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-rose-300 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Failed to load workforce intelligence data. Please verify database connection.</span>
            </div>
            <button
              onClick={() => refetchOverview()}
              className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* EXECUTIVE OVERVIEW KPI CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {/* Card 1: Total Personnel */}
          <GlassCard variant="elevated" className="p-5 flex flex-col justify-between relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>DEPLOYED CADRE</span>
              <Users className="w-4 h-4 text-violet-400" />
            </div>
            <div className="space-y-1">
              <div className="text-2xl lg:text-3xl font-bold text-white tracking-tight">
                {overviewLoading ? (
                  <div className="h-8 w-16 bg-white/10 animate-pulse rounded" />
                ) : (
                  overview?.active_employees ?? '—'
                )}
              </div>
              <div className="text-xs text-slate-400 flex items-center gap-1.5">
                <span>Total Registered:</span>
                <span className="font-semibold text-slate-200">{overview?.total_employees ?? '—'}</span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
              <span>Assessed: {overview?.employees_assessed ?? 0}</span>
              <span className="text-violet-400 font-mono">{overview?.departments_count ?? 0} Divisions</span>
            </div>
          </GlassCard>

          {/* Card 2: Average Competency */}
          <GlassCard variant="elevated" className="p-5 flex flex-col justify-between relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>WORKFORCE COMPETENCY</span>
              <Award className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="space-y-1">
              <div className="text-2xl lg:text-3xl font-bold text-cyan-300 tracking-tight">
                {overviewLoading ? (
                  <div className="h-8 w-20 bg-white/10 animate-pulse rounded" />
                ) : overview?.average_competency_score !== null && overview?.average_competency_score !== undefined ? (
                  `${overview.average_competency_score.toFixed(1)} / 100`
                ) : (
                  <span className="text-slate-400 text-lg">No data</span>
                )}
              </div>
              <div className="text-xs text-slate-400">
                <span>Target Benchmark: </span>
                <span className="font-semibold text-slate-200">70.0 pts</span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
              <span>Tracked: {overview?.competencies_tracked ?? 0}</span>
              <span className="text-cyan-400 font-mono">Real-Time Evidence</span>
            </div>
          </GlassCard>

          {/* Card 3: Average Role Readiness */}
          <GlassCard variant="elevated" className="p-5 flex flex-col justify-between relative overflow-hidden">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>ROLE READINESS</span>
              <Target className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="space-y-1">
              <div className="text-2xl lg:text-3xl font-bold text-emerald-300 tracking-tight">
                {overviewLoading ? (
                  <div className="h-8 w-20 bg-white/10 animate-pulse rounded" />
                ) : overview?.average_role_readiness !== null && overview?.average_role_readiness !== undefined ? (
                  `${overview.average_role_readiness.toFixed(1)}%`
                ) : (
                  <span className="text-slate-400 text-lg">No data</span>
                )}
              </div>
              <div className="text-xs text-slate-400">
                <span>Cadre Targets Met: </span>
                <span className="font-semibold text-slate-200">
                  {overview?.average_role_readiness && overview.average_role_readiness >= 75 ? 'Optimal' : 'In Progress'}
                </span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
              <span>Roles: {overview?.roles_count ?? 0}</span>
              <span className="text-emerald-400 font-mono">Official Cadres</span>
            </div>
          </GlassCard>

          {/* Card 4: Officers Needing Attention */}
          <GlassCard variant="elevated" className="p-5 flex flex-col justify-between relative overflow-hidden border-rose-500/20">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span>NEEDS ATTENTION</span>
              <AlertTriangle className="w-4 h-4 text-rose-400" />
            </div>
            <div className="space-y-1">
              <div className="text-2xl lg:text-3xl font-bold text-rose-400 tracking-tight">
                {overviewLoading ? (
                  <div className="h-8 w-16 bg-white/10 animate-pulse rounded" />
                ) : (
                  overview?.employees_needing_attention ?? 0
                )}
              </div>
              <div className="text-xs text-slate-400">
                <span>High/Critical Deficits</span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
              <span className="text-rose-400 font-medium">Intervention Focus</span>
              <button
                onClick={() => setActiveTab('roster')}
                className="text-xs text-rose-300 hover:text-rose-200 font-semibold underline"
              >
                View Roster
              </button>
            </div>
          </GlassCard>
        </div>

        {/* NAVIGATION TABS */}
        <div className="flex items-center gap-2 border-b border-white/10 mb-6 pb-2 overflow-x-auto text-xs font-medium">
          {[
            { id: 'overview', label: 'Workforce Overview', icon: BarChart3 },
            { id: 'competencies', label: 'Competency Distribution', icon: Award },
            { id: 'gaps', label: 'Priority Skill Gaps', icon: AlertTriangle },
            { id: 'heatmap', label: 'Department Heatmap', icon: Layers },
            { id: 'roles', label: 'Role & Cadre Readiness', icon: Briefcase },
            { id: 'roster', label: 'Personnel Drill-Down', icon: Users },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors whitespace-nowrap ${
                  isActive
                    ? 'bg-violet-600 text-white font-semibold shadow-lg shadow-violet-600/20'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* TAB 1: WORKFORCE OVERVIEW (DASHBOARD MIX) */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Top Row: Competency Chart & Priority Gaps */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Competency Distribution Horizontal Bar Chart */}
              <GlassCard variant="elevated" className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-tight">Competency Benchmark Distribution</h3>
                    <p className="text-xs text-slate-400">Average demonstrated capability across assessed personnel</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('competencies')}
                    className="text-xs text-violet-400 hover:text-violet-300 font-semibold flex items-center gap-1"
                  >
                    <span>Full View</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {compLoading ? (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
                    Loading competency analytics...
                  </div>
                ) : chartCompetencies.length > 0 ? (
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartCompetencies} layout="vertical" margin={{ left: 10, right: 20, top: 10, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                        <XAxis type="number" domain={[0, 100]} stroke="#64748B" fontSize={11} tickLine={false} />
                        <YAxis
                          type="category"
                          dataKey="name"
                          stroke="#94A3B8"
                          fontSize={11}
                          tickLine={false}
                          width={110}
                        />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: '#0F172A',
                            borderColor: 'rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            color: '#F8FAFC',
                            fontSize: '12px',
                          }}
                          formatter={(value: unknown, _name: unknown, item: unknown) => {
                            const entry = item as { payload?: { fullName?: string; officers?: number } };
                            return [
                              `${value} / 100 (${entry?.payload?.officers ?? 0} personnel)`,
                              entry?.payload?.fullName ?? '',
                            ];
                          }}
                        />
                        <Bar dataKey="average" radius={[0, 4, 4, 0]}>
                          {chartCompetencies.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={
                                entry.average >= 75
                                  ? '#10B981'
                                  : entry.average >= 50
                                  ? '#06B6D4'
                                  : '#F43F5E'
                              }
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
                    No competency data available.
                  </div>
                )}
              </GlassCard>

              {/* Top Workforce Skill Gaps */}
              <GlassCard variant="elevated" className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-tight">Top Workforce Deficits</h3>
                    <p className="text-xs text-slate-400">Most critical skill gaps requiring training intervention</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('gaps')}
                    className="text-xs text-violet-400 hover:text-violet-300 font-semibold flex items-center gap-1"
                  >
                    <span>All Gaps</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {gapsLoading ? (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
                    Loading skill gap analytics...
                  </div>
                ) : gapsData?.top_workforce_gaps && gapsData.top_workforce_gaps.length > 0 ? (
                  <div className="space-y-3">
                    {gapsData.top_workforce_gaps.slice(0, 4).map((gap) => (
                      <div
                        key={gap.competency_id}
                        className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between"
                      >
                        <div className="space-y-1">
                          <div className="text-xs font-semibold text-white">{gap.competency_name}</div>
                          <div className="text-[11px] text-slate-400 flex items-center gap-2 font-mono">
                            <span>{gap.domain_name}</span>
                            <span>•</span>
                            <span className="text-slate-300">{gap.affected_employees} personnel affected</span>
                          </div>
                        </div>
                        <div className="text-right space-y-1">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                              gap.highest_priority_level === 'CRITICAL'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : gap.highest_priority_level === 'HIGH'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                            }`}
                          >
                            {gap.highest_priority_level}
                          </span>
                          <div className="text-[11px] font-mono text-slate-400">
                            Avg Gap: <span className="font-semibold text-white">{gap.average_gap_score.toFixed(1)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
                    No critical skill gaps detected across the workforce.
                  </div>
                )}
              </GlassCard>
            </div>

            {/* Department Comparison Table */}
            <GlassCard variant="elevated" className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white tracking-tight">Departmental Capability Comparison</h3>
                  <p className="text-xs text-slate-400">Comparative evaluation across MoSPI directorates & field divisions</p>
                </div>
                <Link
                  href="/admin/departments"
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
                >
                  <span>Dedicated Department Analysis</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>

              {deptLoading ? (
                <div className="py-8 text-center text-slate-400 text-xs">Loading department analytics...</div>
              ) : deptData?.departments && deptData.departments.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                        <th className="py-2.5 px-3">Department</th>
                        <th className="py-2.5 px-3 text-center">Personnel</th>
                        <th className="py-2.5 px-3 text-center">Avg Competency</th>
                        <th className="py-2.5 px-3 text-center">Role Readiness</th>
                        <th className="py-2.5 px-3 text-center">Critical Gaps</th>
                        <th className="py-2.5 px-3">Primary Focus Area</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {deptData.departments.map((dept) => (
                        <tr key={dept.department_id} className="hover:bg-white/5 transition-colors">
                          <td className="py-3 px-3">
                            <div className="font-semibold text-white">{dept.department_name}</div>
                            <div className="text-[10px] font-mono text-slate-400">{dept.department_code}</div>
                          </td>
                          <td className="py-3 px-3 text-center font-mono font-medium text-slate-200">
                            {dept.employee_count}
                          </td>
                          <td className="py-3 px-3 text-center">
                            {dept.average_competency_score !== null ? (
                              <span className="font-mono font-bold text-cyan-300">
                                {dept.average_competency_score.toFixed(1)}
                              </span>
                            ) : (
                              <span className="text-slate-500">No data</span>
                            )}
                          </td>
                          <td className="py-3 px-3 text-center">
                            {dept.average_role_readiness !== null ? (
                              <div className="inline-flex items-center gap-1.5 font-mono font-medium">
                                <span className="text-emerald-300">{dept.average_role_readiness.toFixed(1)}%</span>
                              </div>
                            ) : (
                              <span className="text-slate-500">No data</span>
                            )}
                          </td>
                          <td className="py-3 px-3 text-center">
                            {dept.critical_gap_count > 0 ? (
                              <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 font-mono text-[10px] font-bold">
                                {dept.critical_gap_count} Critical
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px] font-mono">
                                0 Deficits
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-3 text-slate-300">
                            {dept.top_competency_gaps.length > 0 ? (
                              <span className="text-rose-300">{dept.top_competency_gaps[0]}</span>
                            ) : (
                              <span className="text-emerald-400">On Track</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">No department data recorded.</div>
              )}
            </GlassCard>
          </div>
        )}

        {/* TAB 2: COMPETENCY DISTRIBUTION FULL VIEW */}
        {activeTab === 'competencies' && (
          <GlassCard variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">Official Competency Framework Distribution</h3>
                <p className="text-xs text-slate-400">Comprehensive score averages, score range spread, and proficiency levels</p>
              </div>
              <div className="text-xs font-mono text-cyan-400">
                {competenciesData?.total_tracked ?? 0} Tracked Competencies
              </div>
            </div>

            {compLoading ? (
              <div className="py-12 text-center text-slate-400 text-xs">Loading competencies...</div>
            ) : competenciesData?.competencies && competenciesData.competencies.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                      <th className="py-2.5 px-3">Competency</th>
                      <th className="py-2.5 px-3">Domain</th>
                      <th className="py-2.5 px-3 text-center">Personnel Evaluated</th>
                      <th className="py-2.5 px-3 text-center">Average Score</th>
                      <th className="py-2.5 px-3 text-center">Min / Max</th>
                      <th className="py-2.5 px-3 text-center">Proficiency Breakdown</th>
                      <th className="py-2.5 px-3 text-center">Critical Gaps</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {competenciesData.competencies.map((comp) => (
                      <tr key={comp.competency_id} className="hover:bg-white/5 transition-colors">
                        <td className="py-3 px-3">
                          <div className="font-semibold text-white">{comp.name}</div>
                          <div className="text-[10px] font-mono text-slate-400">{comp.code}</div>
                        </td>
                        <td className="py-3 px-3 text-slate-300 font-mono text-[11px]">{comp.domain}</td>
                        <td className="py-3 px-3 text-center font-mono font-medium text-slate-200">
                          {comp.employee_count}
                        </td>
                        <td className="py-3 px-3 text-center">
                          <span
                            className={`font-mono font-bold ${
                              comp.average_score >= 75
                                ? 'text-emerald-300'
                                : comp.average_score >= 50
                                ? 'text-cyan-300'
                                : 'text-rose-400'
                            }`}
                          >
                            {comp.average_score.toFixed(1)}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-center font-mono text-[11px] text-slate-400">
                          {comp.minimum_score.toFixed(0)} — {comp.maximum_score.toFixed(0)}
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex items-center justify-center gap-1 text-[10px] font-mono">
                            <span title="Advanced" className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                              A: {comp.proficiency_distribution.ADVANCED ?? 0}
                            </span>
                            <span title="Proficient" className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
                              P: {comp.proficiency_distribution.PROFICIENT ?? 0}
                            </span>
                            <span title="Developing" className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">
                              D: {comp.proficiency_distribution.DEVELOPING ?? 0}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-3 text-center">
                          {comp.critical_gap_count > 0 ? (
                            <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 font-mono text-[10px] font-bold">
                              {comp.critical_gap_count} Critical
                            </span>
                          ) : (
                            <span className="text-slate-500 font-mono text-[10px]">None</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs">No competencies tracked.</div>
            )}
          </GlassCard>
        )}

        {/* TAB 3: WORKFORCE GAPS FULL VIEW */}
        {activeTab === 'gaps' && (
          <div className="space-y-6">
            {/* Priority Totals Summary */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
                <div className="text-xl font-bold text-white font-mono">{gapsData?.total_gaps ?? 0}</div>
                <div className="text-[11px] text-slate-400">Total Skill Gaps</div>
              </div>
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-center">
                <div className="text-xl font-bold text-rose-400 font-mono">{gapsData?.critical_gaps ?? 0}</div>
                <div className="text-[11px] text-rose-300">Critical Priority</div>
              </div>
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-center">
                <div className="text-xl font-bold text-amber-400 font-mono">{gapsData?.high_gaps ?? 0}</div>
                <div className="text-[11px] text-amber-300">High Priority</div>
              </div>
              <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-center">
                <div className="text-xl font-bold text-cyan-400 font-mono">{gapsData?.medium_gaps ?? 0}</div>
                <div className="text-[11px] text-cyan-300">Medium Priority</div>
              </div>
              <div className="p-4 rounded-xl bg-slate-500/10 border border-slate-500/20 text-center">
                <div className="text-xl font-bold text-slate-300 font-mono">{gapsData?.low_gaps ?? 0}</div>
                <div className="text-[11px] text-slate-400">Low Priority</div>
              </div>
            </div>

            <GlassCard variant="elevated" className="p-6">
              <h3 className="text-sm font-bold text-white tracking-tight mb-4">
                Prioritized Skill Gap Deficits
              </h3>

              {gapsLoading ? (
                <div className="py-8 text-center text-slate-400 text-xs">Loading gap rankings...</div>
              ) : gapsData?.top_workforce_gaps && gapsData.top_workforce_gaps.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                        <th className="py-2.5 px-3">Competency</th>
                        <th className="py-2.5 px-3">Domain</th>
                        <th className="py-2.5 px-3 text-center">Affected Personnel</th>
                        <th className="py-2.5 px-3 text-center">Average Gap Score</th>
                        <th className="py-2.5 px-3 text-center">Priority Level</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {gapsData.top_workforce_gaps.map((gap) => (
                        <tr key={gap.competency_id} className="hover:bg-white/5 transition-colors">
                          <td className="py-3 px-3">
                            <div className="font-semibold text-white">{gap.competency_name}</div>
                            <div className="text-[10px] font-mono text-slate-400">{gap.competency_code}</div>
                          </td>
                          <td className="py-3 px-3 text-slate-300 font-mono text-[11px]">{gap.domain_name}</td>
                          <td className="py-3 px-3 text-center font-mono font-medium text-slate-200">
                            {gap.affected_employees}
                          </td>
                          <td className="py-3 px-3 text-center font-mono font-bold text-rose-400">
                            {gap.average_gap_score.toFixed(1)} pts
                          </td>
                          <td className="py-3 px-3 text-center">
                            <span
                              className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                                gap.highest_priority_level === 'CRITICAL'
                                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                  : gap.highest_priority_level === 'HIGH'
                                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                  : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                              }`}
                            >
                              {gap.highest_priority_level}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">No skill gaps identified.</div>
              )}
            </GlassCard>
          </div>
        )}

        {/* TAB 4: WORKFORCE HEATMAP */}
        {activeTab === 'heatmap' && (
          <GlassCard variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">Workforce Capability Matrix (Heatmap)</h3>
                <p className="text-xs text-slate-400">Department × Competency average demonstrated capability scores</p>
              </div>
              <div className="flex items-center gap-3 text-[11px] font-mono">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded bg-emerald-500/60" />
                  <span className="text-slate-300">&gt; 75 (High)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded bg-cyan-500/60" />
                  <span className="text-slate-300">50-75 (Moderate)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded bg-rose-500/60" />
                  <span className="text-slate-300">&lt; 50 (Critical)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded bg-white/10" />
                  <span className="text-slate-400">No Data</span>
                </div>
              </div>
            </div>

            {heatmapLoading ? (
              <div className="py-12 text-center text-slate-400 text-xs">Loading capability heatmap...</div>
            ) : heatmapData?.departments && heatmapData.departments.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="py-3 px-3 text-slate-400 font-mono uppercase text-[10px] min-w-[160px]">
                        Department
                      </th>
                      {heatmapData.competencies_reference.map((comp) => (
                        <th
                          key={comp.id}
                          className="py-3 px-2 text-center text-slate-300 font-mono text-[10px] min-w-[90px]"
                          title={`${comp.name} (${comp.code})`}
                        >
                          {comp.code}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {heatmapData.departments.map((dept) => (
                      <tr key={dept.department_id} className="hover:bg-white/5">
                        <td className="py-2.5 px-3 font-semibold text-white whitespace-nowrap">
                          {dept.department_name}
                        </td>
                        {dept.competencies.map((c) => {
                          const score = c.average_score;
                          let bgClass = 'bg-white/5 text-slate-500';
                          if (score !== null) {
                            if (score >= 75) {
                              bgClass = 'bg-emerald-500/30 text-emerald-200 font-semibold border border-emerald-500/40';
                            } else if (score >= 50) {
                              bgClass = 'bg-cyan-500/30 text-cyan-200 font-semibold border border-cyan-500/40';
                            } else {
                              bgClass = 'bg-rose-500/30 text-rose-200 font-semibold border border-rose-500/40';
                            }
                          }
                          return (
                            <td key={c.competency_id} className="py-2.5 px-2 text-center">
                              <div
                                className={`py-1.5 px-2 rounded font-mono text-[11px] ${bgClass}`}
                                title={`${dept.department_name} • ${c.competency_name}: ${
                                  score !== null ? `${score.toFixed(1)} pts (${c.employee_count} assessed)` : 'No Data'
                                }`}
                              >
                                {score !== null ? score.toFixed(0) : '—'}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs">No heatmap data available.</div>
            )}
          </GlassCard>
        )}

        {/* TAB 5: ROLE / CADRE ANALYSIS */}
        {activeTab === 'roles' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rolesLoading ? (
              <div className="col-span-full py-12 text-center text-slate-400 text-xs">Loading cadre benchmarks...</div>
            ) : rolesData?.roles && rolesData.roles.length > 0 ? (
              rolesData.roles.map((role) => (
                <GlassCard key={role.role_id} variant="elevated" className="p-5 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/30 font-mono text-[10px]">
                        {role.career_level}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">{role.role_code}</span>
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">{role.role_name}</h4>
                      <p className="text-xs text-slate-400">
                        {role.employee_count} personnel deployed in role
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5 text-xs font-mono">
                      <div>
                        <div className="text-[10px] text-slate-500">AVG READINESS</div>
                        <div className="font-bold text-emerald-300">
                          {role.average_role_readiness !== null ? `${role.average_role_readiness.toFixed(1)}%` : '—'}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500">BELOW TARGET</div>
                        <div className="font-bold text-rose-400">
                          {role.employees_below_target} personnel
                        </div>
                      </div>
                    </div>

                    {role.major_skill_gaps.length > 0 && (
                      <div className="pt-2">
                        <div className="text-[10px] text-slate-500 font-mono uppercase mb-1">Major Deficits:</div>
                        <div className="flex flex-wrap gap-1">
                          {role.major_skill_gaps.map((g, idx) => (
                            <span key={idx} className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300 text-[10px]">
                              {g}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
                    <span>Requirements: {role.competency_requirements_count}</span>
                    <button
                      onClick={() => {
                        setActiveTab('roster');
                        setSearchQuery(role.role_name);
                      }}
                      className="text-cyan-400 hover:text-cyan-300 font-semibold"
                    >
                      Filter Roster →
                    </button>
                  </div>
                </GlassCard>
              ))
            ) : (
              <div className="col-span-full py-12 text-center text-slate-400 text-xs">No cadre records found.</div>
            )}
          </div>
        )}

        {/* TAB 6: PERSONNEL DRILL-DOWN ROSTER */}
        {activeTab === 'roster' && (
          <GlassCard variant="elevated" className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">Executive Personnel Roster</h3>
                <p className="text-xs text-slate-400">Select any officer to inspect their longitudinal capability profile</p>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by name, code, role..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-violet-500"
                />
              </div>
            </div>

            {rosterLoading ? (
              <div className="py-12 text-center text-slate-400 text-xs">Loading personnel roster...</div>
            ) : filteredEmployees.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                      <th className="py-2.5 px-3">Officer Code & Name</th>
                      <th className="py-2.5 px-3">Designation</th>
                      <th className="py-2.5 px-3">Division</th>
                      <th className="py-2.5 px-3 text-center">Avg Competency</th>
                      <th className="py-2.5 px-3 text-center">Role Readiness</th>
                      <th className="py-2.5 px-3 text-center">Status</th>
                      <th className="py-2.5 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {filteredEmployees.map((emp) => (
                      <tr key={emp.id} className="hover:bg-white/5 transition-colors">
                        <td className="py-3 px-3">
                          <div className="font-semibold text-white">{emp.full_name}</div>
                          <div className="text-[10px] font-mono text-cyan-400">{emp.employee_code}</div>
                        </td>
                        <td className="py-3 px-3 text-slate-300">
                          <div>{emp.designation}</div>
                          <div className="text-[10px] text-slate-500 font-mono">{emp.role_name}</div>
                        </td>
                        <td className="py-3 px-3 text-slate-300 font-mono text-[11px]">
                          {emp.department_name}
                        </td>
                        <td className="py-3 px-3 text-center font-mono font-bold">
                          {emp.average_competency !== null ? (
                            <span className={emp.average_competency >= 70 ? 'text-emerald-300' : 'text-rose-400'}>
                              {emp.average_competency.toFixed(1)}
                            </span>
                          ) : (
                            <span className="text-slate-500">Unassessed</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center font-mono">
                          {emp.role_readiness !== null ? (
                            <span className="font-bold text-cyan-300">{emp.role_readiness.toFixed(1)}%</span>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {emp.needs_attention ? (
                            <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-mono font-bold">
                              Attention
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px] font-mono">
                              On Track
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => setSelectedEmployeeId(emp.id)}
                            className="px-2.5 py-1 rounded bg-violet-600/30 hover:bg-violet-600/50 text-violet-200 border border-violet-500/30 font-semibold text-[11px] transition-colors"
                          >
                            Drill Down →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs">No matching personnel found.</div>
            )}
          </GlassCard>
        )}

        {/* DRILL-DOWN MODAL / SLIDE-OVER DRAWER */}
        {selectedEmployeeId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
            <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl bg-[#0B101E] border border-white/10 p-6 shadow-2xl space-y-6">
              {/* Modal Header */}
              <div className="flex items-center justify-between pb-4 border-b border-white/10">
                <div>
                  <div className="text-xs font-mono text-cyan-400 uppercase">
                    Stage 13 Authoritative Performance Profile
                  </div>
                  <h3 className="text-lg font-bold text-white">
                    {drilldownPerf?.employee_name || 'Loading Officer Profile...'}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {drilldownPerf?.department_name} • {drilldownPerf?.job_role_name}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedEmployeeId(null)}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {drilldownLoading ? (
                <div className="py-16 text-center text-slate-400 text-xs">
                  Loading employee performance metrics...
                </div>
              ) : drilldownPerf ? (
                <div className="space-y-6">
                  {/* Summary KPI Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div className="p-3 rounded-xl bg-white/5">
                      <div className="text-xs text-slate-400">Baseline Score</div>
                      <div className="text-lg font-bold text-slate-200 font-mono">
                        {drilldownPerf.overall.baseline_score?.toFixed(1) ?? '—'}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                      <div className="text-xs text-cyan-300">Current Score</div>
                      <div className="text-lg font-bold text-cyan-400 font-mono">
                        {drilldownPerf.overall.current_score?.toFixed(1) ?? '—'}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                      <div className="text-xs text-emerald-300">Role Readiness</div>
                      <div className="text-lg font-bold text-emerald-400 font-mono">
                        {drilldownPerf.overall.target_readiness_percentage !== null &&
                        drilldownPerf.overall.target_readiness_percentage !== undefined
                          ? `${drilldownPerf.overall.target_readiness_percentage.toFixed(1)}%`
                          : '—'}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl bg-violet-500/10 border border-violet-500/20">
                      <div className="text-xs text-violet-300">Growth Points</div>
                      <div className="text-lg font-bold text-violet-400 font-mono">
                        +{drilldownPerf.overall.improvement_points?.toFixed(1) ?? '0.0'}
                      </div>
                    </div>
                  </div>

                  {/* Strongest vs Focus Areas */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Strengths */}
                    <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                      <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider mb-3">
                        Top Demonstrated Strengths
                      </h4>
                      <div className="space-y-2">
                        {drilldownPerf.strongest_competencies.map((s) => (
                          <div key={s.competency_id} className="p-2 rounded-lg bg-white/5 flex items-center justify-between text-xs">
                            <span className="text-white font-medium">{s.competency_name}</span>
                            <span className="font-mono font-bold text-emerald-400">{s.current_score.toFixed(1)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Focus Areas */}
                    <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/20">
                      <h4 className="text-xs font-bold text-rose-300 uppercase tracking-wider mb-3">
                        Priority Focus Deficits
                      </h4>
                      <div className="space-y-2">
                        {drilldownPerf.focus_competencies.map((f) => (
                          <div key={f.competency_id} className="p-2 rounded-lg bg-white/5 flex items-center justify-between text-xs">
                            <span className="text-white font-medium">{f.competency_name}</span>
                            <span className="font-mono text-rose-400 font-bold">Gap: -{f.gap_score.toFixed(1)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Recent Activity Timeline */}
                  {drilldownTimeline?.events && drilldownTimeline.events.length > 0 && (
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                        Recent Learning & Assessment Activity
                      </h4>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {drilldownTimeline.events.slice(0, 5).map((ev) => (
                          <div key={ev.id} className="p-2.5 rounded-lg bg-black/30 flex items-center justify-between text-xs">
                            <div className="space-y-0.5">
                              <div className="font-semibold text-white">{ev.title}</div>
                              <div className="text-[10px] text-slate-400">{ev.description}</div>
                            </div>
                            <div className="text-right font-mono text-[10px] text-slate-400">
                              {new Date(ev.timestamp).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}

              {/* Modal Footer */}
              <div className="pt-4 border-t border-white/10 flex justify-end">
                <button
                  onClick={() => setSelectedEmployeeId(null)}
                  className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold transition-colors"
                >
                  Close Profile
                </button>
              </div>
            </div>
          </div>
        )}
      </PageContainer>
    </AppShell>
  );
}
