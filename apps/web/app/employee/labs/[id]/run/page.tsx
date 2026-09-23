'use client';

import React, { useState, useMemo, Suspense } from 'react';
import Link from 'next/link';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import {
  FlaskConical,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Database,
  ChevronLeft,
  ChevronRight,
  Loader2,
  HelpCircle,
  Search,
} from 'lucide-react';
import {
  useLabScenario,
  useLabSession,
  useSubmitLabAction,
  useCompleteLabSession,
  useLabHint,
} from '@/hooks/use-labs';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';

function VirtualLabPlayerContent() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();

  const paramScenarioId = params.id as string;
  const sessionId = searchParams.get('sessionId') || '';
  const courseId = searchParams.get('courseId') || '';

  const { data: session, isLoading: isLoadingSession, refetch: refetchSession } = useLabSession(sessionId);
  // Fallback to session.scenario_id if the URL param has a typo (e.g. ...6660 vs ...6602)
  const resolvedScenarioId = session?.scenario_id || paramScenarioId;
  const { data: scenario, isLoading: isLoadingScenario } = useLabScenario(resolvedScenarioId);

  const submitActionMutation = useSubmitLabAction(sessionId);
  const completeLabMutation = useCompleteLabSession(sessionId);
  const hintMutation = useLabHint(sessionId);

  // Active step state (1-indexed, local override or session current step)
  const [selectedStep, setSelectedStep] = useState<number | null>(null);
  const activeStep = selectedStep ?? (session?.current_step || 1);
  const [showHint, setShowHint] = useState<boolean>(false);
  const [hintContent, setHintContent] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  // Data Viewer state
  const [dataSearch, setDataSearch] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const pageSize = 8;

  // Controlled Action Form States (Starts intentionally unselected/unanswered)
  // Scenario 1 (Data Quality)
  const [dqIssues, setDqIssues] = useState<string[]>([]);
  const [dqRules, setDqRules] = useState<string[]>([]);
  const [dqStrategy, setDqStrategy] = useState<string>('');
  const [dqNotes, setDqNotes] = useState<string>('');

  // Scenario 2 (Sampling)
  const [sampleMethod, setSampleMethod] = useState<string>('');
  const [sampleSize, setSampleSize] = useState<number | ''>('');
  const [strataFields, setStrataFields] = useState<string[]>([]);
  const [allocationMethod, setAllocationMethod] = useState<string>('');

  // Scenario 3 (Descriptive Stats)
  const [statsMetrics, setStatsMetrics] = useState<string[]>([]);
  const [dispersionMetrics, setDispersionMetrics] = useState<string[]>([]);
  const [skewDiagnosis, setSkewDiagnosis] = useState<string>('');
  const [recommendedMeasure, setRecommendedMeasure] = useState<string>('');

  // Scenario 4 (Missing Data)
  const [missingMechanism, setMissingMechanism] = useState<string>('');
  const [missingStrategy, setMissingStrategy] = useState<string>('');

  // Sync previously completed actions into form state for review
  React.useEffect(() => {
    if (!session?.actions) return;
    const a1 = session.actions.find((a) => a.step_number === 1);
    if (a1?.action_payload?.sampling_method && !sampleMethod) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSampleMethod(String(a1.action_payload.sampling_method));
    }
    const a2 = session.actions.find((a) => a.step_number === 2);
    if (a2?.action_payload?.sample_size !== undefined && sampleSize === '') {
      setSampleSize(Number(a2.action_payload.sample_size));
    }
    const a3 = session.actions.find((a) => a.step_number === 3);
    if (a3?.action_payload?.strata_fields && strataFields.length === 0) {
      setStrataFields(a3.action_payload.strata_fields as string[]);
    }
    if (a3?.action_payload?.allocation_method && !allocationMethod) {
      setAllocationMethod(String(a3.action_payload.allocation_method));
    }
  }, [session]);

  // Handle Hint Request
  const handleRequestHint = () => {
    hintMutation.mutate(activeStep, {
      onSuccess: (res) => {
        setHintContent(`${res.hint} (${res.guidance})`);
        setShowHint(true);
      },
    });
  };

  // Handle Action Submit
  const handleSubmitStepAction = () => {
    if (!scenario) return;
    setActionError(null);

    let payload: Record<string, unknown> = {};
    const scType = scenario.scenario_type;

    if (scType === 'DATA_QUALITY_AUDIT') {
      if (activeStep === 1) {
        if (dqIssues.length === 0) {
          setActionError('Please select at least one observed data quality issue before submitting.');
          return;
        }
        payload = { identified_issues: dqIssues };
      } else if (activeStep === 2) {
        if (dqRules.length === 0) {
          setActionError('Please configure at least one NQAF validation rule before submitting.');
          return;
        }
        payload = { selected_rules: dqRules };
      } else if (activeStep === 3) {
        if (!dqStrategy) {
          setActionError('Please select a controlled cleansing routine before submitting.');
          return;
        }
        payload = { correction_strategy: dqStrategy, apply_all: true };
      } else if (activeStep === 4) {
        payload = { report_notes: dqNotes || 'Standard audit completion notes.' };
      }
    } else if (scType === 'SURVEY_SAMPLING') {
      if (activeStep === 1) {
        if (!sampleMethod) {
          setActionError('Please select a probability sampling method before running the step analysis.');
          return;
        }
        payload = { sampling_method: sampleMethod };
      } else if (activeStep === 2) {
        if (sampleSize === '' || isNaN(Number(sampleSize)) || Number(sampleSize) <= 0) {
          setActionError('Please enter a valid sample size (e.g. 25–45) before running the step analysis.');
          return;
        }
        payload = { sample_size: Number(sampleSize) };
      } else if (activeStep === 3) {
        if (strataFields.length === 0) {
          setActionError('Please select at least one stratification field (e.g. Region or Sector).');
          return;
        }
        if (!allocationMethod) {
          setActionError('Please select an allocation strategy before running analysis.');
          return;
        }
        payload = { strata_fields: strataFields, allocation_method: allocationMethod };
      } else if (activeStep === 4) {
        // Step 4 executes the deterministic simulation using the learner's sample size from Step 2
        payload = { sample_size: sampleSize !== '' ? Number(sampleSize) : 30 };
      }
    } else if (scType === 'DESCRIPTIVE_STATISTICS') {
      if (activeStep === 1) payload = { target_column: 'per_capita_expenditure_inr', metrics: statsMetrics.length ? statsMetrics : ['MEAN', 'MEDIAN'] };
      else if (activeStep === 2) payload = { target_column: 'per_capita_expenditure_inr', metrics: dispersionMetrics.length ? dispersionMetrics : ['MIN', 'MAX', 'STD_DEV'] };
      else if (activeStep === 3) {
        if (!skewDiagnosis || !recommendedMeasure) {
          setActionError('Please select both a skewness diagnosis and an official central measure.');
          return;
        }
        payload = { skewness_diagnosis: skewDiagnosis, recommended_central_measure: recommendedMeasure };
      }
    } else if (scType === 'MISSING_DATA_ANALYSIS') {
      if (activeStep === 1) payload = {};
      else if (activeStep === 2) {
        if (!missingMechanism) {
          setActionError('Please select a missingness mechanism before submitting.');
          return;
        }
        payload = { mechanism: missingMechanism };
      } else if (activeStep === 3) {
        if (!missingStrategy) {
          setActionError('Please select a handling strategy before submitting.');
          return;
        }
        payload = { handling_strategy: missingStrategy };
      } else if (activeStep === 4) payload = {};
    }

    const currentStepConfig = scenario.instructions?.steps?.[activeStep - 1];
    const actionType = currentStepConfig?.action_type || 'EXECUTE_STEP';

    submitActionMutation.mutate(
      {
        step_number: activeStep,
        action_type: actionType,
        action_payload: payload,
      },
      {
        onSuccess: (result) => {
          setActionError(null);
          refetchSession();
          if (result.is_completed) {
            // All steps completed; keep user on step or let them review
          } else {
            setSelectedStep(result.next_step);
          }
        },
        onError: (err: unknown) => {
          const errorMsg = err instanceof Error ? err.message : (err as { message?: string })?.message;
          setActionError(errorMsg || 'Action evaluation failed. Please verify your inputs and retry.');
        },
      }
    );
  };

  // Handle Lab Completion
  const handleCompleteLab = () => {
    setActionError(null);
    completeLabMutation.mutate(undefined, {
      onSuccess: () => {
        const dest = courseId
          ? `/employee/labs/${resolvedScenarioId}/result?sessionId=${sessionId}&courseId=${courseId}`
          : `/employee/labs/${resolvedScenarioId}/result?sessionId=${sessionId}`;
        router.push(dest);
      },
      onError: (err: unknown) => {
        const errorMsg = err instanceof Error ? err.message : (err as { message?: string })?.message;
        setActionError(errorMsg || 'Failed to complete lab session. Ensure all required steps are executed.');
      },
    });
  };

  // Safe Data Viewer Logic
  const rawRecords = useMemo(
    () => scenario?.dataset?.dataset_json || [],
    [scenario?.dataset?.dataset_json]
  );
  const columns = Object.keys(scenario?.dataset?.schema_definition || {});

  const filteredRecords = useMemo(() => {
    if (!dataSearch.trim()) return rawRecords;
    const q = dataSearch.toLowerCase();
    return rawRecords.filter((row) =>
      Object.values(row).some((val) => String(val).toLowerCase().includes(q))
    );
  }, [rawRecords, dataSearch]);

  const totalPages = Math.ceil(filteredRecords.length / pageSize) || 1;
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRecords.slice(start, start + pageSize);
  }, [filteredRecords, currentPage, pageSize]);

  if (isLoadingScenario || isLoadingSession || !scenario || !session) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Virtual Lab Player">
        <PageContainer>
          <div className="flex flex-col items-center justify-center p-24 space-y-3">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading virtual simulation sandbox...</p>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const totalSteps = scenario.instructions?.total_steps || 4;
  const stepsList = scenario.instructions?.steps || [];
  const currentStepInfo = stepsList[activeStep - 1] || stepsList[0];
  const stepAction = session.actions.find((a) => a.step_number === activeStep);

  const step1Done = !!session.actions.find((a) => a.step_number === 1 && a.is_correct);
  const step2Done = !!session.actions.find((a) => a.step_number === 2 && a.is_correct);
  const step3Done = !!session.actions.find((a) => a.step_number === 3 && a.is_correct);
  const step4Done = !!session.actions.find((a) => a.step_number === 4 && a.is_correct);

  const steps1to3Completed = step1Done && step2Done && step3Done;
  const isStep4Locked = activeStep === 4 && !steps1to3Completed;
  const allStepsCompleted = steps1to3Completed && step4Done;

  return (
    <AppShell role="EMPLOYEE" pageTitle={`Lab: ${scenario.title}`}>
      <PageContainer>
        <div className="space-y-4 max-w-[1600px] mx-auto pb-20">
          {/* Top Sticky Progress & Status Bar */}
          <div className="bg-[#0A0E1A]/95 border border-slate-800 p-4 rounded-2xl shadow-xl backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3 w-full md:w-auto">
              <Link
                href="/employee/labs"
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition shrink-0"
              >
                <ChevronLeft className="w-4 h-4" />
              </Link>
              <div>
                <h1 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                  <FlaskConical className="w-4 h-4 text-violet-400 shrink-0" />
                  <span className="truncate max-w-md">{scenario.title}</span>
                </h1>
                <div className="flex items-center gap-2 mt-0.5 text-[11px] text-slate-400">
                  <span className="font-mono text-violet-300">
                    Step {activeStep} of {totalSteps}
                  </span>
                  <span>•</span>
                  <span>{scenario.competency_name}</span>
                </div>
              </div>
            </div>

            {/* Score & Synthetic Badge */}
            <div className="flex items-center gap-3 w-full md:w-auto justify-end">
              <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
                <span className="text-slate-400 mr-2">Session Score:</span>
                <span className="text-emerald-400 font-bold">{session.score || 0} pts</span>
              </div>

              <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px]">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>Synthetic Training Data</span>
              </div>
            </div>
          </div>

          {/* 3-COLUMN SIMULATION WORKSPACE */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* ------------------------------------------------------------- */}
            {/* LEFT COLUMN: Scenario Instructions & Step Checklist (3 cols) */}
            {/* ------------------------------------------------------------- */}
            <div className="lg:col-span-3 space-y-4">
              <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-violet-400" />
                  Simulation Steps
                </h3>

                <div className="space-y-2">
                  {stepsList.map((st) => {
                    const actionForStep = session.actions.find((a) => a.step_number === st.step_number);
                    const isDone = !!actionForStep?.is_correct;
                    const isStepLocked = st.step_number === 4 && !steps1to3Completed;
                    const isCurrent = st.step_number === activeStep;

                    let statusSymbol = '○';
                    let statusLabel = 'UPCOMING';
                    let statusClass = 'bg-slate-900/40 border-slate-800 text-slate-500 hover:bg-slate-900/60';
                    let badgeClass = 'bg-slate-800 text-slate-400';

                    if (isDone) {
                      statusSymbol = '✓';
                      statusLabel = 'COMPLETED';
                      statusClass = 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200 hover:bg-emerald-950/30';
                      badgeClass = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
                    } else if (isStepLocked) {
                      statusSymbol = '🔒';
                      statusLabel = 'LOCKED';
                      statusClass = 'bg-slate-900/20 border-slate-800/60 text-slate-600';
                      badgeClass = 'bg-slate-800 text-slate-500';
                    } else if (isCurrent) {
                      statusSymbol = '→';
                      statusLabel = 'CURRENT';
                      statusClass = 'bg-violet-600/15 border-violet-500/40 text-white shadow-md ring-1 ring-violet-500/30';
                      badgeClass = 'bg-violet-600 text-white';
                    }

                    return (
                      <button
                        key={st.step_number}
                        onClick={() => setSelectedStep(st.step_number)}
                        className={`w-full text-left p-3 rounded-xl border transition-all flex items-start gap-2.5 ${statusClass}`}
                      >
                        <span
                          className={`w-5 h-5 rounded-full flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5 ${badgeClass}`}
                        >
                          {statusSymbol}
                        </span>
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold">
                              {statusSymbol} Step {st.step_number} — {st.title}
                            </span>
                            <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-white/5 border border-white/10 uppercase">
                              {statusLabel}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 line-clamp-1">
                            {st.description}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Lab Guidelines Box */}
              <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-2 text-xs text-slate-400">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                  Execution Sandbox Rules
                </span>
                <p className="leading-relaxed text-[11px]">
                  All analytical operations are computed by authoritative MoSPI backend logic. No arbitrary code execution or live database modifications are permitted.
                </p>
              </div>
            </div>

            {/* ------------------------------------------------------------- */}
            {/* CENTER COLUMN: Safe Tabular Data Viewer & Tools (6 cols)     */}
            {/* ------------------------------------------------------------- */}
            <div className="lg:col-span-6 space-y-4">
              <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-4 shadow-xl">
                {/* Data Viewer Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-cyan-400" />
                    <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                      Interactive Microdata Viewer
                    </h2>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">
                      {rawRecords.length} records
                    </span>
                  </div>

                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder="Filter records..."
                      value={dataSearch}
                      onChange={(e) => {
                        setDataSearch(e.target.value);
                        setCurrentPage(1);
                      }}
                      className="pl-8 pr-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-48"
                    />
                  </div>
                </div>

                {/* Tabular Display */}
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-900/90 text-slate-400 border-b border-slate-800 font-mono text-[11px]">
                        {columns.map((col) => (
                          <th key={col} className="p-2.5 font-medium whitespace-nowrap">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-[#0B0F19]">
                      {paginatedRows.length === 0 ? (
                        <tr>
                          <td colSpan={columns.length} className="p-6 text-center text-slate-500">
                            No records match your filter.
                          </td>
                        </tr>
                      ) : (
                        paginatedRows.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-slate-900/40 transition">
                            {columns.map((col) => {
                              const val = row[col];
                              const isMissing = val === null || val === undefined || String(val).trim() === '';
                              const isNegative = typeof val === 'number' && val < 0;

                              return (
                                <td key={col} className="p-2.5 font-mono text-[11px] whitespace-nowrap">
                                  {isMissing ? (
                                    <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 text-[10px] font-sans">
                                      null
                                    </span>
                                  ) : isNegative ? (
                                    <span className="text-rose-400 font-bold">{val}</span>
                                  ) : typeof val === 'boolean' ? (
                                    <span className={val ? 'text-emerald-400' : 'text-slate-400'}>
                                      {val ? 'TRUE' : 'FALSE'}
                                    </span>
                                  ) : (
                                    <span className="text-slate-300">{String(val)}</span>
                                  )}
                                </td>
                              );
                            })}
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                  <span>
                    Page {currentPage} of {totalPages}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage <= 1}
                      className="p-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-30"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage >= totalPages}
                      className="p-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-30"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* ------------------------------------------------------------- */}
            {/* RIGHT COLUMN: Current Task & Controlled Action Form (3 cols)  */}
            {/* ------------------------------------------------------------- */}
            <div className="lg:col-span-3 space-y-4">
              <div className="p-5 rounded-2xl bg-[#0B0F19] border border-slate-800 space-y-5 shadow-xl">
                {/* Step Header */}
                <div className="space-y-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase font-bold tracking-wider text-violet-400">
                      TASK {activeStep} OF {totalSteps}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-violet-500/10 text-violet-300 border border-violet-500/25">
                      {currentStepInfo.action_type?.replace(/_/g, ' ') || 'ANALYSIS'}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white leading-tight">
                    {currentStepInfo.title}
                  </h3>

                  {/* Explicit YOUR TASK and WHAT TO DO panels */}
                  <div className="space-y-2 text-xs">
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 block">
                        YOUR TASK:
                      </span>
                      <p className="text-slate-300 leading-relaxed">
                        {currentStepInfo.task_instructions || currentStepInfo.description}
                      </p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 block">
                        WHAT TO DO:
                      </span>
                      <p className="text-slate-300 leading-relaxed">
                        Select the required analysis configuration and run it.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Controlled Interactive Form Controls per Scenario */}
                <div className="space-y-4">
                  {/* 1. DATA QUALITY AUDIT CONTROLS */}
                  {scenario.scenario_type === 'DATA_QUALITY_AUDIT' && (
                    <>
                      {activeStep === 1 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Flag anomalies observed in dataset:
                          </span>
                          {[
                            { id: 'DUPLICATE_ROWS', label: 'Duplicate Rows (Multiple identical IDs)' },
                            { id: 'OUT_OF_RANGE', label: 'Out-of-range negative expenditure' },
                            { id: 'INVALID_CODE', label: "Invalid district code ('XX99')" },
                            { id: 'INCONSISTENT_CATEGORY', label: "Inconsistent categories ('agri_cult')" },
                          ].map((item) => (
                            <label
                              key={item.id}
                              className="flex items-start gap-2 p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-200 cursor-pointer hover:bg-slate-800/40"
                            >
                              <input
                                type="checkbox"
                                checked={dqIssues.includes(item.id)}
                                onChange={(e) => {
                                  if (e.target.checked) setDqIssues([...dqIssues, item.id]);
                                  else setDqIssues(dqIssues.filter((x) => x !== item.id));
                                }}
                                className="mt-0.5 rounded border-slate-700 text-violet-600 focus:ring-violet-500"
                              />
                              <span>{item.label}</span>
                            </label>
                          ))}
                        </div>
                      )}

                      {activeStep === 2 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Select NQAF Validation Rules to apply:
                          </span>
                          {[
                            { id: 'NQAF_UNIQUE_KEY', label: 'NQAF Rule 4.1: Unique Frame Key' },
                            { id: 'NQAF_RANGE_CHECK', label: 'NQAF Rule 4.2: Range Bounds Validation' },
                            { id: 'NQAF_CODE_LOOKUP', label: 'NQAF Rule 4.3: Administrative Code Lookup' },
                          ].map((rule) => (
                            <label
                              key={rule.id}
                              className="flex items-start gap-2 p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-200 cursor-pointer hover:bg-slate-800/40"
                            >
                              <input
                                type="checkbox"
                                checked={dqRules.includes(rule.id)}
                                onChange={(e) => {
                                  if (e.target.checked) setDqRules([...dqRules, rule.id]);
                                  else setDqRules(dqRules.filter((r) => r !== rule.id));
                                }}
                                className="mt-0.5 rounded border-slate-700 text-violet-600"
                              />
                              <span>{rule.label}</span>
                            </label>
                          ))}
                        </div>
                      )}

                      {activeStep === 3 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Controlled Cleansing Routine:
                          </span>
                          <select
                            value={dqStrategy}
                            onChange={(e) => setDqStrategy(e.target.value)}
                            className="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                          >
                            <option value="DEDUPLICATE_AND_CLEAN">Deduplicate & Normalize Categories (Recommended)</option>
                            <option value="REMOVE_DUPLICATES">Remove Duplicates Only</option>
                            <option value="STANDARDIZE_CATEGORIES">Standardize Categories Only</option>
                          </select>
                        </div>
                      )}

                      {activeStep === 4 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Audit Sign-off Notes:
                          </span>
                          <textarea
                            value={dqNotes}
                            onChange={(e) => setDqNotes(e.target.value)}
                            rows={3}
                            className="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                          />
                        </div>
                      )}
                    </>
                  )}

                  {/* 2. SURVEY SAMPLING CONTROLS */}
                  {scenario.scenario_type === 'SURVEY_SAMPLING' && (
                    <>
                      {activeStep === 1 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Choose Probability Sampling Method: <span className="text-rose-400">*</span>
                          </span>
                          {!sampleMethod && (
                            <div className="text-[11px] text-amber-400/90 italic pb-1">
                              Please select an appropriate probability sampling method below to proceed.
                            </div>
                          )}
                          {[
                            { id: 'STRATIFIED', label: 'Stratified Sampling (Preserves Sub-populations)' },
                            { id: 'SIMPLE_RANDOM', label: 'Simple Random Sampling (SRS)' },
                            { id: 'SYSTEMATIC', label: 'Systematic Sampling (k-interval)' },
                          ].map((m) => (
                            <label
                              key={m.id}
                              className={`flex items-start gap-2.5 p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                                sampleMethod === m.id
                                  ? 'bg-violet-950/40 border-violet-500/60 text-white shadow-sm'
                                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/40'
                              }`}
                            >
                              <input
                                type="radio"
                                name="sampleMethod"
                                value={m.id}
                                checked={sampleMethod === m.id}
                                onChange={(e) => setSampleMethod(e.target.value)}
                                className="mt-0.5 text-violet-600 focus:ring-violet-500"
                              />
                              <span className="font-medium">{m.label}</span>
                            </label>
                          ))}
                        </div>
                      )}

                      {activeStep === 2 && (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-300">
                              Target Sample Size (n): <span className="text-rose-400">*</span>
                            </span>
                            <span className="font-mono text-violet-300 font-bold">
                              {sampleSize === '' ? 'Unspecified' : `${sampleSize} / 100`}
                            </span>
                          </div>

                          <div className="space-y-1.5">
                            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">
                              Select Sample Size:
                            </span>
                            <div className="grid grid-cols-3 gap-2">
                              {[
                                { val: 15, label: 'n = 15 (Pilot)' },
                                { val: 30, label: 'n = 30 (Recommended)' },
                                { val: 60, label: 'n = 60 (Large)' },
                              ].map((preset) => (
                                <button
                                  key={preset.val}
                                  type="button"
                                  onClick={() => setSampleSize(preset.val)}
                                  className={`p-2 rounded-lg border text-xs font-mono transition text-center ${
                                    sampleSize === preset.val
                                      ? 'bg-violet-950/50 border-violet-500 text-violet-200 font-bold ring-1 ring-violet-500/40'
                                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                                  }`}
                                >
                                  {preset.label}
                                </button>
                              ))}
                            </div>
                          </div>

                          <div>
                            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold mb-1">
                              Or Enter Custom Sample Size:
                            </span>
                            <input
                              type="number"
                              min="1"
                              max="100"
                              placeholder="Enter target sample size (e.g. 30)"
                              value={sampleSize}
                              onChange={(e) => {
                                const v = e.target.value;
                                setSampleSize(v === '' ? '' : Number(v));
                              }}
                              className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-violet-500 font-mono"
                            />
                          </div>
                          <p className="text-[11px] text-slate-400">
                            Recommended: 25 to 45 units for representative power with ~10% margin of error across N=100 frame.
                          </p>
                        </div>
                      )}

                      {activeStep === 3 && (
                        <div className="space-y-3">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Configure Strata Variables: <span className="text-rose-400">*</span>
                          </span>
                          {strataFields.length === 0 && (
                            <div className="text-[11px] text-amber-400/90 italic">
                              Select one or more stratification fields from the household frame.
                            </div>
                          )}
                          <div className="space-y-1.5">
                            {[
                              { id: 'region', label: 'Region (North / South)' },
                              { id: 'sector', label: 'Sector (Rural / Urban)' },
                              { id: 'expenditure_bracket', label: 'Expenditure Bracket' },
                            ].map((f) => (
                              <label
                                key={f.id}
                                className={`flex items-center gap-2.5 p-2 rounded-lg border text-xs cursor-pointer transition ${
                                  strataFields.includes(f.id)
                                    ? 'bg-violet-950/40 border-violet-500/60 text-white'
                                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/40'
                                }`}
                              >
                                <input
                                  type="checkbox"
                                  checked={strataFields.includes(f.id)}
                                  onChange={(e) => {
                                    if (e.target.checked) {
                                      setStrataFields([...strataFields, f.id]);
                                    } else {
                                      setStrataFields(strataFields.filter((item) => item !== f.id));
                                    }
                                  }}
                                  className="rounded text-violet-600 focus:ring-violet-500"
                                />
                                <span>{f.label}</span>
                              </label>
                            ))}
                          </div>

                          <span className="text-[11px] font-medium text-slate-300 block pt-1">
                            Allocation Strategy: <span className="text-rose-400">*</span>
                          </span>
                          <select
                            value={allocationMethod}
                            onChange={(e) => setAllocationMethod(e.target.value)}
                            className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                          >
                            <option value="">-- Select Allocation Method --</option>
                            <option value="PROPORTIONAL">Proportional Allocation (Recommended by MoSPI)</option>
                            <option value="OPTIMAL">Neyman / Optimal Allocation</option>
                            <option value="EQUAL">Equal Allocation</option>
                          </select>
                        </div>
                      )}

                      {activeStep === 4 && (
                        isStep4Locked ? (
                          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 space-y-1.5">
                            <div className="flex items-center gap-2 font-semibold text-amber-400">
                              <ShieldCheck className="w-4 h-4" />
                              <span>Step 4 Locked</span>
                            </div>
                            <p className="text-[11px] text-slate-300">
                              Step 4 (Deterministic Simulation) requires Steps 1, 2, and 3 to be successfully validated first.
                            </p>
                          </div>
                        ) : (
                          <div className="p-3.5 rounded-xl bg-violet-950/20 border border-violet-500/30 text-xs text-slate-300 space-y-2">
                            <p className="font-semibold text-violet-300">Deterministic Simulation Engine Ready</p>
                            <p className="text-[11px] text-slate-400">
                              Ready to execute deterministic seeded simulation (PRNG seed=42) across your configured strata ({strataFields.length > 0 ? strataFields.join(' + ') : 'Region + Sector'}, sample size n={sampleSize || 30}).
                            </p>
                          </div>
                        )
                      )}
                    </>
                  )}

                  {/* 3. DESCRIPTIVE STATISTICS CONTROLS */}
                  {scenario.scenario_type === 'DESCRIPTIVE_STATISTICS' && (
                    <>
                      {activeStep === 1 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Compute Central Tendency Metrics:
                          </span>
                          <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 space-y-1.5">
                            <div>Target Column: <strong>per_capita_expenditure_inr</strong></div>
                            <div>Metrics: <strong>Mean & Median</strong></div>
                          </div>
                        </div>
                      )}

                      {activeStep === 2 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Compute Dispersion Metrics:
                          </span>
                          <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 space-y-1.5">
                            <div>Metrics: <strong>Min, Max, Standard Deviation</strong></div>
                          </div>
                        </div>
                      )}

                      {activeStep === 3 && (
                        <div className="space-y-3">
                          <div>
                            <span className="text-[11px] font-medium text-slate-300 block mb-1">
                              Skewness Diagnosis:
                            </span>
                            <select
                              value={skewDiagnosis}
                              onChange={(e) => setSkewDiagnosis(e.target.value)}
                              className="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200"
                            >
                              <option value="RIGHT_SKEWED">Right Skewed (Mean &gt; Median)</option>
                              <option value="SYMMETRIC">Symmetric (Mean ≈ Median)</option>
                              <option value="LEFT_SKEWED">Left Skewed (Mean &lt; Median)</option>
                            </select>
                          </div>

                          <div>
                            <span className="text-[11px] font-medium text-slate-300 block mb-1">
                              Recommended Official Central Measure:
                            </span>
                            <select
                              value={recommendedMeasure}
                              onChange={(e) => setRecommendedMeasure(e.target.value)}
                              className="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200"
                            >
                              <option value="MEDIAN">Median (Robust to Outliers)</option>
                              <option value="MEAN">Arithmetic Mean</option>
                            </select>
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {/* 4. MISSING DATA ANALYSIS CONTROLS */}
                  {scenario.scenario_type === 'MISSING_DATA_ANALYSIS' && (
                    <>
                      {activeStep === 1 && (
                        <p className="text-xs text-slate-300">
                          Click &ldquo;Execute Step&rdquo; to scan all columns and compute non-response rates.
                        </p>
                      )}

                      {activeStep === 2 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Diagnose Missingness Mechanism:
                          </span>
                          {[
                            { id: 'MAR', label: 'MAR (Missing at Random — Correlated with Enterprise Size)' },
                            { id: 'MCAR', label: 'MCAR (Missing Completely at Random)' },
                            { id: 'MNAR', label: 'MNAR (Missing Not at Random)' },
                          ].map((item) => (
                            <label
                              key={item.id}
                              className="flex items-start gap-2 p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-200 cursor-pointer"
                            >
                              <input
                                type="radio"
                                name="mechanism"
                                value={item.id}
                                checked={missingMechanism === item.id}
                                onChange={(e) => setMissingMechanism(e.target.value)}
                                className="mt-0.5 text-violet-600"
                              />
                              <span>{item.label}</span>
                            </label>
                          ))}
                        </div>
                      )}

                      {activeStep === 3 && (
                        <div className="space-y-2">
                          <span className="text-[11px] font-medium text-slate-300 block">
                            Select Handling Strategy:
                          </span>
                          <select
                            value={missingStrategy}
                            onChange={(e) => setMissingStrategy(e.target.value)}
                            className="w-full p-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200"
                          >
                            <option value="MEDIAN_IMPUTATION">Median Imputation (Preserves N=25 Sample)</option>
                            <option value="REMOVE">Listwise Deletion (Drop Incomplete Rows)</option>
                            <option value="KEEP">Keep with Missingness Flag</option>
                          </select>
                        </div>
                      )}

                      {activeStep === 4 && (
                        <p className="text-xs text-slate-300">
                          Confirm evaluation of post-imputation impact and sample variance retention.
                        </p>
                      )}
                    </>
                  )}
                </div>

                {/* Action Error Banner */}
                {actionError && (
                  <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs text-rose-300 flex items-start gap-2">
                    <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <span className="font-bold block">Execution Error:</span>
                      <span>{actionError}</span>
                    </div>
                  </div>
                )}

                {/* Step Action Button */}
                {(() => {
                  const scType = scenario.scenario_type;
                  let isStepUnanswered = false;
                  if (scType === 'SURVEY_SAMPLING') {
                    if (activeStep === 1) isStepUnanswered = !sampleMethod;
                    else if (activeStep === 2) isStepUnanswered = sampleSize === '' || Number(sampleSize) <= 0;
                    else if (activeStep === 3) isStepUnanswered = strataFields.length === 0 || !allocationMethod;
                    else if (activeStep === 4) isStepUnanswered = isStep4Locked;
                  } else if (scType === 'DATA_QUALITY_AUDIT') {
                    if (activeStep === 1) isStepUnanswered = dqIssues.length === 0;
                    else if (activeStep === 2) isStepUnanswered = dqRules.length === 0;
                    else if (activeStep === 3) isStepUnanswered = !dqStrategy;
                  }

                  const buttonLabel =
                    activeStep === 3
                      ? 'Run Analysis'
                      : activeStep === 4
                      ? 'Execute Simulation'
                      : 'Run Step Analysis';

                  const isDisabled = submitActionMutation.isPending || isStepUnanswered || isStep4Locked;

                  return (
                    <div className="space-y-2">
                      <button
                        onClick={handleSubmitStepAction}
                        disabled={isDisabled}
                        className={`w-full py-2.5 px-4 rounded-xl font-semibold text-xs flex items-center justify-center gap-2 transition shadow-md ${
                          isDisabled
                            ? 'bg-slate-800/80 text-slate-500 border border-slate-700/60 cursor-not-allowed'
                            : 'bg-violet-600 hover:bg-violet-500 text-white shadow-violet-950/40 cursor-pointer'
                        }`}
                      >
                        {submitActionMutation.isPending ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>{activeStep === 4 ? 'Executing Simulation...' : 'Running Analysis...'}</span>
                          </>
                        ) : (
                          <>
                            <span>{buttonLabel}</span>
                            <ArrowRight className="w-4 h-4" />
                          </>
                        )}
                      </button>

                      {isStepUnanswered && !isStep4Locked && (
                        <p className="text-[11px] text-amber-400/80 text-center">
                          {activeStep === 1
                            ? 'Select a probability sampling method above to enable analysis.'
                            : activeStep === 2
                            ? 'Select or enter a target sample size above to enable analysis.'
                            : activeStep === 3
                            ? 'Select strata variables and allocation method above to enable analysis.'
                            : ''}
                        </p>
                      )}
                    </div>
                  );
                })()}

                {/* Instant Feedback Box: RESULT, WHAT YOU DID, WHY IT IS CORRECT, POINTS EARNED */}
                {stepAction && (
                  <div
                    className={`p-4 rounded-xl border space-y-2.5 ${
                      stepAction.is_correct
                        ? 'bg-emerald-950/25 border-emerald-500/35'
                        : 'bg-rose-950/25 border-rose-500/35'
                    }`}
                  >
                    {/* RESULT */}
                    <div className="flex items-center justify-between pb-2 border-b border-white/10">
                      <div className="flex items-center gap-1.5">
                        {stepAction.is_correct ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                              RESULT: Correct Analysis
                            </span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                            <span className="text-xs font-bold uppercase tracking-wider text-rose-300">
                              RESULT: Needs Revision
                            </span>
                          </>
                        )}
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-white/10 text-white">
                        POINTS EARNED: +{stepAction.score_awarded} pts
                      </span>
                    </div>

                    {/* WHAT YOU DID */}
                    <div className="space-y-0.5">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                        WHAT YOU DID:
                      </span>
                      <p className="text-xs text-slate-200">
                        Executed {stepAction.action_type.replace(/_/g, ' ').toLowerCase()}
                        {stepAction.action_payload && Object.keys(stepAction.action_payload).length > 0
                          ? ` with parameters: ${Object.entries(stepAction.action_payload)
                              .map(([k, v]) => `${k.replace(/_/g, ' ')} = ${Array.isArray(v) ? v.join(', ') : String(v)}`)
                              .join('; ')}`
                          : '.'}
                      </p>
                    </div>

                    {/* WHY IT IS CORRECT */}
                    <div className="space-y-0.5">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                        {stepAction.is_correct ? 'WHY IT IS CORRECT:' : 'AUDIT GUIDANCE:'}
                      </span>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {stepAction.feedback}
                      </p>
                    </div>
                  </div>
                )}

                {/* Next Step Navigation CTA for Steps 1 and 2 */}
                {stepAction?.is_correct && activeStep < 3 && (
                  <div className="p-3.5 rounded-xl bg-violet-950/30 border border-violet-500/30 flex items-center justify-between gap-3">
                    <div className="text-xs text-slate-300">
                      <span className="font-semibold text-emerald-400">Step {activeStep} Validated!</span> Proceed to Step {activeStep + 1}.
                    </div>
                    <button
                      onClick={() => setSelectedStep(activeStep + 1)}
                      className="py-1.5 px-3.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs flex items-center gap-1.5 transition shrink-0 shadow-md shadow-violet-950/40"
                    >
                      <span>Proceed to Step {activeStep + 1}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}

                {/* Educational Hint Drawer */}
                <div className="pt-2 border-t border-slate-800">
                  <button
                    onClick={handleRequestHint}
                    className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 font-medium transition"
                  >
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>Need help?</span>
                  </button>

                  {showHint && hintContent && (
                    <div className="mt-2 p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/30 text-xs space-y-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 block">
                        HINT
                      </span>
                      <p className="text-cyan-200/90 leading-relaxed">
                        {hintContent}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Step 3 Completed Banner with CTA to Step 4 */}
              {activeStep === 3 && stepAction?.is_correct && !allStepsCompleted && (
                <div className="p-4 rounded-2xl bg-gradient-to-r from-violet-950/40 via-slate-900 to-slate-900 border border-violet-500/40 space-y-2.5">
                  <div className="flex items-center gap-2 text-violet-300 font-semibold text-xs">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Step 3 Analysis Complete — Step 4 Simulation Pending</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Your strata configuration was validated. Step 4 (Deterministic Simulation) must be executed to conclude the experiment.
                  </p>
                  <button
                    onClick={() => setSelectedStep(4)}
                    className="w-full py-2 px-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs flex items-center justify-center gap-1.5 transition"
                  >
                    <span>Proceed to Step 4: Execute Simulation</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {/* Lab Completion CTA (when all steps done) */}
              {allStepsCompleted && (
                <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-slate-900 border border-emerald-500/40 space-y-3">
                  <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>All Simulation Steps Completed</span>
                  </div>
                  <button
                    onClick={handleCompleteLab}
                    disabled={completeLabMutation.isPending}
                    className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-emerald-950/40"
                  >
                    {completeLabMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Recording Evidence...</span>
                      </>
                    ) : (
                      <>
                        <span>Submit & View Results</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}

export default function VirtualLabPlayerPage() {
  return (
    <Suspense
      fallback={
        <AppShell role="EMPLOYEE" pageTitle="Virtual Lab Player">
          <PageContainer>
            <div className="flex items-center justify-center min-h-[50vh]">
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            </div>
          </PageContainer>
        </AppShell>
      }
    >
      <VirtualLabPlayerContent />
    </Suspense>
  );
}

