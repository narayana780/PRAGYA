'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Search,
  Target,
  ArrowRight,
  ShieldCheck,
  Info,
  UserCheck,
  History,
  Sparkles,
  BrainCircuit,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee } from '@/hooks/use-employee';
import {
  useCompetencies,
  useCompetencyDomains,
  useRoleCompetencies,
} from '@/hooks/use-competency';
import { useEmployeeCompetencies } from '@/hooks/use-assessment';
import { useEmployeeSkillGaps } from '@/hooks/use-skill-gaps';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { DomainVisualizer } from '@/components/competencies/domain-visualizer';
import { CompetencyDetailDrawer } from '@/components/competencies/competency-detail-drawer';
import { EvidenceDrawer } from '@/components/competencies/evidence-drawer';
import { ScoreHistoryDrawer } from '@/components/competencies/score-history-drawer';
import { SelfAssessmentModal } from '@/components/competencies/self-assessment-modal';
import type { RoleCompetencyRequirement, EmployeeCompetency } from '@pragya/types';

export default function EmployeeCompetencyPage() {
  const { data: employee } = useCurrentEmployee();
  const { data: domains = [] } = useCompetencyDomains();

  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRequiredOnly, setFilterRequiredOnly] = useState(false);
  const [filterAssessedOnly, setFilterAssessedOnly] = useState(false);

  // Drawer states
  const [selectedCompetencyId, setSelectedCompetencyId] = useState<string | null>(null);
  const [evidenceCompetency, setEvidenceCompetency] = useState<EmployeeCompetency | null>(null);
  const [historyCompetency, setHistoryCompetency] = useState<EmployeeCompetency | null>(null);
  const [selfAssessCompetency, setSelfAssessCompetency] = useState<EmployeeCompetency | null>(null);

  // Fetch all 33 competencies
  const { data: competenciesData, isLoading: competenciesLoading } = useCompetencies({
    domain: selectedDomain || undefined,
    search: searchQuery || undefined,
    pageSize: 50,
  });

  // Fetch requirements for employee's current role
  const { data: roleRequirements = [] } = useRoleCompetencies(
    employee?.job_role_id
  );

  // Fetch real Stage 5 demonstrated employee competencies
  const {
    data: employeeCompetencies = [],
    isLoading: employeeCompetenciesLoading,
    refetch: refetchEmployeeCompetencies,
  } = useEmployeeCompetencies(employee?.id);

  // Fetch Stage 6 calculated skill gaps
  const { data: skillGaps = [] } = useEmployeeSkillGaps(employee?.id);

  // Map role requirements by competency_id
  const requirementMap = useMemo(() => {
    const map = new Map<string, RoleCompetencyRequirement>();
    roleRequirements.forEach((r) => map.set(r.competency_id, r));
    return map;
  }, [roleRequirements]);

  // Map employee competencies by competency_id
  const employeeCompetencyMap = useMemo(() => {
    const map = new Map<string, EmployeeCompetency>();
    employeeCompetencies.forEach((c) => map.set(c.competency_id, c));
    return map;
  }, [employeeCompetencies]);

  // Map skill gaps by competency_id
  const skillGapMap = useMemo(() => {
    const map = new Map<string, (typeof skillGaps)[0]>();
    skillGaps.forEach((g) => map.set(g.competency_id, g));
    return map;
  }, [skillGaps]);

  // Filter competencies based on active toggles
  const displayedCompetencies = useMemo(() => {
    let list = competenciesData?.items || [];
    if (filterRequiredOnly) {
      list = list.filter((c) => requirementMap.has(c.id));
    }
    if (filterAssessedOnly) {
      list = list.filter((c) => employeeCompetencyMap.has(c.id));
    }
    return list;
  }, [competenciesData, filterRequiredOnly, filterAssessedOnly, requirementMap, employeeCompetencyMap]);

  const selectedRoleRequirement = selectedCompetencyId
    ? requirementMap.get(selectedCompetencyId) || null
    : null;

  return (
    <AppShell role="EMPLOYEE" pageTitle="Competency Framework">
      <PageContainer>
        <PageHeader
          title="Demonstrated Competencies & Evidence"
          subtitle="Empirical capability estimation derived from diagnostic testing, verified training, cadre experience, and self-assessment."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'Competencies & Evidence' },
          ]}
        />

        <div className="space-y-6">
          {/* TOP: ROLE & EVIDENCE SUMMARY HERO */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-[#0F172A] via-[#0B1220] to-[#070A13] border border-cyan-500/25 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-start md:items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
                <Target className="w-7 h-7" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider font-semibold">
                    Current Cadre Role
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    Stage 5 Engine Active
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-bold text-slate-100">
                  {employee?.designation || 'Statistical Officer'}
                </h2>
                <p className="text-xs text-slate-400">
                  {employee?.department_name || 'Department of Economics and Statistics'} • Cadre ID:{' '}
                  {employee?.employee_code || 'EMP-0001'}
                </p>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
              <div className="px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                <div className="text-lg font-bold text-cyan-300 font-mono">
                  {employeeCompetencies.length}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">
                  Assessed Competencies
                </div>
              </div>

              <div className="px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                <div className="text-lg font-bold text-violet-300 font-mono">
                  {roleRequirements.length}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">
                  Role Requirements
                </div>
              </div>

              <div className="px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                <div className="text-lg font-bold text-emerald-300 font-mono">
                  5 Sources
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wider">
                  Evidence Channels
                </div>
              </div>
            </div>
          </div>

          {/* 4-PILLAR DOMAIN VISUALIZER */}
          <DomainVisualizer
            domains={domains}
            selectedDomain={selectedDomain}
            onSelectDomain={setSelectedDomain}
          />

          {/* SEARCH & FILTER CONTROLS */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            {/* Search Input */}
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by competency name, code, or description..."
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            {/* Filter Toggle Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => setFilterRequiredOnly(!filterRequiredOnly)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition ${
                  filterRequiredOnly
                    ? 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                {filterRequiredOnly ? '✓ Required for Role' : 'Required for Role'}
              </button>

              <button
                onClick={() => setFilterAssessedOnly(!filterAssessedOnly)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition ${
                  filterAssessedOnly
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40'
                    : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
                }`}
              >
                {filterAssessedOnly ? '✓ Assessed Only' : 'Assessed Only'}
              </button>

              <span className="text-xs text-slate-400 font-mono px-2">
                Showing {displayedCompetencies.length} of 33
              </span>
            </div>
          </div>

          {/* COMPETENCY CARDS GRID */}
          {competenciesLoading || employeeCompetenciesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-pulse">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-52 rounded-2xl bg-slate-900/50 border border-slate-800" />
              ))}
            </div>
          ) : displayedCompetencies.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 space-y-3">
              <Info className="w-8 h-8 text-slate-500 mx-auto" />
              <p className="text-sm text-slate-300 font-medium">
                No competencies match your current filter criteria.
              </p>
              <button
                onClick={() => {
                  setSelectedDomain(null);
                  setSearchQuery('');
                  setFilterRequiredOnly(false);
                  setFilterAssessedOnly(false);
                }}
                className="text-xs text-cyan-400 hover:underline"
              >
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {displayedCompetencies.map((comp) => {
                const req = requirementMap.get(comp.id);
                const empComp = employeeCompetencyMap.get(comp.id);
                const isRequired = Boolean(req);

                return (
                  <div
                    key={comp.id}
                    className={`p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                      empComp
                        ? 'bg-gradient-to-br from-[#0F172A] to-[#0A111F] border-cyan-500/35 shadow-lg shadow-cyan-950/20'
                        : isRequired
                        ? 'bg-[#0F172A]/80 border-slate-800 hover:border-slate-700'
                        : 'bg-[#0A0E18]/70 border-slate-800/80'
                    }`}
                  >
                    <div>
                      {/* Card Header: Code & Domain Badge */}
                      <div className="flex items-center justify-between gap-2 mb-2.5">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-400">
                          {comp.code}
                        </span>
                        <span
                          className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded ${
                            comp.domain_code === 'STATISTICAL'
                              ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30'
                              : comp.domain_code === 'TECHNICAL'
                              ? 'bg-violet-500/10 text-violet-300 border border-violet-500/30'
                              : comp.domain_code === 'DIGITAL_GOVERNANCE'
                              ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                              : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                          }`}
                        >
                          {comp.domain_name}
                        </span>
                      </div>

                      {/* Title & Criticality */}
                      <h3 className="text-base font-bold text-slate-100 mb-1.5 tracking-tight flex items-center justify-between">
                        <span>{comp.name}</span>
                        {req && (
                          <span
                            className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                              req.criticality === 'CRITICAL'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : req.criticality === 'HIGH'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                            }`}
                          >
                            {req.criticality}
                          </span>
                        )}
                      </h3>

                      {/* Description */}
                      <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
                        {comp.short_description}
                      </p>
                    </div>

                    {/* DEMONSTRATED COMPETENCY CARD SECTION */}
                    <div className="pt-3 border-t border-slate-800/80 space-y-3">
                      {empComp ? (
                        <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2.5">
                          {/* Score and Level */}
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-[9px] font-mono uppercase text-slate-400 block">
                                Demonstrated Score
                              </span>
                              <div className="text-xl font-bold text-cyan-300 font-mono flex items-baseline gap-1">
                                {empComp.current_score.toFixed(1)}
                                <span className="text-[10px] text-slate-500">/ 100</span>
                              </div>
                            </div>

                            <div className="text-right">
                              <span className="text-[9px] font-mono uppercase text-slate-400 block">
                                Proficiency Level
                              </span>
                              <span className="text-xs font-bold text-slate-200">
                                Level {empComp.proficiency_level_number}
                              </span>
                              <div className="text-[10px] text-cyan-400">
                                {empComp.proficiency_level_name}
                              </div>
                            </div>
                          </div>

                          {/* Confidence & Evidence Count */}
                          <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-[10px]">
                            <div className="flex items-center gap-1.5">
                              <span className="text-slate-500">Confidence:</span>
                              <span
                                className={`font-semibold px-1.5 py-0.2 rounded border ${
                                  empComp.confidence_label === 'VERY_HIGH'
                                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                                    : empComp.confidence_label === 'HIGH'
                                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                                    : empComp.confidence_label === 'MEDIUM'
                                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                                    : 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                                }`}
                              >
                                {empComp.confidence_label}
                              </span>
                            </div>

                            <div className="text-slate-400 font-mono">
                              {empComp.evidence_count} evidence source
                              {empComp.evidence_count === 1 ? '' : 's'}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="p-3 rounded-xl bg-slate-950/40 border border-dashed border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
                          <span>Demonstrated Score:</span>
                          <span className="text-slate-500 italic">No empirical evidence</span>
                        </div>
                      )}

                      {/* Required for Role Comparison & Stage 6 Skill Gap & Priority */}
                      {req && (
                        <div className="space-y-1.5 pt-1 text-xs px-1 border-t border-slate-800/60">
                          <div className="flex items-center justify-between">
                            <span className="text-slate-400">Required for Role:</span>
                            <span className="font-semibold text-slate-200 font-mono">
                              Level {req.required_level_number} ({req.required_level_name})
                            </span>
                          </div>

                          {(() => {
                            const gap = skillGapMap.get(comp.id);
                            if (!gap) return null;
                            const isMet = gap.gap_score <= 0;
                            return (
                              <>
                                <div className="flex items-center justify-between pt-0.5">
                                  <span className="text-slate-400">Gap & Priority:</span>
                                  <div className="flex items-center gap-2">
                                    {isMet ? (
                                      <span className="text-emerald-400 font-semibold text-xs">
                                        ✓ Met
                                      </span>
                                    ) : (
                                      <span className="font-mono font-bold text-amber-400 text-xs">
                                        {gap.gap_score} pts
                                      </span>
                                    )}
                                    <GapPriorityBadge priority={gap.priority_level} size="sm" />
                                  </div>
                                </div>
                                {!isMet && (
                                  <div className="pt-1.5 flex justify-end">
                                    <Link
                                      href="/employee/learning"
                                      className="inline-flex items-center gap-1 text-[10px] text-amber-400 hover:text-amber-300 font-semibold transition-colors"
                                    >
                                      <Sparkles className="w-2.5 h-2.5" />
                                      <span>Recommended next step →</span>
                                    </Link>
                                  </div>
                                )}
                              </>
                            );
                          })()}
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex items-center gap-2 pt-1">
                        {empComp ? (
                          <>
                            <button
                              onClick={() => setEvidenceCompetency(empComp)}
                              className="flex-1 py-1.5 px-2 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition-colors"
                            >
                              <ShieldCheck className="w-3.5 h-3.5" />
                              <span>View Evidence</span>
                            </button>
                            <button
                              onClick={() => setHistoryCompetency(empComp)}
                              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
                              title="Score History"
                            >
                              <History className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => setSelfAssessCompetency(empComp)}
                              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-amber-400 transition-colors"
                              title="Self Assessment"
                            >
                              <UserCheck className="w-3.5 h-3.5" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => setSelectedCompetencyId(comp.id)}
                            className="w-full py-1.5 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition-colors"
                          >
                            <span>View Taxonomy Definition</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>

                      {/* Stage 11: Reassess Competency CTA */}
                      <div className="pt-2">
                        <Link
                          href={`/employee/adaptive-assessment?competencyId=${comp.id}`}
                          className="w-full py-1.5 px-3 rounded-lg bg-indigo-600/15 hover:bg-indigo-600/25 border border-indigo-500/30 text-indigo-300 text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Reassess Competency</span>
                        </Link>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* TAXONOMY DETAIL DRAWER */}
        <CompetencyDetailDrawer
          competencyId={selectedCompetencyId}
          onClose={() => setSelectedCompetencyId(null)}
          currentRoleRequirement={selectedRoleRequirement}
        />

        {/* EVIDENCE PORTFOLIO DRAWER */}
        <EvidenceDrawer
          employeeId={employee?.id}
          competency={evidenceCompetency}
          onClose={() => setEvidenceCompetency(null)}
        />

        {/* SCORE HISTORY DRAWER */}
        <ScoreHistoryDrawer
          employeeId={employee?.id}
          competency={historyCompetency}
          onClose={() => setHistoryCompetency(null)}
        />

        {/* SELF ASSESSMENT MODAL */}
        <SelfAssessmentModal
          employeeId={employee?.id}
          competency={selfAssessCompetency}
          onClose={() => setSelfAssessCompetency(null)}
          onSuccess={() => refetchEmployeeCompetencies()}
        />
      </PageContainer>
    </AppShell>
  );
}
