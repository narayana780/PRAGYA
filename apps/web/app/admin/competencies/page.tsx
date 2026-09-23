'use client';

import React, { useState } from 'react';
import {
  Award,
  BookOpen,
  Search,
  Layers,
  ShieldCheck,
  Building2,
  Filter,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import {
  useCompetencies,
  useCompetencyDomains,
  useProficiencyLevels,
  useRoleCompetencies,
} from '@/hooks/use-competency';
import { useJobRoles } from '@/hooks/use-organization';
import { CompetencyDetailDrawer } from '@/components/competencies/competency-detail-drawer';

export default function AdminCompetenciesPage() {
  const { data: domains = [] } = useCompetencyDomains();
  const { data: levels = [] } = useProficiencyLevels();
  const { data: jobRoles = [] } = useJobRoles();

  const [activeTab, setActiveTab] = useState<'dictionary' | 'levels' | 'roles'>('dictionary');
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [inspectCompetencyId, setInspectCompetencyId] = useState<string | null>(null);

  const effectiveRoleId = selectedRoleId || (jobRoles.length > 0 ? jobRoles[0].id : '');

  const { data: competenciesData } = useCompetencies({
    domain: selectedDomain || undefined,
    search: searchQuery || undefined,
    pageSize: 100,
  });

  const { data: roleRequirements = [] } = useRoleCompetencies(
    effectiveRoleId || undefined
  );

  return (
    <AppShell role="ADMIN" pageTitle="Competency Framework">
      <PageContainer>
        <PageHeader
          title="MoSPI Competency Framework Governance"
          subtitle="Official cadre capability dictionary, proficiency taxonomy, and role mapping standards (SIH26101 Standard)."
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Competencies' },
          ]}
        />

        <div className="space-y-6">
          {/* STATS OVERVIEW */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-[#0F172A] border border-cyan-500/20 shadow-md">
              <span className="text-xs text-slate-400 font-mono">Taxonomy Domains</span>
              <div className="text-2xl font-bold text-cyan-300 mt-1">
                {domains.length || 4}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Statistical, Technical, Digital, Behavioural
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-[#0F172A] border border-violet-500/20 shadow-md">
              <span className="text-xs text-slate-400 font-mono">Total Competencies</span>
              <div className="text-2xl font-bold text-violet-300 mt-1">
                {competenciesData?.total || 33}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                SIH26101 Canonical Dictionary Entities
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-[#0F172A] border border-emerald-500/20 shadow-md">
              <span className="text-xs text-slate-400 font-mono">Proficiency Hierarchy</span>
              <div className="text-2xl font-bold text-emerald-300 mt-1">
                {levels.length || 5} Levels
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Normalized 0–100 Scale Mapping
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-[#0F172A] border border-amber-500/20 shadow-md">
              <span className="text-xs text-slate-400 font-mono">Active Cadre Roles</span>
              <div className="text-2xl font-bold text-amber-300 mt-1">
                {jobRoles.length || 5} Roles
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Operational Profiles Configured
              </p>
            </div>
          </div>

          {/* TAB NAVIGATION */}
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            <button
              onClick={() => setActiveTab('dictionary')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'dictionary'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Competency Dictionary (33)
            </button>
            <button
              onClick={() => setActiveTab('levels')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'levels'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Proficiency Scale (1–5)
            </button>
            <button
              onClick={() => setActiveTab('roles')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeTab === 'roles'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Role Requirement Profiles
            </button>
          </div>

          {/* TAB 1: COMPETENCY DICTIONARY */}
          {activeTab === 'dictionary' && (
            <div className="space-y-4">
              {/* Search & Domain Filter */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="relative flex-1 max-w-md w-full">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search dictionary..."
                    className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  />
                </div>

                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <select
                    value={selectedDomain}
                    onChange={(e) => setSelectedDomain(e.target.value)}
                    className="px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none"
                  >
                    <option value="">All Domains (4)</option>
                    {domains.map((d) => (
                      <option key={d.id} value={d.code}>
                        {d.name} ({d.competency_count})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto rounded-2xl bg-[#0F172A] border border-slate-800 shadow-md">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono">
                      <th className="py-3 px-4">Code</th>
                      <th className="py-3 px-4">Competency Name</th>
                      <th className="py-3 px-4">Domain</th>
                      <th className="py-3 px-4">Definition Summary</th>
                      <th className="py-3 px-4">Source</th>
                      <th className="py-3 px-4">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {competenciesData?.items.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-900/40 transition">
                        <td className="py-3 px-4 font-mono font-semibold text-cyan-300">
                          {c.code}
                        </td>
                        <td className="py-3 px-4 font-bold text-slate-100">{c.name}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              c.domain_code === 'STATISTICAL'
                                ? 'bg-cyan-500/15 text-cyan-300'
                                : c.domain_code === 'TECHNICAL'
                                ? 'bg-violet-500/15 text-violet-300'
                                : c.domain_code === 'DIGITAL_GOVERNANCE'
                                ? 'bg-emerald-500/15 text-emerald-300'
                                : 'bg-amber-500/15 text-amber-300'
                            }`}
                          >
                            {c.domain_name}
                          </span>
                        </td>
                        <td className="py-3 px-4 max-w-md text-slate-400 truncate">
                          {c.short_description}
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-400">
                          {c.source_reference}
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => setInspectCompetencyId(c.id)}
                            className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: PROFICIENCY LEVEL SCALE */}
          {activeTab === 'levels' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>
                  The 5-Level Proficiency Scale provides a canonical qualitative descriptor paired with numerical 0–100 ranges for algorithmic analysis.
                </span>
              </div>

              <div className="overflow-x-auto rounded-2xl bg-[#0F172A] border border-slate-800">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono">
                      <th className="py-3 px-4">Level</th>
                      <th className="py-3 px-4">Level Name</th>
                      <th className="py-3 px-4">Score Range</th>
                      <th className="py-3 px-4">Behavioral & Operational Meaning</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {levels.map((lvl) => (
                      <tr key={lvl.id} className="hover:bg-slate-900/40 transition">
                        <td className="py-3.5 px-4 font-mono font-bold text-cyan-300">
                          Level {lvl.level_number}
                        </td>
                        <td className="py-3.5 px-4 font-semibold text-slate-100">
                          {lvl.name}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-emerald-400">
                          {lvl.minimum_score} – {lvl.maximum_score}
                        </td>
                        <td className="py-3.5 px-4 text-slate-300 leading-relaxed max-w-lg">
                          {lvl.description}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: ROLE REQUIREMENT PROFILES */}
          {activeTab === 'roles' && (
            <div className="space-y-4">
              {/* Role Picker */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                    Select Cadre Role:
                  </span>
                  <select
                    value={selectedRoleId}
                    onChange={(e) => setSelectedRoleId(e.target.value)}
                    className="px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-semibold text-cyan-300 focus:outline-none"
                  >
                    {jobRoles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name} ({role.career_level})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="text-xs text-slate-400 font-mono">
                  {roleRequirements.length} Competencies Required
                </div>
              </div>

              {/* Role Requirements List */}
              <div className="overflow-x-auto rounded-2xl bg-[#0F172A] border border-slate-800">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono">
                      <th className="py-3 px-4">Priority</th>
                      <th className="py-3 px-4">Competency</th>
                      <th className="py-3 px-4">Domain</th>
                      <th className="py-3 px-4">Required Level</th>
                      <th className="py-3 px-4">Criticality</th>
                      <th className="py-3 px-4">Task Relevance</th>
                      <th className="py-3 px-4">Prototype Rationale</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {roleRequirements.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-900/40 transition">
                        <td className="py-3 px-4 font-mono text-slate-400">#{r.priority}</td>
                        <td className="py-3 px-4">
                          <span className="font-bold text-slate-100">{r.competency_name}</span>
                          <span className="text-[10px] text-slate-500 block font-mono">
                            {r.competency_code}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-semibold text-cyan-300">
                          {r.domain_name}
                        </td>
                        <td className="py-3 px-4 font-mono font-semibold text-slate-100">
                          Level {r.required_level_number} ({r.required_level_name})
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              r.criticality === 'CRITICAL'
                                ? 'bg-rose-500/20 text-rose-300'
                                : r.criticality === 'HIGH'
                                ? 'bg-amber-500/20 text-amber-300'
                                : 'bg-cyan-500/20 text-cyan-300'
                            }`}
                          >
                            {r.criticality}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-400">
                          {r.task_relevance}
                        </td>
                        <td className="py-3 px-4 text-slate-400 leading-relaxed max-w-sm">
                          {r.rationale || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* DETAIL DRAWER */}
        <CompetencyDetailDrawer
          competencyId={inspectCompetencyId}
          onClose={() => setInspectCompetencyId(null)}
        />
      </PageContainer>
    </AppShell>
  );
}
