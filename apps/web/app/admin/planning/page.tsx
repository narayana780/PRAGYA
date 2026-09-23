'use client';

import React, { useState } from 'react';
import {
  Users,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Info,
  Search,
  Zap,
  Target,
  Building2,
  Briefcase,
  HelpCircle,
  Clock,
  Sparkles,
  Award,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import {
  useWorkforcePlanningOverview,
  useWorkforcePlanningTrends,
  useWorkforceCapacityForecast,
  useCompetencyCapacityForecast,
  useRoleCapacityForecast,
  useDepartmentCapacityForecast,
  usePlanningRecommendations,
} from '@/hooks/use-workforce-planning';

export default function AdminWorkforcePlanningPage() {
  const [activeTab, setActiveTab] = useState<'competencies' | 'roles' | 'departments'>('competencies');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const { data: overview, isLoading: overviewLoading } = useWorkforcePlanningOverview();
  const { data: trendsData, isLoading: trendsLoading } = useWorkforcePlanningTrends();
  const { data: forecast, isLoading: forecastLoading } = useWorkforceCapacityForecast();
  const { data: compForecast, isLoading: compLoading } = useCompetencyCapacityForecast();
  const { data: roleForecast, isLoading: roleLoading } = useRoleCapacityForecast();
  const { data: deptForecast, isLoading: deptLoading } = useDepartmentCapacityForecast();
  const { data: recsData, isLoading: recsLoading } = usePlanningRecommendations();

  // Filter competencies
  const filteredCompetencies = (compForecast?.competencies || []).filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.domain.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Filter roles
  const filteredRoles = (roleForecast?.roles || []).filter((r) => {
    const matchesSearch = r.role_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || r.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Filter departments
  const filteredDepartments = (deptForecast?.departments || []).filter((d) => {
    const matchesSearch = d.department_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || d.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <AppShell role="ADMIN" pageTitle="Workforce Planning & Capacity Forecasting">
      <PageContainer>
        {/* HEADER */}
        <PageHeader
          title="Predictive Workforce Planning & Capacity Forecasting"
          subtitle="Deterministic cadre capacity modeling synthesizing gap pressure, training demand, emerging skills, and role deficits for India's Official Statistical System."
          badge={
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span>Stage 17 Operational</span>
            </div>
          }
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Workforce Planning' },
          ]}
        />

        {/* METHODOLOGY & AUDIT CALLOUT */}
        <div className="mb-8 p-4 rounded-xl bg-slate-900/60 border border-cyan-500/30 flex items-start gap-3 text-xs text-slate-300 backdrop-blur-sm">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-semibold text-white flex items-center gap-2">
              <span>Deterministic Workforce Capacity Model</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Data Quality: {overview?.data_quality.quality_grade ?? 'HIGH'} ({overview?.data_quality.records_used ?? 0} records)
              </span>
            </div>
            <p>
              Projections are computed deterministically from internal PRAGYA database evidence (observed skill gaps, learning progress, role requirements, and Stage 16 horizon signals). In strict adherence to MoSPI data integrity guidelines, no unverified external market forecasts or synthetic scores are used.
            </p>
          </div>
        </div>

        {/* TOP LEVEL KPI METRICS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>WORKFORCE READINESS</span>
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-cyan-300 font-mono">
              {overviewLoading ? '...' : `${overview?.capacity.average_role_readiness.toFixed(1)}%`}
            </div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
              <span>Cadre target: 80.0%</span>
              <span className="text-emerald-400 font-medium">
                {overview?.capacity.employees_with_improvement ?? 0} improving
              </span>
            </div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>CURRENT QUALIFIED</span>
              <Users className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">
              {forecastLoading ? '...' : `${forecast?.current_capacity} / ${forecast?.total_workforce}`}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {forecast ? `${forecast.current_capacity_percentage}% officers qualified` : 'Assessing readiness...'}
            </div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>PROJECTED CAPACITY DEFICIT</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 font-mono">
              {forecastLoading ? '...' : `${forecast?.projected_gap} Officers`}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Current shortfall: {forecast?.capacity_gap ?? 0} officers
            </div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>PLANNING PRESSURE INDEX</span>
              <Zap className="w-4 h-4 text-violet-400" />
            </div>
            <div className="text-2xl font-bold text-violet-300 font-mono">
              {forecastLoading ? '...' : `${forecast?.overall_pressure_index} / 100`}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {overview?.capacity.employees_with_gaps ?? 0} officers with active gaps
            </div>
          </GlassCard>
        </div>

        {/* SECTION 2: HISTORICAL TREND & FORECAST PRIORITY TARGETS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* HISTORICAL WORKFORCE TRAJECTORY */}
          <div className="lg:col-span-2">
            <GlassCard variant="elevated" className="p-6 h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-white flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-cyan-400" />
                      Longitudinal Workforce Competency Trajectory
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Periodic competency averages and target achievement from authoritative evaluation snapshots.
                    </p>
                  </div>
                  <span className="px-2.5 py-1 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                    {trendsData?.status === 'OK' ? `${trendsData.periods_count} Snapshot Periods` : 'Status: Baseline Active'}
                  </span>
                </div>

                {trendsLoading ? (
                  <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
                    Loading historical trends...
                  </div>
                ) : trendsData && trendsData.trends.length > 0 ? (
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendsData.trends} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                        <XAxis dataKey="period" stroke="#64748B" fontSize={11} tickLine={false} />
                        <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#0F172A',
                            borderColor: '#334155',
                            borderRadius: '8px',
                            fontSize: '12px',
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="average_competency_score"
                          name="Avg Score"
                          stroke="#06B6D4"
                          strokeWidth={2.5}
                          dot={{ fill: '#06B6D4', r: 4 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="employees_meeting_target"
                          name="Meeting Target"
                          stroke="#10B981"
                          strokeWidth={2}
                          dot={{ fill: '#10B981', r: 3 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex flex-col items-center justify-center text-center p-6 border border-dashed border-slate-800 rounded-xl">
                    <Clock className="w-8 h-8 text-slate-600 mb-2" />
                    <div className="text-sm font-medium text-slate-300">Baseline Assessment State</div>
                    <p className="text-xs text-slate-500 max-w-sm mt-1">
                      Current evaluations establish the foundational baseline. Longitudinal trend curves will dynamically render as successive recalibrations accumulate over reporting cycles.
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                <span>Metric source: CompetencyRecalibration & Evidence snapshots</span>
                <span className="text-cyan-400 font-mono">Benchmark: 70.0 pts</span>
              </div>
            </GlassCard>
          </div>

          {/* PRIORITY PLANNING PRESSURES */}
          <div className="lg:col-span-1">
            <GlassCard variant="elevated" className="p-6 h-full flex flex-col justify-between">
              <div>
                <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-1">
                  <Target className="w-4 h-4 text-fuchsia-400" />
                  Priority Capacity Focus
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Highest projected deficits requiring immediate intervention.
                </p>

                <div className="space-y-4">
                  <div>
                    <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-cyan-400" />
                      Priority Competencies
                    </div>
                    <div className="space-y-1.5">
                      {forecast?.priority_competencies.length ? (
                        forecast.priority_competencies.map((name, i) => (
                          <div
                            key={i}
                            className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-950/50 border border-slate-800 text-xs"
                          >
                            <span className="text-slate-200 font-medium">{name}</span>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                              High Pressure
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="text-xs text-slate-500 italic">No acute competency deficits logged</div>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Briefcase className="w-3.5 h-3.5 text-violet-400" />
                      Priority Cadre Roles
                    </div>
                    <div className="space-y-1.5">
                      {forecast?.priority_roles.length ? (
                        forecast.priority_roles.map((name, i) => (
                          <div
                            key={i}
                            className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-950/50 border border-slate-800 text-xs"
                          >
                            <span className="text-slate-200 font-medium">{name}</span>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                              Cadre Need
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="text-xs text-slate-500 italic">Roles meeting readiness thresholds</div>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                      Priority Departments
                    </div>
                    <div className="space-y-1.5">
                      {forecast?.priority_departments.length ? (
                        forecast.priority_departments.map((name, i) => (
                          <div
                            key={i}
                            className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-950/50 border border-slate-800 text-xs"
                          >
                            <span className="text-slate-200 font-medium">{name}</span>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                              Focus
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="text-xs text-slate-500 italic">Balanced departmental distribution</div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500">
                Determined by: 35% Gaps + 25% Demand + 20% Emerging + 20% Deficit
              </div>
            </GlassCard>
          </div>
        </div>

        {/* SECTION 3: DETERMINISTIC PLANNING RECOMMENDATIONS */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                Actionable Workforce Planning Interventions
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Targeted capacity building directives synthesized from active gaps, enrollment patterns, and horizon signals.
              </p>
            </div>
            <span className="px-2.5 py-1 rounded text-xs font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
              {recsData?.total_recommendations ?? 0} Directives Active
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recsLoading ? (
              <div className="col-span-3 text-center py-10 text-slate-500 text-sm">
                Generating deterministic recommendations...
              </div>
            ) : recsData?.recommendations.length ? (
              recsData.recommendations.map((rec) => (
                <GlassCard key={rec.id} variant="elevated" className="p-5 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                          rec.priority === 'HIGH'
                            ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                            : rec.priority === 'MEDIUM'
                            ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                            : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                        }`}
                      >
                        {rec.priority} PRIORITY
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {rec.affected_population} Officers Affected
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-white mb-2 leading-snug">{rec.title}</h4>
                    <p className="text-xs text-slate-300 mb-3 leading-relaxed">{rec.rationale}</p>

                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 mb-3">
                      <div className="text-[10px] font-mono text-cyan-400 uppercase mb-1">Suggested Action</div>
                      <div className="text-xs text-slate-300">{rec.suggested_action}</div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-1">
                    {rec.evidence_signals.slice(0, 2).map((sig, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {sig}
                      </span>
                    ))}
                  </div>
                </GlassCard>
              ))
            ) : (
              <div className="col-span-3 text-center py-10 text-slate-500 text-sm">
                No acute capacity building recommendations required at this time.
              </div>
            )}
          </div>
        </div>

        {/* SECTION 4: DETAILED CAPACITY FORECAST RADAR */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
            {/* TABS */}
            <div className="flex items-center gap-2 p-1 rounded-lg bg-slate-900 border border-slate-800">
              <button
                onClick={() => setActiveTab('competencies')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  activeTab === 'competencies'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Competencies ({compForecast?.total_competencies ?? 0})
              </button>
              <button
                onClick={() => setActiveTab('roles')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  activeTab === 'roles'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Cadre Roles ({roleForecast?.total_roles ?? 0})
              </button>
              <button
                onClick={() => setActiveTab('departments')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  activeTab === 'departments'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Departments ({deptForecast?.total_departments ?? 0})
              </button>
            </div>

            {/* SEARCH & FILTERS */}
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-64">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder={`Filter ${activeTab}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none"
              >
                <option value="ALL">All Statuses</option>
                {activeTab === 'competencies' ? (
                  <>
                    <option value="HIGH_DEFICIT">High Deficit</option>
                    <option value="MODERATE_DEFICIT">Moderate Deficit</option>
                    <option value="BALANCED">Balanced</option>
                  </>
                ) : (
                  <>
                    <option value="HIGH_PRESSURE">High Pressure</option>
                    <option value="MODERATE_PRESSURE">Moderate Pressure</option>
                    <option value="ADEQUATE">Adequate / Balanced</option>
                  </>
                )}
              </select>
            </div>
          </div>

          {/* TAB 1: COMPETENCIES */}
          {activeTab === 'competencies' && (
            <GlassCard variant="elevated" className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-mono">
                      <th className="py-3 px-4">COMPETENCY</th>
                      <th className="py-3 px-3">DOMAIN</th>
                      <th className="py-3 px-3">COVERAGE</th>
                      <th className="py-3 px-3">GAP POPULATION</th>
                      <th className="py-3 px-3">LEARNING DEMAND</th>
                      <th className="py-3 px-3">HORIZON SCORE</th>
                      <th className="py-3 px-3">PLANNING PRESSURE</th>
                      <th className="py-3 px-4">STATUS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300 font-sans">
                    {compLoading ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          Loading competency capacity forecast...
                        </td>
                      </tr>
                    ) : filteredCompetencies.length ? (
                      filteredCompetencies.map((c) => (
                        <tr key={c.competency_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4 font-medium text-white">
                            <div>{c.name}</div>
                            <div className="text-[11px] text-slate-400 font-normal">
                              {c.rationale[0] || 'Baseline tracked'}
                            </div>
                          </td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                              {c.domain}
                            </span>
                          </td>
                          <td className="py-3 px-3 font-mono">
                            <div className="flex items-center gap-2">
                              <span>{c.current_coverage}%</span>
                              <div className="w-12 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                                <div
                                  className={`h-full ${
                                    c.current_coverage >= 70 ? 'bg-emerald-400' : 'bg-amber-400'
                                  }`}
                                  style={{ width: `${Math.min(100, c.current_coverage)}%` }}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-3 font-mono">{c.gap_population} Officers</td>
                          <td className="py-3 px-3 font-mono">{c.learning_demand} Enrolled</td>
                          <td className="py-3 px-3 font-mono text-cyan-400">{c.emerging_signal.toFixed(1)}</td>
                          <td className="py-3 px-3 font-mono font-semibold text-white">
                            {c.planning_pressure.toFixed(1)}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                                c.status === 'HIGH_DEFICIT'
                                  ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                                  : c.status === 'MODERATE_DEFICIT'
                                  ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                                  : c.status === 'INSUFFICIENT_DATA'
                                  ? 'bg-slate-800 text-slate-400 border border-slate-700'
                                  : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                              }`}
                            >
                              {c.status.replace('_', ' ')}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          No competencies matching filter criteria.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </GlassCard>
          )}

          {/* TAB 2: ROLES */}
          {activeTab === 'roles' && (
            <GlassCard variant="elevated" className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-mono">
                      <th className="py-3 px-4">ROLE / CADRE</th>
                      <th className="py-3 px-3">LEVEL</th>
                      <th className="py-3 px-3">OFFICERS</th>
                      <th className="py-3 px-3">MEETING TARGET</th>
                      <th className="py-3 px-3">BELOW TARGET</th>
                      <th className="py-3 px-3">READINESS SIGNAL</th>
                      <th className="py-3 px-3">CAPACITY PRESSURE</th>
                      <th className="py-3 px-4">STATUS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300 font-sans">
                    {roleLoading ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          Loading role capacity forecast...
                        </td>
                      </tr>
                    ) : filteredRoles.length ? (
                      filteredRoles.map((r) => (
                        <tr key={r.role_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4 font-medium text-white">
                            <div>{r.role_name}</div>
                            <div className="text-[11px] text-slate-400 font-normal">
                              {r.required_competencies_count} required competencies
                            </div>
                          </td>
                          <td className="py-3 px-3 font-mono text-slate-400">{r.cadre_level || 'General'}</td>
                          <td className="py-3 px-3 font-mono text-white">{r.employee_count}</td>
                          <td className="py-3 px-3 font-mono text-emerald-400">{r.employees_meeting_target}</td>
                          <td className="py-3 px-3 font-mono text-rose-400">{r.employees_below_target}</td>
                          <td className="py-3 px-3 font-mono text-cyan-400">{r.readiness_signal}%</td>
                          <td className="py-3 px-3 font-mono font-semibold text-white">
                            {r.projected_capacity_pressure.toFixed(1)}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                                r.status === 'HIGH_PRESSURE'
                                  ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                                  : r.status === 'MODERATE_PRESSURE'
                                  ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                                  : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                              }`}
                            >
                              {r.status.replace('_', ' ')}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          No cadre roles matching filter criteria.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </GlassCard>
          )}

          {/* TAB 3: DEPARTMENTS */}
          {activeTab === 'departments' && (
            <GlassCard variant="elevated" className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-900/80 text-slate-400 border-b border-slate-800 font-mono">
                      <th className="py-3 px-4">DEPARTMENT</th>
                      <th className="py-3 px-3">CODE</th>
                      <th className="py-3 px-3">WORKFORCE</th>
                      <th className="py-3 px-3">AVG PROFICIENCY</th>
                      <th className="py-3 px-3">ACTIVE GAPS</th>
                      <th className="py-3 px-3">LEARNING DEMAND</th>
                      <th className="py-3 px-3">PLANNING PRESSURE</th>
                      <th className="py-3 px-4">STATUS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300 font-sans">
                    {deptLoading ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          Loading department capacity forecast...
                        </td>
                      </tr>
                    ) : filteredDepartments.length ? (
                      filteredDepartments.map((d) => (
                        <tr key={d.department_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4 font-medium text-white">
                            <div>{d.department_name}</div>
                            <div className="text-[11px] text-slate-400 font-normal">
                              {d.rationale[0] || 'Department monitored'}
                            </div>
                          </td>
                          <td className="py-3 px-3 font-mono text-slate-400">{d.code || '—'}</td>
                          <td className="py-3 px-3 font-mono text-white">{d.workforce_size} Officers</td>
                          <td className="py-3 px-3 font-mono text-cyan-400">{d.competency_coverage.toFixed(1)}</td>
                          <td className="py-3 px-3 font-mono text-amber-400">{d.major_skill_gaps}</td>
                          <td className="py-3 px-3 font-mono">{d.learning_demand} Active</td>
                          <td className="py-3 px-3 font-mono font-semibold text-white">
                            {d.projected_capacity_pressure.toFixed(1)}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                                d.status === 'HIGH_PRESSURE'
                                  ? 'bg-rose-500/10 text-rose-300 border border-rose-500/30'
                                  : d.status === 'MODERATE_PRESSURE'
                                  ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                                  : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                              }`}
                            >
                              {d.status.replace('_', ' ')}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          No departments matching filter criteria.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </GlassCard>
          )}
        </div>

        {/* SECTION 5: METHODOLOGY & AUDIT SPECIFICATION */}
        <GlassCard variant="elevated" className="p-6">
          <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
            <HelpCircle className="w-4 h-4 text-cyan-400" />
            Statutory Cadre Planning Methodology & Mathematical Formula
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-300">
            <div>
              <div className="font-semibold text-cyan-300 mb-1">Composite Planning Pressure Index</div>
              <p className="mb-2 text-slate-400">
                To guarantee explainability and audit compliance across India&apos;s Official Statistical System, the planning pressure is formulated as a transparent weighted sum of active operational indicators:
              </p>
              <div className="p-3 rounded-lg bg-slate-950 font-mono text-[11px] text-cyan-300 border border-slate-800 mb-2">
                Pressure = 0.35 × GapPressure + 0.25 × TrainingDemand + 0.20 × EmergingSignal + 0.20 × Deficit
              </div>
              <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
                <li><strong className="text-slate-200">Gap Pressure:</strong> Density of assessed officers with active deficiency scores.</li>
                <li><strong className="text-slate-200">Training Demand:</strong> Velocity of module enrollments addressing the competency.</li>
                <li><strong className="text-slate-200">Emerging Signal:</strong> Multi-factor horizon score from Stage 16.</li>
                <li><strong className="text-slate-200">Deficit:</strong> Shortfall from designated ministry coverage target (80.0%).</li>
              </ul>
            </div>

            <div>
              <div className="font-semibold text-cyan-300 mb-1">Core Governance Assumptions & Limitations</div>
              <ul className="list-disc list-inside space-y-1.5 text-slate-400 text-[11px]">
                <li>
                  <strong className="text-slate-200">Internal Operational Data:</strong> Model inputs are strictly restricted to verifiable PRAGYA records in PostgreSQL.
                </li>
                <li>
                  <strong className="text-slate-200">Deterministic Governance:</strong> Calculations do not rely on stochastic external predictive algorithms that produce non-reproducible outcomes.
                </li>
                <li>
                  <strong className="text-slate-200">Statutory Cadre Advisory:</strong> Output figures serve as decision support signals for capacity-building directors and do not substitute statutory cadre recruitment boards.
                </li>
              </ul>
            </div>
          </div>
        </GlassCard>
      </PageContainer>
    </AppShell>
  );
}
