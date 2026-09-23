'use client';

import React, { useState, useEffect, useMemo, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  BrainCircuit,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Sparkles,
  ShieldCheck,
  Award,
  BookOpen,
  Target,
  Loader2,
  HelpCircle,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useCompetencies } from '@/hooks/use-competency';
import { useEmployeeCompetencies } from '@/hooks/use-assessment';
import { useEmployeeSkillGaps } from '@/hooks/use-skill-gaps';
import {
  useCreateAdaptiveSession,
  useAdaptiveSession,
  useSubmitAdaptiveResponse,
  useCompleteAdaptiveSession,
  useAdaptiveResult,
} from '@/hooks/use-adaptive';
import { getNextAdaptiveQuestion } from '@/lib/api-client';
import type {
  AdaptiveQuestionPresentation,
  AdaptiveSubmitAnswerResponse,
  RecalibrationResultResponse,
} from '@pragya/types';

function AdaptiveAssessmentContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCompetencyId = searchParams.get('competencyId') || '';
  const initialSessionId = searchParams.get('sessionId') || '';

  const { data: employee } = useCurrentEmployee();
  const { data: competenciesData } = useCompetencies({ pageSize: 50 });
  const { data: employeeCompetencies = [] } = useEmployeeCompetencies(employee?.id);
  const { data: skillGaps = [] } = useEmployeeSkillGaps(employee?.id);

  // Core State
  const [selectedCompetencyId, setSelectedCompetencyId] = useState<string>(initialCompetencyId);
  const [sessionId, setSessionId] = useState<string>(initialSessionId);
  const [currentQuestion, setCurrentQuestion] = useState<AdaptiveQuestionPresentation | null>(null);
  const [selectedOptionId, setSelectedOptionId] = useState<string>('');
  const [feedback, setFeedback] = useState<AdaptiveSubmitAnswerResponse | null>(null);
  const [completedResult, setCompletedResult] = useState<RecalibrationResultResponse | null>(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Queries & Mutations
  const createSessionMutation = useCreateAdaptiveSession();
  const submitAnswerMutation = useSubmitAdaptiveResponse(sessionId);
  const completeSessionMutation = useCompleteAdaptiveSession(sessionId);
  const { data: sessionData, refetch: refetchSession } = useAdaptiveSession(sessionId || undefined);
  const { data: resultData } = useAdaptiveResult(sessionId && sessionData?.status === 'COMPLETED' ? sessionId : undefined);

  // Derived recalibration result
  const recalibrationResult = completedResult || resultData || null;

  // Selected competency metadata
  const selectedCompetency = useMemo(() => {
    return competenciesData?.items.find((c) => c.id === selectedCompetencyId);
  }, [competenciesData, selectedCompetencyId]);

  const targetEmpCompetency = useMemo(() => {
    return employeeCompetencies.find((c) => c.competency_id === selectedCompetencyId);
  }, [employeeCompetencies, selectedCompetencyId]);

  const targetSkillGap = useMemo(() => {
    return skillGaps.find((g) => g.competency_id === selectedCompetencyId);
  }, [skillGaps, selectedCompetencyId]);

  // Handle starting a session
  const handleStartAssessment = async () => {
    if (!selectedCompetencyId) {
      setErrorMsg('Please select a competency to reassess.');
      return;
    }
    setErrorMsg(null);
    setIsLoadingQuestion(true);

    try {
      const session = await createSessionMutation.mutateAsync({
        competency_id: selectedCompetencyId,
      });
      // Fetch first question before advancing to runner view
      const question = await getNextAdaptiveQuestion(session.id);
      setSessionId(session.id);
      setCurrentQuestion(question);
      setSelectedOptionId('');
      setFeedback(null);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to start adaptive session.');
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  // If resuming an existing session in progress without current question
  useEffect(() => {
    let isMounted = true;
    if (sessionId && !currentQuestion && !recalibrationResult) {
      getNextAdaptiveQuestion(sessionId)
        .then((q) => {
          if (isMounted) {
            setCurrentQuestion(q);
            setSelectedOptionId('');
            setFeedback(null);
          }
        })
        .catch((err: unknown) => {
          if (isMounted && sessionData?.status !== 'COMPLETED') {
            setErrorMsg(err instanceof Error ? err.message : 'Error fetching question.');
          }
        });
    }
    return () => {
      isMounted = false;
    };
  }, [sessionId, currentQuestion, recalibrationResult, sessionData?.status]);

  // Handle submitting an answer
  const handleSubmitAnswer = async () => {
    if (!selectedOptionId || !currentQuestion || !sessionId) return;
    setErrorMsg(null);

    try {
      const res = await submitAnswerMutation.mutateAsync({
        question_id: currentQuestion.id,
        selected_option_id: selectedOptionId,
      });
      setFeedback(res);
      refetchSession();
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to submit answer.');
    }
  };

  // Handle requesting the next question
  const handleNextQuestion = async () => {
    if (!sessionId) return;
    setIsLoadingQuestion(true);
    setErrorMsg(null);

    try {
      const nextQ = await getNextAdaptiveQuestion(sessionId);
      setCurrentQuestion(nextQ);
      setSelectedOptionId('');
      setFeedback(null);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to retrieve next question.');
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  // Handle completing session and recalibrating
  const handleCompleteSession = async () => {
    if (!sessionId) return;
    setErrorMsg(null);

    try {
      const result = await completeSessionMutation.mutateAsync();
      setCompletedResult(result);
      setCurrentQuestion(null);
      setFeedback(null);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Failed to complete assessment.');
    }
  };

  // Reset to reassess another competency
  const handleReset = () => {
    setSessionId('');
    setCurrentQuestion(null);
    setSelectedOptionId('');
    setFeedback(null);
    setCompletedResult(null);
    setErrorMsg(null);
    router.replace('/employee/adaptive-assessment');
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Adaptive Competency Assessment">
      <PageContainer>
        <div className="max-w-4xl mx-auto space-y-6 pb-16">
          {/* Header & Explanation Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-[#0A0E1A] via-slate-900 to-[#0A0E1A] border border-indigo-500/25 shadow-xl space-y-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-3.5">
                <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/25 shrink-0">
                  <BrainCircuit className="w-7 h-7" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold text-white tracking-tight">
                      Adaptive Competency Assessment
                    </h1>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/25">
                      Item Response Theory (CAT)
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                    PRAGYA adapts the difficulty of questions based on your responses to estimate your demonstrated competency more precisely.
                  </p>
                </div>
              </div>

              {/* Disclaimer Notice */}
              <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-[11px] text-slate-400 max-w-xs self-start md:self-auto">
                <span className="text-cyan-400 font-semibold block mb-0.5">Assessment Scope:</span>
                &ldquo;This is an evidence-based estimate, not a statement of your absolute ability.&rdquo;
              </div>
            </div>

            {/* HOW IT WORKS 5-Step Visual */}
            <div className="pt-4 border-t border-slate-800/80 space-y-2.5">
              <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-300">
                How It Works
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-3">
                {[
                  { step: '1', title: 'Start at a suitable difficulty', desc: 'Calibrated to your prior score' },
                  { step: '2', title: 'Answer a question', desc: 'Select authoritative solution' },
                  { step: '3', title: 'PRAGYA adjusts the next difficulty', desc: 'Precision Bayesian tracking' },
                  { step: '4', title: 'Complete the assessment', desc: 'Confidence threshold reached' },
                  { step: '5', title: 'Your competency is recalibrated', desc: 'Evidence updated with audit trail' },
                ].map((s) => (
                  <div
                    key={s.step}
                    className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1 hover:border-indigo-500/30 transition"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center justify-center font-mono text-[10px] font-bold shrink-0">
                        {s.step}
                      </span>
                      <span className="text-xs font-semibold text-slate-200 line-clamp-1">{s.title}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 pl-7 leading-snug">{s.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {errorMsg && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* ========================================================================= */}
          {/* VIEW 1: RECALIBRATION RESULT VIEW */}
          {/* ========================================================================= */}
          {recalibrationResult ? (
            <div className="space-y-6 animate-in fade-in duration-300">
              {/* Header */}
              <div className="flex items-center justify-between">
                <button
                  onClick={handleReset}
                  className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-medium transition"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Assess Another Competency</span>
                </button>
                <div className="flex items-center gap-2">
                  <Link
                    href="/employee/gaps"
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-violet-600/20 hover:bg-violet-600/30 text-violet-300 border border-violet-500/30 text-xs font-medium transition"
                  >
                    <Target className="w-3.5 h-3.5" />
                    <span>View Skill Gaps</span>
                  </Link>
                  <Link
                    href="/employee/competency"
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-medium transition"
                  >
                    <Award className="w-3.5 h-3.5" />
                    <span>View Competency Profile</span>
                  </Link>
                </div>
              </div>

              {/* Main Recalibration Card */}
              <div className="p-6 rounded-2xl bg-[#0A0E1A]/95 border border-indigo-500/30 shadow-2xl space-y-6 backdrop-blur-md">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
                  <div>
                    <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider font-semibold mb-1">
                      Recalibration Result & Auditable Evidence
                    </div>
                    <h1 className="text-xl font-bold text-white tracking-tight">
                      {recalibrationResult.competency_name}
                    </h1>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Audited & Recalibrated
                    </span>
                  </div>
                </div>

                {/* Score Transformation Display */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
                  {/* Previous Demonstrated Score */}
                  <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                      Previous Demonstrated Score
                    </div>
                    <div className="text-xl font-bold text-slate-300 font-mono">
                      {recalibrationResult.previous_score.toFixed(1)}
                      <span className="text-xs text-slate-500 font-normal"> / 100</span>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">Prior validated evidence</div>
                  </div>

                  {/* Assessment Evidence Score */}
                  <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                    <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1">
                      Assessment Evidence Score
                    </div>
                    <div className="text-xl font-bold text-indigo-300 font-mono">
                      {recalibrationResult.assessment_score.toFixed(1)}
                      <span className="text-xs text-slate-500 font-normal"> / 100</span>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      {recalibrationResult.correct_count} / {recalibrationResult.questions_answered} correct
                    </div>
                  </div>

                  {/* Recalibrated Score */}
                  <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/40 to-slate-900 border border-cyan-500/40 shadow-inner">
                    <div className="text-[10px] font-bold text-cyan-300 uppercase tracking-wider mb-1 flex items-center justify-between">
                      <span>Recalibrated Score</span>
                    </div>
                    <div className="text-xl font-bold text-cyan-200 font-mono">
                      {recalibrationResult.recalibrated_score.toFixed(1)}
                      <span className="text-xs text-cyan-500/70 font-normal"> / 100</span>
                    </div>
                    <div className="text-[10px] text-cyan-400 mt-1">Evidence aggregation</div>
                  </div>

                  {/* Score Change */}
                  <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                    <div className="text-[10px] font-bold text-amber-400 uppercase tracking-wider mb-1">
                      Score Change (Δ)
                    </div>
                    <div className={`text-xl font-bold font-mono ${recalibrationResult.delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {recalibrationResult.delta >= 0 ? `+${recalibrationResult.delta.toFixed(1)}` : recalibrationResult.delta.toFixed(1)} pts
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">Recalibration delta</div>
                  </div>

                  {/* Confidence */}
                  <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                      Confidence
                    </div>
                    <div className="text-xl font-bold text-emerald-400 font-mono">
                      {(recalibrationResult.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      Evidence coverage
                    </div>
                  </div>
                </div>

                {/* Downstream Impact: UPDATED COMPETENCY, UPDATED SKILL GAP, UPDATED PRIORITY */}
                <div className="p-5 rounded-xl bg-gradient-to-r from-violet-950/30 via-slate-900 to-indigo-950/30 border border-violet-500/30 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-bold text-violet-300 uppercase tracking-wider">
                      <Target className="w-4 h-4 text-violet-400" />
                      <span>Updated Competency & Skill Gap Recalibration</span>
                    </div>
                    <span className="text-[10px] font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                      Closed-Loop Synced
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                    {/* UPDATED COMPETENCY */}
                    <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                      <div className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                        UPDATED COMPETENCY
                      </div>
                      <div className="text-sm font-bold text-white truncate" title={recalibrationResult.competency_name}>
                        {recalibrationResult.competency_name}
                      </div>
                      <div className="text-[11px] font-mono text-cyan-300">
                        Score: {recalibrationResult.recalibrated_score.toFixed(1)} / 100
                      </div>
                    </div>

                    {/* UPDATED SKILL GAP */}
                    <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                      <div className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                        UPDATED SKILL GAP
                      </div>
                      <div className="text-sm font-bold font-mono text-amber-400">
                        {recalibrationResult.updated_gap_score !== null && recalibrationResult.updated_gap_score !== undefined
                          ? recalibrationResult.updated_gap_score <= 0
                            ? '0.0 pts (Requirement Met)'
                            : `${recalibrationResult.updated_gap_score.toFixed(1)} pts`
                          : 'Synchronized'}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Deficit against required role level
                      </div>
                    </div>

                    {/* UPDATED PRIORITY */}
                    <div className="p-3.5 rounded-lg bg-slate-900/70 border border-slate-800 space-y-1">
                      <div className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                        UPDATED PRIORITY
                      </div>
                      <div className="text-sm font-bold font-mono text-violet-300">
                        {recalibrationResult.updated_priority_level || 'STANDARD'}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Priority Score: {recalibrationResult.updated_priority_score?.toFixed(1) || '0.0'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Audit & Explainability Note */}
                <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 space-y-2">
                  <div className="flex items-center gap-2 font-semibold text-cyan-400">
                    <HelpCircle className="w-4 h-4" />
                    <span>Evidence-Based Recalibration Methodology</span>
                  </div>
                  <p className="leading-relaxed text-slate-300">
                    &ldquo;Your demonstrated competency was recalibrated using the new assessment evidence while retaining previous validated evidence.&rdquo;
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Reason: {recalibrationResult.reason}
                  </p>
                </div>
              </div>
            </div>
          ) : !sessionId ? (
            /* ========================================================================= */
            /* VIEW 2: LAUNCH & TARGET COMPETENCY SELECTION */
            /* ========================================================================= */
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-[#0A0E1A]/95 border border-indigo-500/20 shadow-xl space-y-6">
                <div>
                  <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider font-semibold mb-1">
                    Select Target Competency
                  </div>
                  <h2 className="text-xl font-bold text-white tracking-tight">
                    Reassess Competency Level
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    PRAGYA adapts the difficulty of questions based on your responses to estimate your demonstrated competency more precisely.
                  </p>
                </div>

                {/* Competency Picker */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">
                    Target Competency:
                  </label>
                  <select
                    value={selectedCompetencyId}
                    onChange={(e) => setSelectedCompetencyId(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="">-- Choose Competency to Reassess --</option>
                    {competenciesData?.items.map((comp) => {
                      const gap = skillGaps.find((g) => g.competency_id === comp.id);
                      return (
                        <option key={comp.id} value={comp.id}>
                          {comp.code} - {comp.name} {gap && gap.gap_score > 0 ? `(Gap: ${gap.gap_score} pts)` : ''}
                        </option>
                      );
                    })}
                  </select>
                </div>

                {/* Active Competency Details Preview: SHOW CURRENT CONTEXT */}
                {selectedCompetency && (
                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-xs font-semibold text-slate-200">
                          {selectedCompetency.name}
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono">
                          {selectedCompetency.code} • {selectedCompetency.domain_name}
                        </div>
                      </div>
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                        {targetEmpCompetency ? `Score: ${targetEmpCompetency.current_score.toFixed(1)}/100` : 'No Prior Score'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 text-[10px] uppercase font-bold block">Current Competency</span>
                        <span className="font-semibold text-slate-200 truncate block" title={selectedCompetency.name}>
                          {selectedCompetency.name}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 text-[10px] uppercase font-bold block">Current Score</span>
                        <span className="font-semibold text-cyan-300 font-mono">
                          {targetEmpCompetency ? `${targetEmpCompetency.current_score.toFixed(1)} / 100` : '0.0 / 100'}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 text-[10px] uppercase font-bold block">Required Level</span>
                        <span className="font-semibold text-slate-200">
                          {targetSkillGap ? targetSkillGap.required_level_name : 'Level 2 - Applied'}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 text-[10px] uppercase font-bold block">Skill Gap</span>
                        <span className={`font-semibold ${targetSkillGap && targetSkillGap.gap_score > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                          {targetSkillGap && targetSkillGap.gap_score > 0 ? `${targetSkillGap.gap_score} pts` : '0 pts (Met)'}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 text-[10px] uppercase font-bold block">Priority</span>
                        <span className="font-semibold text-violet-300">
                          {targetSkillGap?.priority_level || 'STANDARD'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Start Button */}
                <button
                  onClick={handleStartAssessment}
                  disabled={!selectedCompetencyId || createSessionMutation.isPending || isLoadingQuestion}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-50 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-900/40 transition"
                >
                  {createSessionMutation.isPending || isLoadingQuestion ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Initializing Adaptive Engine...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>{selectedCompetency ? `Reassess ${selectedCompetency.name}` : 'Start Adaptive Assessment'}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            /* ========================================================================= */
            /* VIEW 3: ACTIVE ADAPTIVE ASSESSMENT RUNNER */
            /* ========================================================================= */
            <div className="space-y-6">
              {/* Session Progress Header */}
              <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-cyan-400 font-semibold">
                      Target Competency
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-violet-500/10 text-violet-300 border border-violet-500/25">
                      {feedback ? 'Response Evaluated' : 'Assessment In Progress'}
                    </span>
                  </div>
                  <div className="text-sm font-bold text-white">
                    {sessionData?.competency_name || selectedCompetency?.name || 'Competency Reassessment'}
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                  {/* Current Difficulty Badge */}
                  {currentQuestion && (
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border ${
                        currentQuestion.difficulty === 'ADVANCED'
                          ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                          : currentQuestion.difficulty === 'INTERMEDIATE'
                          ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                      }`}
                    >
                      {currentQuestion.difficulty} Level
                    </span>
                  )}

                  {/* Question Count Progress */}
                  {(currentQuestion || feedback) && (
                    <span className="px-3 py-1 rounded-full text-xs font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                      Question {sessionData ? sessionData.question_count + (feedback ? 0 : 1) : 1} of 15
                    </span>
                  )}

                  {/* Confidence */}
                  {sessionData && (currentQuestion || feedback || sessionData.question_count > 0) && (
                    <span className="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                      Confidence: {(sessionData.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>

              {isLoadingQuestion ? (
                <div className="p-12 rounded-2xl bg-[#0A0E1A]/95 border border-slate-800 flex flex-col items-center justify-center space-y-3">
                  <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                  <span className="text-xs text-slate-400">Selecting next calibrated question...</span>
                </div>
              ) : currentQuestion ? (
                /* Question Card */
                <div className="p-6 rounded-2xl bg-[#0A0E1A]/95 border border-indigo-500/20 shadow-xl space-y-6">
                  <div className="space-y-2">
                    <div className="text-base font-semibold text-slate-100 leading-relaxed">
                      {currentQuestion.question_text}
                    </div>

                    {currentQuestion.source_document_title && (
                      <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Source: {currentQuestion.source_document_title}</span>
                        {currentQuestion.source_page_number && (
                          <span>(Page {currentQuestion.source_page_number})</span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Options List */}
                  <div className="space-y-3">
                    {currentQuestion.options.map((opt, idx) => {
                      const isSelected = selectedOptionId === opt.id;
                      const letter = String.fromCharCode(65 + idx);

                      let optionStyle =
                        'bg-slate-900/70 border-slate-800 hover:border-slate-700 text-slate-300';

                      if (feedback) {
                        if (opt.id === feedback.correct_option_id) {
                          optionStyle =
                            'bg-emerald-500/15 border-emerald-500/40 text-emerald-200';
                        } else if (isSelected && !feedback.is_correct) {
                          optionStyle =
                            'bg-rose-500/15 border-rose-500/40 text-rose-200';
                        } else {
                          optionStyle = 'bg-slate-900/30 border-slate-800/40 text-slate-500 opacity-60';
                        }
                      } else if (isSelected) {
                        optionStyle =
                          'bg-indigo-500/15 border-indigo-500/50 text-indigo-200 shadow-sm';
                      }

                      return (
                        <button
                          key={opt.id}
                          onClick={() => !feedback && setSelectedOptionId(opt.id)}
                          disabled={Boolean(feedback)}
                          className={`w-full p-3.5 rounded-xl border text-left text-xs transition flex items-center gap-3 ${optionStyle}`}
                        >
                          <span
                            className={`w-6 h-6 rounded-lg flex items-center justify-center font-mono font-bold text-xs ${
                              isSelected
                                ? 'bg-indigo-600 text-white'
                                : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {letter}
                          </span>
                          <span className="flex-1">{opt.option_text}</span>

                          {feedback && opt.id === feedback.correct_option_id && (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                          )}
                          {feedback && isSelected && !feedback.is_correct && (
                            <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Feedback / Evaluation Section */}
                  {feedback && (
                    <div
                      className={`p-4 rounded-xl border text-xs space-y-2 ${
                        feedback.is_correct
                          ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                          : 'bg-rose-950/20 border-rose-500/30 text-rose-300'
                      }`}
                    >
                      <div className="flex items-center gap-2 font-semibold">
                        {feedback.is_correct ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span>Correct Response</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 text-rose-400" />
                            <span>Incorrect Response</span>
                          </>
                        )}
                      </div>
                      <p className="leading-relaxed text-slate-300">
                        {feedback.explanation}
                      </p>
                    </div>
                  )}

                  {/* Bottom Action Buttons */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                    <div className="text-[11px] text-slate-500">
                      {feedback?.stop_reason ? (
                        <span className="text-amber-400">{feedback.stop_reason}</span>
                      ) : sessionData && sessionData.question_count < 5 ? (
                        <span>Minimum questions: {5 - sessionData.question_count} more required</span>
                      ) : (
                        <span>Sufficient evidence collected to recalibrate</span>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      {!feedback ? (
                        <button
                          onClick={handleSubmitAnswer}
                          disabled={!selectedOptionId || submitAnswerMutation.isPending}
                          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs flex items-center gap-2 transition"
                        >
                          {submitAnswerMutation.isPending ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              <span>Evaluating...</span>
                            </>
                          ) : (
                            <span>Submit Answer</span>
                          )}
                        </button>
                      ) : feedback.should_stop ? (
                        <button
                          onClick={handleCompleteSession}
                          disabled={completeSessionMutation.isPending}
                          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-cyan-500 hover:from-cyan-500 hover:to-cyan-400 text-white font-semibold text-xs flex items-center gap-2 transition shadow-lg shadow-cyan-900/40"
                        >
                          {completeSessionMutation.isPending ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              <span>Recalibrating Competency...</span>
                            </>
                          ) : (
                            <>
                              <ShieldCheck className="w-4 h-4" />
                              <span>Complete & Recalibrate</span>
                            </>
                          )}
                        </button>
                      ) : (
                        <div className="flex items-center gap-2">
                          {feedback.can_complete && (
                            <button
                              onClick={handleCompleteSession}
                              disabled={completeSessionMutation.isPending}
                              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
                            >
                              <span>Finish Now</span>
                            </button>
                          )}
                          <button
                            onClick={handleNextQuestion}
                            disabled={isLoadingQuestion}
                            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-2 transition"
                          >
                            <span>Next Question</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 rounded-2xl bg-[#0A0E1A]/95 border border-slate-800 text-center space-y-4">
                  {(sessionData?.question_count || 0) >= 5 ? (
                    <>
                      <div className="flex items-center justify-center gap-2 text-emerald-400 text-xs font-semibold">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Sufficient Evidence Gathered ({sessionData?.question_count} Questions Completed)</span>
                      </div>
                      <p className="text-xs text-slate-400">
                        Item Response Theory model has established sufficient statistical confidence for competency estimation.
                      </p>
                      <button
                        onClick={handleCompleteSession}
                        disabled={completeSessionMutation.isPending}
                        className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs inline-flex items-center gap-2 transition shadow-lg shadow-cyan-950/40"
                      >
                        {completeSessionMutation.isPending ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Recalibrating...</span>
                          </>
                        ) : (
                          <>
                            <ShieldCheck className="w-4 h-4" />
                            <span>Complete Assessment</span>
                          </>
                        )}
                      </button>
                    </>
                  ) : (sessionData?.question_count || 0) > 0 ? (
                    <>
                      <div className="text-xs text-amber-400 font-medium">
                        No further questions available for this competency.
                      </div>
                      <p className="text-xs text-slate-400">
                        You have answered {sessionData?.question_count} questions. Finalize assessment to record available evidence.
                      </p>
                      <button
                        onClick={handleCompleteSession}
                        disabled={completeSessionMutation.isPending}
                        className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs inline-flex items-center gap-2 transition"
                      >
                        {completeSessionMutation.isPending ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Recalibrating...</span>
                          </>
                        ) : (
                          <>
                            <ShieldCheck className="w-4 h-4" />
                            <span>Finalize Assessment</span>
                          </>
                        )}
                      </button>
                    </>
                  ) : (
                    <>
                      <div className="text-xs text-rose-400 font-medium">
                        No questions available for this competency.
                      </div>
                      <p className="text-xs text-slate-400">
                        Please choose another competency to assess or upload supporting learning materials.
                      </p>
                      <button
                        onClick={handleReset}
                        className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs inline-flex items-center gap-2 transition"
                      >
                        <ArrowLeft className="w-4 h-4" />
                        <span>Select Another Competency</span>
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </PageContainer>
    </AppShell>
  );
}

export default function AdaptiveAssessmentPage() {
  return (
    <Suspense
      fallback={
        <AppShell role="EMPLOYEE" pageTitle="Adaptive Competency Assessment">
          <PageContainer>
            <div className="flex items-center justify-center min-h-[50vh]">
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            </div>
          </PageContainer>
        </AppShell>
      }
    >
      <AdaptiveAssessmentContent />
    </Suspense>
  );
}
