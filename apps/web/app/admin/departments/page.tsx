'use client';

import React, { useState, useMemo } from 'react';
import {
  Building2,
  AlertTriangle,
  Layers,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import {
  useDepartmentAnalytics,
  useDepartmentHeatmap,
  useAdminEmployeeList,
} from '@/hooks/use-admin-workforce';
import type { DepartmentAnalyticsItem } from '@pragya/types';

export default function AdminDepartmentsPage() {
  const [selectedDeptId, setSelectedDeptId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'profile' | 'heatmap'>('profile');

  const {
    data: deptData,
    isLoading: deptLoading,
    error: deptError,
    refetch: refetchDepts,
  } = useDepartmentAnalytics();

  const {
    data: heatmapData,
    isLoading: heatmapLoading,
  } = useDepartmentHeatmap();

  const {
    data: rosterData,
  } = useAdminEmployeeList();

  // Auto-select first department when data loads if none selected
  const selectedDept: DepartmentAnalyticsItem | undefined = useMemo(() => {
    if (!deptData?.departments || deptData.departments.length === 0) return undefined;
    if (selectedDeptId) {
      return deptData.departments.find((d) => d.department_id === selectedDeptId);
    }
    return deptData.departments[0];
  }, [deptData, selectedDeptId]);

  // Personnel belonging to selected department
  const deptEmployees = useMemo(() => {
    if (!rosterData?.employees || !selectedDept) return [];
    return rosterData.employees.filter(
      (e) => e.department_name.toLowerCase() === selectedDept.department_name.toLowerCase()
    );
  }, [rosterData, selectedDept]);

  // Summary counts
  const totalDivisions = deptData?.departments?.length ?? 0;
  const totalPersonnel = useMemo(() => {
    return deptData?.departments?.reduce((acc, d) => acc + d.employee_count, 0) ?? 0;
  }, [deptData]);

  const deptsWithCriticalGaps = useMemo(() => {
    return deptData?.departments?.filter((d) => d.critical_gap_count > 0).length ?? 0;
  }, [deptData]);

  return (
    <AppShell role="ADMIN" pageTitle="Department Analysis">
      <PageContainer>
        {/* HEADER */}
        <PageHeader
          title="Department-Wise Capability Analysis"
          subtitle="Skill gap heatmaps and capability readiness comparisons across NAD, FOD, CPD, and State Statistical Bureaus."
          badge={
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono">
              <Building2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>MoSPI Organizational View</span>
            </div>
          }
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Department Analysis' },
          ]}
        />

        {/* ERROR BANNER */}
        {deptError && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-rose-300 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Failed to load department analytics.</span>
            </div>
            <button
              onClick={() => refetchDepts()}
              className="px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-200 text-xs font-semibold flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* OVERVIEW CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1">TOTAL DIVISIONS</div>
            <div className="text-2xl font-bold text-white font-mono">{totalDivisions}</div>
            <div className="text-[11px] text-slate-400 mt-1">Official Org Units</div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1">DEPLOYED OFFICERS</div>
            <div className="text-2xl font-bold text-cyan-300 font-mono">{totalPersonnel}</div>
            <div className="text-[11px] text-slate-400 mt-1">Across all departments</div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1">DIVISIONS WITH GAPS</div>
            <div className="text-2xl font-bold text-rose-400 font-mono">{deptsWithCriticalGaps}</div>
            <div className="text-[11px] text-slate-400 mt-1">Requiring intervention</div>
          </GlassCard>

          <GlassCard variant="elevated" className="p-5">
            <div className="text-xs font-mono text-slate-400 mb-1">CADRE ALLOCATION</div>
            <div className="text-2xl font-bold text-emerald-400 font-mono">100%</div>
            <div className="text-[11px] text-slate-400 mt-1">Integrated with DB</div>
          </GlassCard>
        </div>

        {/* VIEW TOGGLE */}
        <div className="flex items-center gap-2 border-b border-white/10 mb-6 pb-2">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'profile'
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span>Department Profiles</span>
          </button>
          <button
            onClick={() => setActiveTab('heatmap')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === 'heatmap'
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/20'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Cross-Department Heatmap</span>
          </button>
        </div>

        {/* TAB 1: DEPARTMENT PROFILES (MASTER-DETAIL VIEW) */}
        {activeTab === 'profile' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* LEFT COLUMN: DEPARTMENT LIST */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 font-mono uppercase tracking-wider mb-2">
                Select Department ({deptData?.departments?.length ?? 0})
              </h3>
              {deptLoading ? (
                <div className="py-8 text-center text-slate-400 text-xs">Loading departments...</div>
              ) : deptData?.departments && deptData.departments.length > 0 ? (
                deptData.departments.map((dept) => {
                  const isSelected = selectedDept?.department_id === dept.department_id;
                  return (
                    <button
                      key={dept.department_id}
                      onClick={() => setSelectedDeptId(dept.department_id)}
                      className={`w-full text-left p-4 rounded-xl border transition-all ${
                        isSelected
                          ? 'bg-cyan-500/10 border-cyan-500/40 shadow-lg shadow-cyan-500/5'
                          : 'bg-white/5 border-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-bold text-white">{dept.department_name}</span>
                        <span className="text-[10px] font-mono text-cyan-400">{dept.department_code}</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                        <span>{dept.employee_count} Personnel</span>
                        <span>
                          {dept.average_competency_score !== null
                            ? `Avg: ${dept.average_competency_score.toFixed(1)} pts`
                            : 'Unassessed'}
                        </span>
                      </div>
                      {dept.critical_gap_count > 0 && (
                        <div className="mt-2 text-[10px] font-mono text-rose-300">
                          ⚠ {dept.critical_gap_count} Critical Deficit{dept.critical_gap_count > 1 ? 's' : ''}
                        </div>
                      )}
                    </button>
                  );
                })
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">No departments found.</div>
              )}
            </div>

            {/* RIGHT COLUMN: SELECTED DEPARTMENT DETAIL */}
            <div className="lg:col-span-2 space-y-6">
              {selectedDept ? (
                <>
                  {/* Department Capability Header Card */}
                  <GlassCard variant="elevated" className="p-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
                      <div>
                        <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider">
                          Department Capability Profile
                        </div>
                        <h2 className="text-xl font-bold text-white tracking-tight">
                          {selectedDept.department_name}
                        </h2>
                        <p className="text-xs text-slate-400 font-mono">{selectedDept.department_code}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold font-mono ${
                            selectedDept.critical_gap_count > 0
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          }`}
                        >
                          {selectedDept.critical_gap_count > 0
                            ? `${selectedDept.critical_gap_count} Critical Gaps`
                            : 'Cadre Ready'}
                        </span>
                      </div>
                    </div>

                    {/* Department Metric Cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-4">
                      <div className="p-3 rounded-xl bg-white/5 text-center">
                        <div className="text-[10px] text-slate-400 font-mono">STAFF STRENGTH</div>
                        <div className="text-lg font-bold text-white font-mono mt-0.5">
                          {selectedDept.employee_count}
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-center">
                        <div className="text-[10px] text-cyan-300 font-mono">AVG COMPETENCY</div>
                        <div className="text-lg font-bold text-cyan-400 font-mono mt-0.5">
                          {selectedDept.average_competency_score !== null
                            ? `${selectedDept.average_competency_score.toFixed(1)}`
                            : '—'}
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-center">
                        <div className="text-[10px] text-emerald-300 font-mono">ROLE READINESS</div>
                        <div className="text-lg font-bold text-emerald-400 font-mono mt-0.5">
                          {selectedDept.average_role_readiness !== null
                            ? `${selectedDept.average_role_readiness.toFixed(1)}%`
                            : '—'}
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-center">
                        <div className="text-[10px] text-rose-300 font-mono">CRITICAL GAPS</div>
                        <div className="text-lg font-bold text-rose-400 font-mono mt-0.5">
                          {selectedDept.critical_gap_count}
                        </div>
                      </div>
                    </div>

                    {/* Strengths & Gaps Row */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-white/5 text-xs">
                      <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                        <div className="text-[10px] font-bold text-emerald-300 uppercase font-mono mb-2">
                          Top Demonstrated Strengths
                        </div>
                        {selectedDept.top_competency_strengths.length > 0 ? (
                          <div className="space-y-1.5">
                            {selectedDept.top_competency_strengths.map((s, idx) => (
                              <div key={idx} className="text-slate-200 flex items-center gap-1.5">
                                <span className="text-emerald-400 font-bold">•</span>
                                <span>{s}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-slate-500 text-xs">No evaluated data yet.</div>
                        )}
                      </div>

                      <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20">
                        <div className="text-[10px] font-bold text-rose-300 uppercase font-mono mb-2">
                          Priority Skill Deficits
                        </div>
                        {selectedDept.top_competency_gaps.length > 0 ? (
                          <div className="space-y-1.5">
                            {selectedDept.top_competency_gaps.map((g, idx) => (
                              <div key={idx} className="text-slate-200 flex items-center gap-1.5">
                                <span className="text-rose-400 font-bold">•</span>
                                <span>{g}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-emerald-400 text-xs flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>No critical skill gaps identified.</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </GlassCard>

                  {/* Department Personnel Roster */}
                  <GlassCard variant="elevated" className="p-6">
                    <h3 className="text-sm font-bold text-white tracking-tight mb-4">
                      Department Personnel ({deptEmployees.length})
                    </h3>

                    {deptEmployees.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-xs">
                          <thead>
                            <tr className="border-b border-white/10 text-slate-400 font-mono uppercase text-[10px]">
                              <th className="py-2.5 px-3">Officer</th>
                              <th className="py-2.5 px-3">Designation</th>
                              <th className="py-2.5 px-3 text-center">Avg Score</th>
                              <th className="py-2.5 px-3 text-center">Readiness</th>
                              <th className="py-2.5 px-3 text-center">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/5">
                            {deptEmployees.map((emp) => (
                              <tr key={emp.id} className="hover:bg-white/5 transition-colors">
                                <td className="py-2.5 px-3">
                                  <div className="font-semibold text-white">{emp.full_name}</div>
                                  <div className="text-[10px] font-mono text-cyan-400">{emp.employee_code}</div>
                                </td>
                                <td className="py-2.5 px-3 text-slate-300">
                                  <div>{emp.designation}</div>
                                  <div className="text-[10px] text-slate-500 font-mono">{emp.role_name}</div>
                                </td>
                                <td className="py-2.5 px-3 text-center font-mono font-bold">
                                  {emp.average_competency !== null ? (
                                    <span className={emp.average_competency >= 70 ? 'text-emerald-300' : 'text-rose-400'}>
                                      {emp.average_competency.toFixed(1)}
                                    </span>
                                  ) : (
                                    <span className="text-slate-500">—</span>
                                  )}
                                </td>
                                <td className="py-2.5 px-3 text-center font-mono font-bold text-cyan-300">
                                  {emp.role_readiness !== null ? `${emp.role_readiness.toFixed(1)}%` : '—'}
                                </td>
                                <td className="py-2.5 px-3 text-center">
                                  {emp.needs_attention ? (
                                    <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-mono">
                                      Attention
                                    </span>
                                  ) : (
                                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px] font-mono">
                                      On Track
                                    </span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="py-8 text-center text-slate-400 text-xs">
                        No personnel currently assigned to this department.
                      </div>
                    )}
                  </GlassCard>
                </>
              ) : (
                <div className="py-16 text-center text-slate-400 text-xs">
                  Select a department from the left column to view capability details.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: FULL CROSS-DEPARTMENT HEATMAP */}
        {activeTab === 'heatmap' && (
          <GlassCard variant="elevated" className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">Cross-Department Capability Heatmap</h3>
                <p className="text-xs text-slate-400">Departmental capability comparisons across all framework competencies</p>
              </div>
            </div>

            {heatmapLoading ? (
              <div className="py-12 text-center text-slate-400 text-xs">Loading heatmap...</div>
            ) : heatmapData?.departments && heatmapData.departments.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="py-3 px-3 text-slate-400 font-mono uppercase text-[10px] min-w-[160px]">
                        Department
                      </th>
                      {heatmapData.competencies_reference.map((comp) => (
                        <th
                          key={comp.id}
                          className="py-3 px-2 text-center text-slate-300 font-mono text-[10px] min-w-[90px]"
                          title={`${comp.name} (${comp.code})`}
                        >
                          {comp.code}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {heatmapData.departments.map((dept) => (
                      <tr key={dept.department_id} className="hover:bg-white/5">
                        <td className="py-2.5 px-3 font-semibold text-white whitespace-nowrap">
                          {dept.department_name}
                        </td>
                        {dept.competencies.map((c) => {
                          const score = c.average_score;
                          let bgClass = 'bg-white/5 text-slate-500';
                          if (score !== null) {
                            if (score >= 75) {
                              bgClass = 'bg-emerald-500/30 text-emerald-200 font-semibold border border-emerald-500/40';
                            } else if (score >= 50) {
                              bgClass = 'bg-cyan-500/30 text-cyan-200 font-semibold border border-cyan-500/40';
                            } else {
                              bgClass = 'bg-rose-500/30 text-rose-200 font-semibold border border-rose-500/40';
                            }
                          }
                          return (
                            <td key={c.competency_id} className="py-2.5 px-2 text-center">
                              <div
                                className={`py-1.5 px-2 rounded font-mono text-[11px] ${bgClass}`}
                                title={`${dept.department_name} • ${c.competency_name}: ${
                                  score !== null ? `${score.toFixed(1)} pts (${c.employee_count} assessed)` : 'No Data'
                                }`}
                              >
                                {score !== null ? score.toFixed(0) : '—'}
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400 text-xs">No heatmap data recorded.</div>
            )}
          </GlassCard>
        )}
      </PageContainer>
    </AppShell>
  );
}
