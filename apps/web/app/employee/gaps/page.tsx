'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  AlertTriangle,
  ShieldAlert,
  CheckCircle,
  RefreshCw,
  Search,
  ArrowRight,
  TrendingDown,
  Layers,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useCompetencyDomains } from '@/hooks/use-competency';
import {
  useEmployeeSkillGaps,
  useSkillGapSummary,
  useRecalculateSkillGaps,
} from '@/hooks/use-skill-gaps';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { CurrentVsRequiredBar } from '@/components/gaps/current-vs-required-bar';
import { GapDetailDrawer } from '@/components/gaps/gap-detail-drawer';
import type { SkillGap } from '@pragya/types';

export default function EmployeeSkillGapsPage() {
  const { data: employee, isLoading: employeeLoading } = useCurrentEmployee();
  const { data: domains = [] } = useCompetencyDomains();

  const [selectedPriority, setSelectedPriority] = useState<string>('ALL');
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeDrawerGap, setActiveDrawerGap] = useState<SkillGap | null>(null);

  const {
    data: gaps = [],
    isLoading: gapsLoading,
    isRefetching: gapsRefetching,
  } = useEmployeeSkillGaps(employee?.id);

  const {
    data: summary,
    isLoading: summaryLoading,
  } = useSkillGapSummary(employee?.id);

  const recalculateMutation = useRecalculateSkillGaps(employee?.id);

  const handleRecalculate = () => {
    recalculateMutation.mutate();
  };

  // Filtered gaps for table display
  const filteredGaps = useMemo(() => {
    return gaps.filter((gap) => {
      // Priority filter
      if (selectedPriority !== 'ALL' && gap.priority_level !== selectedPriority) {
        return false;
      }
      // Domain filter
      if (selectedDomain !== 'ALL' && gap.domain_code !== selectedDomain) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName = gap.competency_name.toLowerCase().includes(q);
        const matchCode = gap.competency_code.toLowerCase().includes(q);
        const matchDomain = gap.domain_name.toLowerCase().includes(q);
        if (!matchName && !matchCode && !matchDomain) return false;
      }
      return true;
    });
  }, [gaps, selectedPriority, selectedDomain, searchQuery]);

  // Top priority gap (highest priority gap with positive gap score)
  const topPriorityGap = useMemo(() => {
    if (summary?.highest_priority_gap && summary.highest_priority_gap.gap_score > 0) {
      return summary.highest_priority_gap;
    }
    const positiveGaps = gaps.filter((g) => g.gap_score > 0);
    if (positiveGaps.length === 0) return null;
    return [...positiveGaps].sort((a, b) => b.priority_score - a.priority_score)[0];
  }, [summary, gaps]);

  const isLoading = employeeLoading || gapsLoading || summaryLoading;

  return (
    <AppShell role="EMPLOYEE" pageTitle="My Skill Gaps">
      <PageContainer>
        {/* Page Header with Recalculate Action */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <PageHeader
            title="My Skill Gaps"
            subtitle="Understand which competencies need attention for your current role."
            breadcrumbs={[
              { label: 'Learner Workspace', href: '/employee' },
              { label: 'Skill Gaps' },
            ]}
          />
          <button
            onClick={handleRecalculate}
            disabled={recalculateMutation.isPending || gapsRefetching}
            className="self-start md:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs transition disabled:opacity-50 shadow-sm"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${
                recalculateMutation.isPending || gapsRefetching ? 'animate-spin' : ''
              }`}
            />
            {recalculateMutation.isPending ? 'Recalculating...' : 'Recalculate Gaps'}
          </button>
        </div>

        {/* Top Summary Metrics Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Role Competencies */}
          <div className="bg-slate-900/60 border border-slate-800/90 rounded-2xl p-4 sm:p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <span>Role Competencies</span>
              <Layers className="w-4 h-4 text-slate-400" />
            </div>
            <div className="text-3xl font-extrabold text-slate-100 font-mono">
              {summary?.total_competencies ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Required for {employee?.job_role_name || 'Current Role'}
            </p>
          </div>

          {/* Active Skill Gaps */}
          <div className="bg-slate-900/60 border border-slate-800/90 rounded-2xl p-4 sm:p-5 relative overflow-hidden">
            <div className="flex items-center justify-between text-amber-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <span>Active Gaps</span>
              <TrendingDown className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-extrabold text-amber-300 font-mono">
              {summary?.gaps_count ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              {summary?.no_gap_count ?? 0} requirements fully met
            </p>
          </div>

          {/* Critical Priority Gaps */}
          <div className="bg-slate-900/60 border border-rose-900/40 rounded-2xl p-4 sm:p-5 relative overflow-hidden bg-gradient-to-br from-rose-950/20 to-transparent">
            <div className="flex items-center justify-between text-rose-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <span>Critical Gaps</span>
              <ShieldAlert className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-3xl font-extrabold text-rose-300 font-mono">
              {summary?.critical_count ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              High deficit in critical role functions
            </p>
          </div>

          {/* High Priority Gaps */}
          <div className="bg-slate-900/60 border border-amber-900/40 rounded-2xl p-4 sm:p-5 relative overflow-hidden bg-gradient-to-br from-amber-950/20 to-transparent">
            <div className="flex items-center justify-between text-amber-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <span>High Priority Gaps</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-extrabold text-amber-300 font-mono">
              {summary?.high_count ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Moderate deficit in key tasks
            </p>
          </div>
        </div>

        {/* Priority Distribution Overview Bar */}
        {summary && summary.total_competencies > 0 && (
          <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 sm:p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Priority Distribution Overview
              </span>
              <span className="text-xs text-slate-500">
                Avg. Gap Deficit: <span className="text-cyan-300 font-mono font-bold">{summary.average_gap} pts</span>
              </span>
            </div>

            {/* Segmented Distribution Bar */}
            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
              {summary.critical_count > 0 && (
                <div
                  className="bg-rose-500 transition-all hover:opacity-90"
                  style={{ width: `${(summary.critical_count / summary.total_competencies) * 100}%` }}
                  title={`Critical: ${summary.critical_count}`}
                />
              )}
              {summary.high_count > 0 && (
                <div
                  className="bg-amber-500 transition-all hover:opacity-90"
                  style={{ width: `${(summary.high_count / summary.total_competencies) * 100}%` }}
                  title={`High: ${summary.high_count}`}
                />
              )}
              {summary.medium_count > 0 && (
                <div
                  className="bg-sky-500 transition-all hover:opacity-90"
                  style={{ width: `${(summary.medium_count / summary.total_competencies) * 100}%` }}
                  title={`Medium: ${summary.medium_count}`}
                />
              )}
              {summary.low_count > 0 && (
                <div
                  className="bg-slate-500 transition-all hover:opacity-90"
                  style={{ width: `${(summary.low_count / summary.total_competencies) * 100}%` }}
                  title={`Low: ${summary.low_count}`}
                />
              )}
              {summary.no_gap_count > 0 && (
                <div
                  className="bg-emerald-500 transition-all hover:opacity-90"
                  style={{ width: `${(summary.no_gap_count / summary.total_competencies) * 100}%` }}
                  title={`No Gap: ${summary.no_gap_count}`}
                />
              )}
            </div>

            {/* Interactive Filter Pills */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              <button
                onClick={() => setSelectedPriority('ALL')}
                className={`px-3 py-1 rounded-full border transition ${
                  selectedPriority === 'ALL'
                    ? 'bg-slate-700 text-white border-slate-600 font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                All ({summary.total_competencies})
              </button>
              <button
                onClick={() => setSelectedPriority('CRITICAL')}
                className={`px-3 py-1 rounded-full border transition flex items-center gap-1.5 ${
                  selectedPriority === 'CRITICAL'
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                Critical ({summary.critical_count})
              </button>
              <button
                onClick={() => setSelectedPriority('HIGH')}
                className={`px-3 py-1 rounded-full border transition flex items-center gap-1.5 ${
                  selectedPriority === 'HIGH'
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                High ({summary.high_count})
              </button>
              <button
                onClick={() => setSelectedPriority('MEDIUM')}
                className={`px-3 py-1 rounded-full border transition flex items-center gap-1.5 ${
                  selectedPriority === 'MEDIUM'
                    ? 'bg-sky-500/20 text-sky-300 border-sky-500/50 font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-sky-500" />
                Medium ({summary.medium_count})
              </button>
              <button
                onClick={() => setSelectedPriority('LOW')}
                className={`px-3 py-1 rounded-full border transition flex items-center gap-1.5 ${
                  selectedPriority === 'LOW'
                    ? 'bg-slate-500/20 text-slate-300 border-slate-500/50 font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                Low ({summary.low_count})
              </button>
              <button
                onClick={() => setSelectedPriority('NO_GAP')}
                className={`px-3 py-1 rounded-full border transition flex items-center gap-1.5 ${
                  selectedPriority === 'NO_GAP'
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 font-semibold'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                No Gap ({summary.no_gap_count})
              </button>
            </div>
          </div>
        )}

        {/* Top Priority Gap Card ("NEXT SKILL TO IMPROVE") */}
        {topPriorityGap && (
          <div className="relative rounded-2xl bg-gradient-to-r from-rose-950/40 via-amber-950/20 to-slate-900/80 border border-amber-500/40 p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  Next Skill to Improve
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Priority Score: {topPriorityGap.priority_score.toFixed(1)}/100
                </span>
              </div>
              <GapPriorityBadge priority={topPriorityGap.priority_level} size="lg" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
              <div className="lg:col-span-6 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-400">
                    {topPriorityGap.domain_name}
                  </span>
                  <span className="text-slate-600">•</span>
                  <span className="text-xs font-mono text-slate-500">
                    {topPriorityGap.competency_code}
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-slate-100">
                  {topPriorityGap.competency_name}
                </h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                  {topPriorityGap.explanation}
                </p>
              </div>

              <div className="lg:col-span-6 space-y-4">
                <CurrentVsRequiredBar
                  currentScore={topPriorityGap.current_score}
                  requiredScore={topPriorityGap.required_score}
                  currentLevelName={topPriorityGap.current_level_name}
                  requiredLevelName={topPriorityGap.required_level_name}
                  gapScore={topPriorityGap.gap_score}
                />

                <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                  <Link
                    href="/employee/learning"
                    className="inline-flex items-center gap-1.5 text-xs text-amber-400 hover:text-amber-300 font-medium transition"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Recommended learning available in personalized pathway →</span>
                  </Link>
                  <button
                    onClick={() => setActiveDrawerGap(topPriorityGap)}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition shadow-md shadow-amber-950/40"
                  >
                    View Gap Details
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search competencies or domains..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Domain Dropdown */}
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <span className="text-xs text-slate-400 whitespace-nowrap">Domain:</span>
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="w-full sm:w-auto px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All Domains</option>
              {domains.map((d) => (
                <option key={d.id} value={d.code}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Gap Table */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4 font-semibold">Competency</th>
                  <th className="py-3.5 px-4 font-semibold">Domain</th>
                  <th className="py-3.5 px-4 font-semibold min-w-[220px]">Current vs Required</th>
                  <th className="py-3.5 px-4 font-semibold text-center">Gap</th>
                  <th className="py-3.5 px-4 font-semibold text-center">Priority</th>
                  <th className="py-3.5 px-4 font-semibold text-center">Confidence</th>
                  <th className="py-3.5 px-4 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-500">
                      Loading skill gaps...
                    </td>
                  </tr>
                ) : filteredGaps.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-500">
                      No competencies match the selected filters.
                    </td>
                  </tr>
                ) : (
                  filteredGaps.map((gap) => {
                    const isNoGap = gap.gap_score <= 0;
                    const isLowConfidence = gap.confidence_flag === 'LOW_CONFIDENCE';

                    return (
                      <tr
                        key={gap.id}
                        className="hover:bg-slate-800/40 transition group"
                      >
                        {/* Competency Name & Code */}
                        <td className="py-4 px-4">
                          <div className="font-semibold text-slate-200 group-hover:text-cyan-300 transition">
                            {gap.competency_name}
                          </div>
                          <div className="text-[11px] font-mono text-slate-500">
                            {gap.competency_code}
                          </div>
                        </td>

                        {/* Domain */}
                        <td className="py-4 px-4 text-slate-400">
                          {gap.domain_name}
                        </td>

                        {/* Dual Score Visual Bar */}
                        <td className="py-4 px-4">
                          <CurrentVsRequiredBar
                            currentScore={gap.current_score}
                            requiredScore={gap.required_score}
                            currentLevelName={gap.current_level_name}
                            requiredLevelName={gap.required_level_name}
                            gapScore={gap.gap_score}
                            compact={true}
                          />
                        </td>

                        {/* Gap Delta Score */}
                        <td className="py-4 px-4 text-center">
                          {isNoGap ? (
                            <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                              <CheckCircle className="w-3.5 h-3.5" />
                              0
                            </span>
                          ) : (
                            <span className="font-mono font-bold text-amber-400 text-sm">
                              {gap.gap_score}
                            </span>
                          )}
                        </td>

                        {/* Priority Badge */}
                        <td className="py-4 px-4 text-center">
                          <GapPriorityBadge priority={gap.priority_level} size="sm" />
                        </td>

                        {/* Confidence Indicator */}
                        <td className="py-4 px-4 text-center">
                          {isLowConfidence ? (
                            <span
                              className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-amber-950/50 text-amber-300 border border-amber-800/40"
                              title="More evidence is recommended before making a strong training decision"
                            >
                              <AlertTriangle className="w-3 h-3 text-amber-400" />
                              Low
                            </span>
                          ) : (
                            <span className="text-slate-400 font-mono text-xs">
                              {(gap.confidence * 100).toFixed(0)}%
                            </span>
                          )}
                        </td>

                        {/* Action Button */}
                        <td className="py-4 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              href={`/employee/adaptive-assessment?competencyId=${gap.competency_id}`}
                              className="px-2.5 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 hover:border-indigo-500/50 font-medium text-xs transition inline-flex items-center gap-1"
                              title="Reassess this skill with adaptive testing"
                            >
                              <Sparkles className="w-3 h-3 text-indigo-400" />
                              <span>Reassess this skill</span>
                            </Link>
                            <button
                              onClick={() => setActiveDrawerGap(gap)}
                              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 hover:text-cyan-300 hover:border-cyan-700/50 text-slate-300 border border-slate-700 font-medium text-xs transition"
                            >
                              View Details
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Gap Detail Drawer */}
        <GapDetailDrawer
          gap={activeDrawerGap}
          onClose={() => setActiveDrawerGap(null)}
        />
      </PageContainer>
    </AppShell>
  );
}
