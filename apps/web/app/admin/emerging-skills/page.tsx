'use client';

import React, { useState, useMemo } from 'react';
import {
  Zap,
  Eye,
  ShieldCheck,
  BarChart3,
  Search,
  Filter,
  RefreshCw,
  AlertTriangle,
  Info,
  TrendingUp,
  Sparkles,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { useEmergingSkills } from '@/hooks/use-emerging-skills';

export default function AdminEmergingSkillsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [domainFilter, setDomainFilter] = useState('ALL');

  const { data, isLoading, error, refetch } = useEmergingSkills();

  // Extract unique domains for filter
  const domains = useMemo(() => {
    if (!data?.skills) return [];
    const unique = new Set(data.skills.map((s) => s.domain_name));
    return Array.from(unique).sort();
  }, [data]);

  // Filter skills
  const filteredSkills = useMemo(() => {
    if (!data?.skills) return [];
    return data.skills.filter((skill) => {
      const matchesSearch =
        skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        skill.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        skill.domain_name.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus =
        statusFilter === 'ALL' || skill.status === statusFilter;

      const matchesDomain =
        domainFilter === 'ALL' || skill.domain_name === domainFilter;

      return matchesSearch && matchesStatus && matchesDomain;
    });
  }, [data, searchTerm, statusFilter, domainFilter]);

  // Top emerging spotlight
  const topEmerging = useMemo(() => {
    if (!data?.skills) return [];
    return data.skills
      .filter((s) => s.status === 'EMERGING' || s.status === 'WATCH')
      .slice(0, 3);
  }, [data]);

  return (
    <AppShell role="ADMIN" pageTitle="Emerging Skills & Horizon Scanning">
      <PageContainer>
        {/* HEADER */}
        <PageHeader
          title="Emerging Statistical Skills & Horizon Scanning"
          subtitle="Empirical detection of rising statistical, analytical, and digital competencies across India's Official Statistical System."
          badge={
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30 font-mono">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Horizon Signals Radar</span>
            </div>
          }
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Emerging Skills' },
          ]}
        />

        {/* ERROR BANNER */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-rose-300 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Failed to load emerging skill signals.</span>
            </div>
            <button
              onClick={() => refetch()}
              className="px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-200 text-xs font-semibold flex items-center gap-1.5 hover:bg-rose-500/30 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* SECTION 1: SIGNAL KPI CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <GlassCard variant="elevated" className="p-5 border-amber-500/20 bg-amber-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>EMERGING SIGNALS</span>
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-amber-300 font-mono">
              {isLoading ? '...' : data?.emerging_count ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">High workforce deficit & demand acceleration</div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5 border-cyan-500/20 bg-cyan-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>WATCHLIST COMPETENCIES</span>
              <Eye className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-cyan-300 font-mono">
              {isLoading ? '...' : data?.watch_count ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Moderate demand velocity across cadres</div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5 border-emerald-500/20 bg-emerald-950/10">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>ESTABLISHED CORE</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-emerald-300 font-mono">
              {isLoading ? '...' : data?.established_count ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Institutionalized competencies with low gaps</div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5 border-slate-700 bg-slate-900/40">
            <div className="text-xs font-mono text-slate-400 mb-1 flex items-center justify-between">
              <span>TOTAL ANALYZED</span>
              <BarChart3 className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-white font-mono">
              {isLoading ? '...' : data?.total_analyzed ?? 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              {data?.insufficient_data_count ?? 0} competencies pending signal evidence
            </div>
          </GlassCard>
        </div>

        {/* METHODOLOGY EXPLAINER BANNER */}
        <div className="mb-8 p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-start gap-3 text-xs text-slate-300">
          <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-semibold text-white">Signal Methodology & Explainability Policy</div>
            <p>
              Emerging Skill Signals are computed using a deterministic weighted combination of internal workforce evidence: <span className="text-amber-300 font-semibold">30% Workforce Skill Gap Frequency</span>, <span className="text-cyan-300 font-semibold">25% Recommendation Generation Velocity</span>, <span className="text-emerald-300 font-semibold">25% Training Demand & Enrollments</span>, and <span className="text-violet-300 font-semibold">20% Cadre Job Role Coverage</span>. PRAGYA does not employ ungrounded black-box predictions; every score displays its concrete underlying operational signals.
            </p>
          </div>
        </div>

        {/* SECTION 2: TOP EMERGING SPOTLIGHT */}
        {topEmerging.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white tracking-tight">Top Horizon Signals Spotlight</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {topEmerging.map((skill) => (
                <GlassCard key={skill.competency_id} variant="elevated" className="p-5 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-400">
                          {skill.domain_name}
                        </span>
                        <h4 className="text-sm font-bold text-white mt-1.5">{skill.name}</h4>
                        <div className="text-[11px] font-mono text-slate-400">{skill.code}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold font-mono text-amber-300">
                          {skill.signal_score.toFixed(1)}
                        </div>
                        <span
                          className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-semibold ${
                            skill.status === 'EMERGING'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                          }`}
                        >
                          {skill.status}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2 py-2 border-y border-white/5 text-center text-[10px] font-mono mb-3">
                      <div>
                        <div className="text-slate-400">GAPS</div>
                        <div className="font-bold text-rose-400">{skill.gap_frequency}</div>
                      </div>
                      <div>
                        <div className="text-slate-400">DEMAND</div>
                        <div className="font-bold text-emerald-400">{skill.training_demand}</div>
                      </div>
                      <div>
                        <div className="text-slate-400">ROLES</div>
                        <div className="font-bold text-cyan-300">{skill.role_coverage}</div>
                      </div>
                    </div>
                  </div>

                  {/* WHY IS THIS EMERGING */}
                  <div className="space-y-1.5">
                    <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                      Why this signal is rising:
                    </div>
                    {skill.signals.slice(0, 2).map((sig, idx) => (
                      <div
                        key={idx}
                        className="text-[11px] text-slate-300 flex items-start gap-1.5 bg-slate-900/60 p-1.5 rounded"
                      >
                        <TrendingUp className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                        <span>{sig}</span>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 3: HORIZON SCANNING TABLE */}
        <GlassCard variant="elevated" className="p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Emerging Competencies Radar & Demand Matrix
              </h3>
              <p className="text-xs text-slate-400">
                Prioritized ranking across all active statistical competencies
              </p>
            </div>

            {/* SEARCH & FILTERS */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search competency or code..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-900/60 border border-slate-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 w-48 sm:w-56"
                />
              </div>

              {/* DOMAIN FILTER */}
              <div className="flex items-center gap-1 bg-slate-900/60 border border-slate-700 rounded-lg p-1 text-xs">
                <Filter className="w-3.5 h-3.5 text-slate-400 ml-1.5" />
                <select
                  value={domainFilter}
                  onChange={(e) => setDomainFilter(e.target.value)}
                  className="bg-transparent text-slate-200 text-xs py-0.5 px-2 focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-slate-900">All Domains</option>
                  {domains.map((dom) => (
                    <option key={dom} value={dom} className="bg-slate-900">
                      {dom}
                    </option>
                  ))}
                </select>
              </div>

              {/* STATUS FILTER */}
              <div className="flex items-center gap-1 bg-slate-900/60 border border-slate-700 rounded-lg p-1 text-xs">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="bg-transparent text-slate-200 text-xs py-0.5 px-2 focus:outline-none cursor-pointer"
                >
                  <option value="ALL" className="bg-slate-900">All Statuses</option>
                  <option value="EMERGING" className="bg-slate-900">Emerging</option>
                  <option value="WATCH" className="bg-slate-900">Watch</option>
                  <option value="ESTABLISHED" className="bg-slate-900">Established</option>
                  <option value="INSUFFICIENT_DATA" className="bg-slate-900">Insufficient Data</option>
                </select>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-slate-400 text-xs">Computing horizon signals...</div>
          ) : filteredSkills.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                    <th className="py-2.5 px-3">Competency</th>
                    <th className="py-2.5 px-3">Domain</th>
                    <th className="py-2.5 px-3 text-center">Signal Score</th>
                    <th className="py-2.5 px-3 text-center">Status</th>
                    <th className="py-2.5 px-3 text-center">Gaps</th>
                    <th className="py-2.5 px-3 text-center">Rec Velocity</th>
                    <th className="py-2.5 px-3 text-center">Demand</th>
                    <th className="py-2.5 px-3 text-center">Roles</th>
                    <th className="py-2.5 px-3">Explainability Signals</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredSkills.map((skill) => (
                    <tr key={skill.competency_id} className="hover:bg-white/5 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-semibold text-white">{skill.name}</div>
                        <div className="text-[10px] font-mono text-slate-400">{skill.code}</div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 font-mono text-[10px]">
                          {skill.domain_name}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-center font-mono">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div
                              className={`h-1.5 rounded-full ${
                                skill.signal_score >= 60.0
                                  ? 'bg-amber-400'
                                  : skill.signal_score >= 35.0
                                  ? 'bg-cyan-400'
                                  : 'bg-slate-600'
                              }`}
                              style={{ width: `${Math.min(skill.signal_score, 100)}%` }}
                            />
                          </div>
                          <span
                            className={`font-bold ${
                              skill.signal_score >= 60.0
                                ? 'text-amber-300'
                                : skill.signal_score >= 35.0
                                ? 'text-cyan-300'
                                : 'text-slate-400'
                            }`}
                          >
                            {skill.signal_score.toFixed(1)}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                            skill.status === 'EMERGING'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : skill.status === 'WATCH'
                              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                              : skill.status === 'ESTABLISHED'
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                              : 'bg-slate-700/40 text-slate-400 border border-slate-700'
                          }`}
                        >
                          {skill.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-medium text-rose-400">
                        {skill.gap_frequency}
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-medium text-cyan-300">
                        {skill.recommendation_frequency}
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-medium text-emerald-400">
                        {skill.training_demand}
                      </td>
                      <td className="py-3 px-3 text-center font-mono font-medium text-violet-300">
                        {skill.role_coverage}
                      </td>
                      <td className="py-3 px-3 max-w-sm">
                        <div className="flex flex-wrap gap-1">
                          {skill.signals.slice(0, 2).map((sig, i) => (
                            <span
                              key={i}
                              className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 truncate"
                            >
                              {sig}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-400 text-xs">
              No competency signals matching current filters.
            </div>
          )}
        </GlassCard>
      </PageContainer>
    </AppShell>
  );
}
