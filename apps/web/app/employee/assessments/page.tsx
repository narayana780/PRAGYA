'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import {
  Play,
  Clock,
  HelpCircle,
  ShieldCheck,
  Award,
  Layers,
  Info,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useAssessments, useAssessment, useStartAttempt } from '@/hooks/use-assessment';

export default function EmployeeAssessmentsPage() {
  const router = useRouter();
  const { data: employee } = useCurrentEmployee();
  const { data: assessments = [], isLoading } = useAssessments();
  const startAttemptMutation = useStartAttempt();

  // Find the primary diagnostic assessment
  const diagnostic = assessments.find((a) => a.assessment_type === 'DIAGNOSTIC') || assessments[0];
  const { data: diagnosticDetail } = useAssessment(diagnostic?.id || null);

  const handleStartDiagnostic = async (assessmentId: string) => {
    if (!employee?.id) return;
    try {
      const attempt = await startAttemptMutation.mutateAsync({
        assessmentId,
        employeeId: employee.id,
      });
      router.push(`/employee/assessments/diagnostic?attemptId=${attempt.id}&assessmentId=${assessmentId}`);
    } catch (err) {
      console.error('Failed to initiate assessment attempt:', err);
    }
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Assessments">
      <PageContainer>
        <PageHeader
          title="Diagnostic & Competency Assessment"
          subtitle="Empirical capability evaluations designed for MoSPI cadre professionals with deterministic, psychometrically validated questions."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'Assessments' },
          ]}
        />

        <div className="space-y-8">
          {/* PRIMARY DIAGNOSTIC HERO CARD */}
          {isLoading ? (
            <div className="h-72 rounded-3xl bg-slate-900/50 border border-slate-800 animate-pulse" />
          ) : diagnostic ? (
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0B1528] via-[#08101E] to-[#040810] border border-cyan-500/30 p-8 shadow-2xl">
              {/* Subtle background glow */}
              <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

              <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8">
                <div className="space-y-4 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase bg-cyan-500/15 text-cyan-300 border border-cyan-500/40">
                      Standard Diagnostic Test
                    </span>
                    <span className="px-3 py-1 rounded-full text-[10px] font-semibold tracking-wider uppercase bg-slate-800/80 text-slate-300 border border-slate-700">
                      Primary Evidence Source (50% Weight)
                    </span>
                  </div>

                  <div>
                    <h2 className="text-2xl lg:text-3xl font-black text-slate-100 tracking-tight">
                      {diagnostic.title}
                    </h2>
                    <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                      {diagnostic.description}
                    </p>
                  </div>

                  {/* Badges / Competency Tags */}
                  <div className="pt-2">
                    <span className="text-[11px] font-mono text-slate-400 uppercase block mb-2">
                      Competencies Covered in Diagnostic:
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {(diagnosticDetail?.competencies || []).map((comp) => (
                        <span
                          key={comp.id}
                          className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-900/90 border border-slate-800 text-slate-200"
                        >
                          {comp.name}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Meta Specs */}
                  <div className="flex flex-wrap items-center gap-6 pt-2 text-xs text-slate-400 font-mono">
                    <div className="flex items-center gap-2">
                      <HelpCircle className="w-4 h-4 text-cyan-400" />
                      <span>{diagnostic.question_count} Questions</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-cyan-400" />
                      <span>{diagnostic.duration_minutes} Minutes Allowed</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      <span>Server-Authoritative Psychometrics</span>
                    </div>
                  </div>
                </div>

                {/* Launch Button Column */}
                <div className="w-full lg:w-auto flex flex-col items-center sm:items-end gap-3 shrink-0">
                  <button
                    onClick={() => handleStartDiagnostic(diagnostic.id)}
                    disabled={startAttemptMutation.isPending}
                    className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-sm tracking-wide uppercase shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-3 transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50"
                  >
                    {startAttemptMutation.isPending ? (
                      <span>Initializing Session...</span>
                    ) : (
                      <>
                        <Play className="w-5 h-5 fill-slate-950" />
                        <span>Start Assessment</span>
                      </>
                    )}
                  </button>
                  <p className="text-[11px] text-slate-500 text-center sm:text-right">
                    Responses saved incrementally on question advance
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-2xl bg-slate-900/50 border border-slate-800 text-center text-slate-400">
              No diagnostic assessments currently available.
            </div>
          )}

          {/* METHODOLOGY NOTICE */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                <Award className="w-4 h-4" />
                <span>Deterministic Scoring</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Stage 5 diagnostic evaluations use verified deterministic seed questions mapped
                directly to Official MoSPI competency descriptors. No LLM randomness is introduced.
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                <Layers className="w-4 h-4" />
                <span>Multi-Source Evidence</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Diagnostic score forms 50% of demonstrated competency. Completed training,
                cadre experience, and self-assessment contribute the remaining 50%.
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                <Info className="w-4 h-4" />
                <span>Methodology Disclaimer</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                The scoring weights and experience normalization curves implemented here represent a
                prototype methodology and are not official MoSPI scoring regulations.
              </p>
            </div>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}
