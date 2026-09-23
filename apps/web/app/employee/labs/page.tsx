'use client';

import React, { useState, useMemo, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  FlaskConical,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Database,
  Search,
  Loader2,
  Award,
} from 'lucide-react';
import { useLabScenarios, useStartLabSession } from '@/hooks/use-labs';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';

function VirtualLabsHubContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCompetencyId = searchParams.get('competencyId') || 'ALL';

  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedCompetency, setSelectedCompetency] = useState<string>(initialCompetencyId);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: scenarios = [], isLoading } = useLabScenarios();
  const startSessionMutation = useStartLabSession();

  const handleStartLab = (scenarioId: string) => {
    startSessionMutation.mutate(scenarioId, {
      onSuccess: (session) => {
        router.push(`/employee/labs/${scenarioId}/run?sessionId=${session.id}`);
      },
    });
  };

  const filteredScenarios = useMemo(() => {
    return scenarios.filter((sc) => {
      if (selectedDifficulty !== 'ALL' && sc.difficulty !== selectedDifficulty) return false;
      if (selectedType !== 'ALL' && sc.scenario_type !== selectedType) return false;
      if (selectedCompetency !== 'ALL' && sc.competency_id !== selectedCompetency) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = sc.title.toLowerCase().includes(q);
        const matchDesc = sc.description.toLowerCase().includes(q);
        const matchComp = (sc.competency_name || '').toLowerCase().includes(q);
        if (!matchTitle && !matchDesc && !matchComp) return false;
      }
      return true;
    });
  }, [scenarios, selectedDifficulty, selectedType, selectedCompetency, searchQuery]);

  return (
    <AppShell role="EMPLOYEE" pageTitle="Virtual Labs">
      <PageContainer>
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
          {/* Header Bar */}
          <div className="bg-gradient-to-br from-[#0A0E1A] via-slate-900 to-[#0A0E1A] border border-violet-500/25 p-6 sm:p-8 rounded-2xl shadow-xl space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-violet-600/20 border border-violet-500/30 text-violet-400 shrink-0">
                  <FlaskConical className="w-7 h-7" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
                    Statistical Virtual Labs
                    <span className="px-2.5 py-0.5 text-[10px] font-mono rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-300">
                      Simulation Sandbox
                    </span>
                  </h1>
                  <p className="text-sm text-slate-300 mt-1">
                    Practice statistical tasks safely using synthetic data and receive evidence-based feedback on your performance.
                  </p>
                </div>
              </div>

              {/* Synthetic Notice Badge */}
              <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs shrink-0 font-medium self-start md:self-auto">
                <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Synthetic Training Data — not official government data.</span>
              </div>
            </div>

            {/* WHAT IS A VIRTUAL LAB? Section */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800/90 space-y-4">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-violet-400 block mb-1">
                  What is a Virtual Lab?
                </span>
                <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
                  A Virtual Lab lets you practice realistic statistical work in a safe simulation. You inspect a synthetic dataset, perform controlled analytical tasks, receive feedback, and build competency evidence.
                </p>
              </div>

              {/* 5-Step Visual Flow */}
              <div className="pt-2 border-t border-slate-800/70">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
                  Simulation Workflow:
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-3">
                  {[
                    { step: '1', title: 'Choose Scenario', desc: 'Select domain task' },
                    { step: '2', title: 'Explore Data', desc: 'Inspect microdata' },
                    { step: '3', title: 'Perform Task', desc: 'Execute analysis' },
                    { step: '4', title: 'Receive Feedback', desc: 'Audited guidance' },
                    { step: '5', title: 'View Result', desc: 'Evidence & score' },
                  ].map((s) => (
                    <div
                      key={s.step}
                      className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 flex flex-col justify-between space-y-1 hover:border-violet-500/30 transition"
                    >
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-violet-600/20 text-violet-300 border border-violet-500/30 flex items-center justify-center font-mono text-[10px] font-bold shrink-0">
                          {s.step}
                        </span>
                        <span className="text-xs font-semibold text-slate-200">{s.title}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 pl-7">{s.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Filters Bar */}
          <div className="bg-[#0B0F19] border border-slate-800/80 p-4 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
              <div className="relative flex-1 md:w-64">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search labs or competencies..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
                />
              </div>

              {/* Difficulty Filter */}
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
              >
                <option value="ALL">All Difficulties</option>
                <option value="BEGINNER">Beginner</option>
                <option value="INTERMEDIATE">Intermediate</option>
                <option value="ADVANCED">Advanced</option>
              </select>

              {/* Scenario Type Filter */}
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
              >
                <option value="ALL">All Scenario Types</option>
                <option value="DATA_QUALITY_AUDIT">Data Quality Audit</option>
                <option value="SURVEY_SAMPLING">Survey Sampling</option>
                <option value="DESCRIPTIVE_STATISTICS">Descriptive Statistics</option>
                <option value="MISSING_DATA_ANALYSIS">Missing Data Analysis</option>
              </select>

              {/* Competency Filter */}
              <select
                value={selectedCompetency}
                onChange={(e) => setSelectedCompetency(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
              >
                <option value="ALL">All Competencies</option>
                {Array.from(new Map(scenarios.map((s) => [s.competency_id, s.competency_name])).entries()).map(
                  ([cId, cName]) => (
                    <option key={cId} value={cId}>
                      {cName || 'Competency'}
                    </option>
                  )
                )}
              </select>
            </div>

            <div className="text-xs text-slate-400 font-mono self-end md:self-auto">
              Showing {filteredScenarios.length} of {scenarios.length} Labs
            </div>
          </div>

          {/* Scenarios Grid */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center p-16 space-y-3">
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
              <p className="text-xs text-slate-400">Loading virtual lab scenarios...</p>
            </div>
          ) : filteredScenarios.length === 0 ? (
            <div className="text-center p-12 bg-slate-900/40 border border-slate-800 rounded-2xl">
              <FlaskConical className="w-10 h-10 text-slate-600 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-300">No matching lab scenarios found</p>
              <p className="text-xs text-slate-500 mt-1">Try changing or clearing your search filters.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredScenarios.map((sc) => {
                const isStarting = startSessionMutation.isPending && startSessionMutation.variables === sc.id;

                return (
                  <div
                    key={sc.id}
                    className="flex flex-col justify-between bg-gradient-to-br from-[#0B0F19] to-slate-900/90 border border-slate-800 hover:border-violet-500/40 rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-violet-950/20 group"
                  >
                    <div className="space-y-4">
                      {/* Scenario Badges Header */}
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-medium bg-violet-500/10 text-violet-300 border border-violet-500/25">
                          {sc.scenario_type.replace(/_/g, ' ')}
                        </span>
                        <div className="flex items-center gap-2">
                          {/* Synthetic Data badge */}
                          <span className="flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/25">
                            <ShieldCheck className="w-3 h-3 text-amber-400" />
                            Synthetic Data
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                              sc.difficulty === 'BEGINNER'
                                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                                : sc.difficulty === 'INTERMEDIATE'
                                ? 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30'
                                : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                            }`}
                          >
                            {sc.difficulty}
                          </span>
                          <span className="flex items-center gap-1 text-[11px] text-slate-400 font-mono">
                            <Clock className="w-3 h-3 text-slate-500" />
                            {sc.estimated_minutes} mins
                          </span>
                        </div>
                      </div>

                      {/* Title & Description */}
                      <div>
                        <h2 className="text-base font-bold text-white group-hover:text-violet-300 transition-colors">
                          {sc.title}
                        </h2>
                        <p className="text-xs text-slate-400 leading-relaxed mt-2 line-clamp-2">
                          {sc.description}
                        </p>
                      </div>

                      {/* What you will practice */}
                      <div className="space-y-1.5 p-3 rounded-xl bg-slate-900/50 border border-slate-800/80">
                        <span className="text-[10px] uppercase font-bold tracking-wider text-violet-400 block">
                          What you will practice
                        </span>
                        <ul className="space-y-1">
                          {sc.learning_objectives.slice(0, 2).map((obj, idx) => (
                            <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                              <CheckCircle2 className="w-3.5 h-3.5 text-violet-400 shrink-0 mt-0.5" />
                              <span className="line-clamp-1">{obj}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Competency & Dataset Info */}
                      <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800/80 space-y-2 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 flex items-center gap-1.5">
                            <Award className="w-3.5 h-3.5 text-violet-400" />
                            Competency
                          </span>
                          <span className="font-semibold text-slate-200">
                            {sc.competency_name || 'Statistical Methodology'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                          <span className="text-slate-400 flex items-center gap-1.5">
                            <Database className="w-3.5 h-3.5 text-cyan-400" />
                            Dataset
                          </span>
                          <span className="text-slate-300 font-mono text-[11px]">
                            {sc.dataset_row_count} records (Synthetic)
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Actions Bottom Bar */}
                    <div className="pt-4 mt-6 border-t border-slate-800 flex items-center justify-between gap-3">
                      <Link
                        href={`/employee/labs/${sc.id}`}
                        className="text-xs font-semibold text-slate-400 hover:text-white transition flex items-center gap-1"
                      >
                        <span>View Scenario</span>
                        <ArrowRight className="w-3 h-3 text-slate-500" />
                      </Link>

                      <button
                        onClick={() => handleStartLab(sc.id)}
                        disabled={isStarting}
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs transition shadow-md shadow-violet-950/40 disabled:opacity-50"
                      >
                        {isStarting ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Starting Practice...</span>
                          </>
                        ) : (
                          <>
                            <span>Start Practice</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </PageContainer>
    </AppShell>
  );
}

export default function VirtualLabsHubPage() {
  return (
    <Suspense
      fallback={
        <AppShell role="EMPLOYEE" pageTitle="Virtual Labs">
          <PageContainer>
            <div className="flex items-center justify-center min-h-[50vh]">
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            </div>
          </PageContainer>
        </AppShell>
      }
    >
      <VirtualLabsHubContent />
    </Suspense>
  );
}

