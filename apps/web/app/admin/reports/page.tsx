'use client';

import React, { useState } from 'react';
import {
  FileText,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Building2,
  TrendingUp,
  BrainCircuit,
  GraduationCap,
  Users,
  Target,
  Sparkles,
  Loader2,
  Clock,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { Badge } from '@/components/ui/badge';
import { downloadAdminReport } from '@/lib/api-client';
import { useAdminEmployeeList } from '@/hooks/use-admin-workforce';

interface ReportCardConfig {
  id: string;
  title: string;
  category: string;
  description: string;
  scope: string;
  primaryTable: string;
  pdfEndpoint: string;
  pdfFilename: string;
  xlsxEndpoint: string;
  xlsxFilename: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor: string;
}

const REPORT_DEFINITIONS: ReportCardConfig[] = [
  {
    id: 'executive-summary',
    title: 'Executive Workforce & Capacity Summary',
    category: 'Executive Reports',
    description:
      'High-level statutory audit brief synthesizing active cadre strength, average competency proficiency, role readiness, and projected capacity shortfalls.',
    scope: 'National Statistical Cadre (Consolidated)',
    primaryTable: 'employees, departments, job_roles, skill_gaps, course_progress',
    pdfEndpoint: '/api/v1/admin/reports/executive-summary.pdf',
    pdfFilename: 'PRAGYA_Executive_Summary.pdf',
    xlsxEndpoint: '/api/v1/admin/reports/executive-summary.xlsx',
    xlsxFilename: 'PRAGYA_Executive_Summary.xlsx',
    icon: ShieldCheck,
    accentColor: 'text-violet-400 bg-violet-500/10 border-violet-500/30',
  },
  {
    id: 'workforce-competency',
    title: 'Workforce Competency Distribution Audit',
    category: 'Workforce Reports',
    description:
      'Granular distribution of evaluated proficiency scores across statistical, mathematical, technical, and digital governance competency domains.',
    scope: 'Evaluated Cadre across all Domains',
    primaryTable: 'employee_competencies, competencies, competency_domains',
    pdfEndpoint: '/api/v1/admin/reports/workforce.pdf',
    pdfFilename: 'PRAGYA_Workforce_Competency_Report.pdf',
    xlsxEndpoint: '/api/v1/admin/reports/workforce.xlsx',
    xlsxFilename: 'PRAGYA_Workforce_Competency_Report.xlsx',
    icon: Building2,
    accentColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
  },
  {
    id: 'skill-gaps',
    title: 'National Cadre Skill Gap Analysis',
    category: 'Competency Reports',
    description:
      'Audit of identified proficiency shortfalls against mandatory role benchmarks, prioritizing critical severity deficits and affected officer populations.',
    scope: 'Identified Skill Shortfalls (Gap > 0)',
    primaryTable: 'skill_gaps, competency_requirements, job_roles',
    pdfEndpoint: '/api/v1/admin/reports/skill-gaps.pdf',
    pdfFilename: 'PRAGYA_Skill_Gaps_Report.pdf',
    xlsxEndpoint: '/api/v1/admin/reports/skill-gaps.xlsx',
    xlsxFilename: 'PRAGYA_Skill_Gaps_Report.xlsx',
    icon: Target,
    accentColor: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  },
  {
    id: 'training-effectiveness',
    title: 'Training Effectiveness & Longitudinal Gains',
    category: 'Training Reports',
    description:
      'Longitudinal analysis of course completion rates, measurable post-training competency score deltas, and recommendation funnel conversion.',
    scope: 'Course Enrollments & Completed Modules',
    primaryTable: 'course_progress, competency_recalibrations, learning_recommendations',
    pdfEndpoint: '/api/v1/admin/reports/training-effectiveness.pdf',
    pdfFilename: 'PRAGYA_Training_Effectiveness_Report.pdf',
    xlsxEndpoint: '/api/v1/admin/reports/training-effectiveness.xlsx',
    xlsxFilename: 'PRAGYA_Training_Effectiveness_Report.xlsx',
    icon: GraduationCap,
    accentColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  },
  {
    id: 'emerging-skills',
    title: 'Emerging Skills & Technology Horizon Scanning',
    category: 'Emerging Skill Reports',
    description:
      'Deterministic demand signal scoring identifying high-velocity capabilities from gap frequency, recommendation velocity, and role requirements.',
    scope: 'All 33 Statistical Competencies',
    primaryTable: 'competencies, skill_gaps, recommendations, courses',
    pdfEndpoint: '/api/v1/admin/reports/emerging-skills.pdf',
    pdfFilename: 'PRAGYA_Emerging_Skills_Report.pdf',
    xlsxEndpoint: '/api/v1/admin/reports/emerging-skills.xlsx',
    xlsxFilename: 'PRAGYA_Emerging_Skills_Report.xlsx',
    icon: BrainCircuit,
    accentColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  },
  {
    id: 'workforce-planning',
    title: 'Workforce Capacity Forecast & Planning Audit',
    category: 'Planning Reports',
    description:
      'Projected capacity shortfalls and deterministic planning pressure indicators across competencies, cadres, and operational divisions.',
    scope: 'Projected Capacity Requirements',
    primaryTable: 'employees, skill_gaps, job_roles, departments',
    pdfEndpoint: '/api/v1/admin/reports/planning.pdf',
    pdfFilename: 'PRAGYA_Workforce_Planning_Report.pdf',
    xlsxEndpoint: '/api/v1/admin/reports/planning.xlsx',
    xlsxFilename: 'PRAGYA_Workforce_Planning_Report.xlsx',
    icon: TrendingUp,
    accentColor: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  },
];

export default function AdminReportsPage() {
  const { data: employeeList, isLoading: employeesLoading } = useAdminEmployeeList();
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const employees = React.useMemo(() => employeeList?.employees ?? [], [employeeList]);
  const effectiveEmployeeId = selectedEmployeeId || (employees.length > 0 ? employees[0].id : '');

  const handleExport = async (endpoint: string, filename: string, actionId: string) => {
    setLoadingAction(actionId);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      await downloadAdminReport(endpoint, filename);
      setSuccessMsg(`Successfully generated and downloaded: ${filename}`);
      setTimeout(() => setSuccessMsg(null), 5000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Report generation failed. Please try again.';
      setErrorMsg(msg);
    } finally {
      setLoadingAction(null);
    }
  };

  const selectedOfficer = employees.find((e) => e.id === effectiveEmployeeId);

  return (
    <AppShell role="ADMIN" pageTitle="Report Center">
      <PageContainer>
        {/* HEADER */}
        <PageHeader
          title="Official Reporting & Audit Compliance Export"
          subtitle="Generate deterministic statutory workforce intelligence dossiers, audit tables, and capacity benchmarks in PDF and Excel formats."
          badge={
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-mono">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Stage 18 Statutory Export Verified</span>
            </div>
          }
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Official Reports' },
          ]}
        />

        {/* FEEDBACK BANNERS */}
        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-xs animate-in fade-in">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-rose-200">Export Error</div>
              <p>{errorMsg}</p>
            </div>
          </div>
        )}

        {successMsg && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3 text-emerald-300 text-xs animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-emerald-200">Export Complete</div>
              <p>{successMsg}</p>
            </div>
          </div>
        )}

        {/* STATUTORY GOVERNANCE & AUDIT ASSURANCES */}
        <GlassCard variant="elevated" className="p-5 mb-8 border-cyan-500/20 bg-cyan-950/20">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 shrink-0">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm font-bold text-white flex items-center gap-2">
                  <span>Deterministic Audit Traceability Standard</span>
                  <Badge variant="outline" className="text-[10px] text-cyan-300 border-cyan-500/40 font-mono">
                    MoSPI OSS Standard
                  </Badge>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">
                  All reports are generated directly from authoritative PostgreSQL records with explicit calculation methodologies. Zero synthetic or unverified external figures applied.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono text-slate-400 shrink-0">
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>Live Database State</span>
              </div>
              <div className="flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-emerald-400" />
                <span>Standard A4 / OpenXML</span>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* CADRE-WIDE REPORT DOSSIERS */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Cadre Intelligence & Statutory Reports</h2>
              <p className="text-xs text-slate-400">Standardized dossiers for parliamentary committees, ministry audits, and strategic cadre reviews.</p>
            </div>
            <span className="text-xs font-mono text-slate-500">6 Core Statutory Reports</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {REPORT_DEFINITIONS.map((rep) => {
              const IconComp = rep.icon;
              const isPdfLoading = loadingAction === `${rep.id}-pdf`;
              const isXlsxLoading = loadingAction === `${rep.id}-xlsx`;

              return (
                <GlassCard
                  key={rep.id}
                  variant="elevated"
                  className="p-5 flex flex-col justify-between hover:border-slate-700/80 transition-all group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                        {rep.category}
                      </span>
                      <div className={`p-1.5 rounded-lg border ${rep.accentColor}`}>
                        <IconComp className="w-4 h-4" />
                      </div>
                    </div>

                    <div>
                      <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                        {rep.title}
                      </h3>
                      <p className="text-xs text-slate-300 mt-1.5 leading-relaxed line-clamp-3">
                        {rep.description}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-white/5 space-y-1.5">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-400 font-mono">Scope:</span>
                        <span className="text-slate-200 font-medium truncate max-w-[200px]">{rep.scope}</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-400 font-mono">Source Tables:</span>
                        <span className="text-cyan-300/90 font-mono text-[10px] truncate max-w-[180px]">
                          {rep.primaryTable}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2.5 pt-5 mt-4 border-t border-white/5">
                    <button
                      type="button"
                      disabled={loadingAction !== null}
                      onClick={() => handleExport(rep.pdfEndpoint, rep.pdfFilename, `${rep.id}-pdf`)}
                      className="py-2 px-3 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isPdfLoading ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-rose-400" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <FileText className="w-3.5 h-3.5 text-rose-400" />
                          <span>Generate PDF</span>
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      disabled={loadingAction !== null}
                      onClick={() => handleExport(rep.xlsxEndpoint, rep.xlsxFilename, `${rep.id}-xlsx`)}
                      className="py-2 px-3 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isXlsxLoading ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-emerald-400" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Generate Excel</span>
                        </>
                      )}
                    </button>
                  </div>
                </GlassCard>
              );
            })}
          </div>
        </div>

        {/* INDIVIDUAL OFFICER COMPETENCY REPORT EXPORT */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Individual Officer Competency Dossier</h2>
              <p className="text-xs text-slate-400">Generate confidential individual assessment history, competency scores, active gaps, and learning interventions.</p>
            </div>
            <span className="text-xs font-mono text-slate-500">Officer Drilldown Export</span>
          </div>

          <GlassCard variant="elevated" className="p-6 border-slate-700/60">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
              <div className="lg:col-span-2 space-y-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-blue-500/15 border border-blue-500/30 text-blue-300">
                    <Users className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Statistical Officer Profile Dossier</h3>
                    <p className="text-xs text-slate-300">
                      Auditable individual dossier detailing current competency evaluations, longitudinal trajectory, and personalized recommendations.
                    </p>
                  </div>
                </div>

                <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                  <div className="flex-1">
                    <label className="block text-[11px] font-mono text-slate-400 mb-1">
                      SELECT CADRE OFFICER FOR EXPORT:
                    </label>
                    <select
                      value={effectiveEmployeeId}
                      onChange={(e) => setSelectedEmployeeId(e.target.value)}
                      disabled={employeesLoading || employees.length === 0}
                      className="w-full py-2 px-3 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500 font-sans"
                    >
                      {employeesLoading ? (
                        <option>Loading officers...</option>
                      ) : employees.length > 0 ? (
                        employees.map((emp) => (
                          <option key={emp.id} value={emp.id}>
                            {emp.full_name} ({emp.employee_code || emp.designation || 'Officer'})
                          </option>
                        ))
                      ) : (
                        <option>No officers recorded</option>
                      )}
                    </select>
                  </div>

                  {selectedOfficer && (
                    <div className="p-3 rounded-lg bg-white/5 border border-white/10 text-xs shrink-0 sm:self-end">
                      <div className="text-slate-400 font-mono text-[10px]">SELECTED OFFICER:</div>
                      <div className="font-semibold text-cyan-300">{selectedOfficer.full_name}</div>
                      <div className="text-[10px] text-slate-400">{selectedOfficer.role_name} • {selectedOfficer.department_name}</div>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-3 lg:border-l lg:border-white/5 lg:pl-6">
                <button
                  type="button"
                  disabled={!effectiveEmployeeId || loadingAction !== null}
                  onClick={() => {
                    const fname = `PRAGYA_Officer_${selectedOfficer?.full_name.replace(/\s+/g, '_') || 'Report'}.pdf`;
                    handleExport(
                      `/api/v1/admin/reports/employee/${effectiveEmployeeId}.pdf`,
                      fname,
                      'emp-pdf'
                    );
                  }}
                  className="w-full py-2.5 px-4 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-200 text-xs font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingAction === 'emp-pdf' ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-rose-400" />
                      <span>Generating Officer PDF...</span>
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4 text-rose-400" />
                      <span>Export Officer PDF</span>
                    </>
                  )}
                </button>

                <button
                  type="button"
                  disabled={!effectiveEmployeeId || loadingAction !== null}
                  onClick={() => {
                    const fname = `PRAGYA_Officer_${selectedOfficer?.full_name.replace(/\s+/g, '_') || 'Report'}.xlsx`;
                    handleExport(
                      `/api/v1/admin/reports/employee/${effectiveEmployeeId}.xlsx`,
                      fname,
                      'emp-xlsx'
                    );
                  }}
                  className="w-full py-2.5 px-4 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-200 text-xs font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingAction === 'emp-xlsx' ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
                      <span>Generating Officer Excel...</span>
                    </>
                  ) : (
                    <>
                      <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                      <span>Export Officer Excel</span>
                    </>
                  )}
                </button>

                <div className="text-[10px] text-slate-500 text-center font-mono">
                  Enforces strict administrator role verification
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </PageContainer>
    </AppShell>
  );
}
