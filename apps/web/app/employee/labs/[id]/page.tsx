'use client';

import React from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import {
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Award,
  ChevronLeft,
  Loader2,
  Table as TableIcon,
} from 'lucide-react';
import { useLabScenario, useStartLabSession } from '@/hooks/use-labs';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';

export default function ScenarioDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scenarioId = params.id as string;

  const { data: scenario, isLoading } = useLabScenario(scenarioId);
  const startSessionMutation = useStartLabSession();

  const handleStartLab = () => {
    if (!scenarioId) return;
    startSessionMutation.mutate(scenarioId, {
      onSuccess: (session) => {
        router.push(`/employee/labs/${scenarioId}/run?sessionId=${session.id}`);
      },
    });
  };

  if (isLoading || !scenario) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Scenario Details">
        <PageContainer>
          <div className="flex flex-col items-center justify-center p-24 space-y-3">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading scenario specifications...</p>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const dataset = scenario.dataset;
  const columns = Object.keys(dataset.schema_definition || {});

  return (
    <AppShell role="EMPLOYEE" pageTitle={scenario.title}>
      <PageContainer>
        <div className="space-y-6 max-w-5xl mx-auto pb-16">
          {/* Back Navigation */}
          <Link
            href="/employee/labs"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Back to Virtual Labs Hub</span>
          </Link>

          {/* Scenario Hero Header */}
          <div className="bg-gradient-to-br from-[#0B0F19] to-slate-900 border border-violet-500/25 p-8 rounded-2xl shadow-xl space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-violet-500/10 text-violet-300 border border-violet-500/30">
                {scenario.scenario_type.replace(/_/g, ' ')}
              </span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                  scenario.difficulty === 'BEGINNER'
                    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                    : scenario.difficulty === 'INTERMEDIATE'
                    ? 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30'
                    : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                }`}
              >
                {scenario.difficulty}
              </span>
              <span className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                {scenario.estimated_minutes} Minutes
              </span>
            </div>

            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              {scenario.title}
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed max-w-3xl">
              {scenario.description}
            </p>

            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-800">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs">
                <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Synthetic Training Data — not official government data.</span>
              </div>

              <button
                onClick={handleStartLab}
                disabled={startSessionMutation.isPending}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-sm transition shadow-lg shadow-violet-950/40 disabled:opacity-50"
              >
                {startSessionMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Starting Lab...</span>
                  </>
                ) : (
                  <>
                    <span>Start Lab</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Learn & Do */}
            <div className="lg:col-span-2 space-y-6">
              {/* WHAT YOU WILL LEARN */}
              <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-violet-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-violet-400" />
                  What You Will Learn
                </h3>
                <ul className="space-y-2.5">
                  {scenario.learning_objectives.map((obj, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2.5">
                      <span className="w-5 h-5 rounded-full bg-violet-500/10 text-violet-400 flex items-center justify-center font-mono text-[10px] shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span className="leading-relaxed">{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* WHAT YOU WILL DO */}
              <div className="p-6 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                  <TableIcon className="w-4 h-4 text-cyan-400" />
                  What You Will Do
                </h3>
                <div className="space-y-3">
                  {scenario.instructions?.steps?.map((st) => (
                    <div
                      key={st.step_number}
                      className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-violet-400 text-[11px]">
                            Step {st.step_number}
                          </span>
                          {st.title}
                        </span>
                        <span className="text-[10px] font-mono text-slate-500 uppercase">
                          {st.action_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        {st.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Col: How this works, Competency, Dataset, Metadata */}
            <div className="space-y-6">
              {/* HOW THIS WORKS Box */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/30 to-[#0B0F19] border border-indigo-500/25 space-y-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 block">
                  How This Works
                </span>
                <ol className="space-y-2 text-xs text-slate-300">
                  {[
                    'Inspect the dataset',
                    'Complete the requested analysis',
                    'Submit the action',
                    'Get immediate feedback',
                    'Finish the scenario and view your result',
                  ].map((stepText, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="w-4 h-4 rounded-full bg-indigo-500/20 text-indigo-300 font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5 font-bold">
                        {idx + 1}
                      </span>
                      <span>{stepText}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* COMPETENCY Card */}
              <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Competency
                </span>
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-violet-600/20 text-violet-400 border border-violet-500/30">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white">
                      {scenario.competency_name || 'Statistical Competency'}
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400">
                      {scenario.competency_code || 'STATISTICAL'}
                    </span>
                  </div>
                </div>
                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                  <span>Difficulty</span>
                  <span className="font-semibold text-slate-200">{scenario.difficulty}</span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Estimated Time</span>
                  <span className="font-semibold text-slate-200">{scenario.estimated_minutes} Minutes</span>
                </div>
              </div>

              {/* DATASET Specifications */}
              <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Dataset
                </span>
                <div className="text-xs font-semibold text-white">
                  {dataset.title}
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Total Records</span>
                  <span className="font-mono text-white font-semibold">
                    {dataset.row_count} records
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Variables / Columns</span>
                  <span className="font-mono text-white font-semibold">
                    {columns.length} columns
                  </span>
                </div>

                <div className="pt-2 border-t border-slate-800 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">
                    Columns / Fields
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {columns.map((col) => (
                      <span
                        key={col}
                        className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-300"
                      >
                        {col}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}
