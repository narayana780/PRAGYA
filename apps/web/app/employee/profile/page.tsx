'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Building2,
  Briefcase,
  GraduationCap,
  Compass,
  Globe,
  Award,
  Calendar,
  Clock,
  CheckCircle2,
  ArrowRight,
  Edit3,
  ShieldCheck,
  AlertTriangle,
  RotateCw,
  ExternalLink,
  BookOpen,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee, useEmployeeTrainingHistory } from '@/hooks/use-employee';
import { EditProfileModal } from '@/components/profile/edit-profile-modal';

export default function EmployeeProfilePage() {
  const {
    data: employee,
    isLoading: employeeLoading,
    isError: employeeError,
    error: employeeErrorObj,
    refetch: refetchEmployee,
  } = useCurrentEmployee();

  const {
    data: trainingHistory = [],
    isLoading: trainingLoading,
    refetch: refetchTraining,
  } = useEmployeeTrainingHistory(employee?.id);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // Deterministic profile completeness calculation
  const calculateCompleteness = () => {
    if (!employee) return { score: 0, items: [] };
    const checks = [
      { label: 'Cadre Identity & Designation', completed: Boolean(employee.designation), weight: 15 },
      { label: 'Official Department Affiliation', completed: Boolean(employee.department_id), weight: 15 },
      { label: 'Current Assignment & Posting', completed: Boolean(employee.current_assignment), weight: 15 },
      { label: 'Highest Education Qualification', completed: Boolean(employee.education), weight: 15 },
      { label: 'Service Experience Recorded', completed: employee.experience_years > 0, weight: 10 },
      { label: 'Official Language Preference', completed: Boolean(employee.preferred_language), weight: 10 },
      { label: 'Target Cadre Role Defined', completed: Boolean(employee.target_role_id), weight: 10 },
      { label: 'Verified Training History on Record', completed: trainingHistory.length > 0, weight: 10 },
    ];
    const score = checks.reduce((acc, c) => acc + (c.completed ? c.weight : 0), 0);
    return { score, items: checks };
  };

  const { score: completenessScore, items: completenessItems } = calculateCompleteness();

  if (employeeLoading) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="My Profile">
        <PageContainer>
          <div className="space-y-6 animate-pulse">
            <div className="h-8 w-64 bg-slate-800 rounded-lg" />
            <div className="h-48 w-full bg-slate-900/60 border border-slate-800 rounded-2xl" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="h-64 bg-slate-900/60 border border-slate-800 rounded-2xl" />
              <div className="h-64 bg-slate-900/60 border border-slate-800 rounded-2xl" />
            </div>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  if (employeeError || !employee) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="My Profile">
        <PageContainer>
          <div className="p-8 rounded-2xl bg-rose-950/20 border border-rose-500/30 text-center max-w-lg mx-auto my-12">
            <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-slate-100 mb-2">
              Failed to Load Officer Profile
            </h2>
            <p className="text-sm text-slate-400 mb-6">
              {employeeErrorObj instanceof Error
                ? employeeErrorObj.message
                : 'Could not connect to PostgreSQL employee service. Please verify the API backend is running.'}
            </p>
            <button
              onClick={() => {
                refetchEmployee();
                refetchTraining();
              }}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 text-sm font-medium transition"
            >
              <RotateCw className="w-4 h-4" />
              Retry Connection
            </button>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  return (
    <AppShell role="EMPLOYEE" pageTitle="My Profile">
      <PageContainer>
        <PageHeader
          title="Officer Profile & Cadre Identity"
          subtitle="Official Statistical System cadre attributes, service records, and competency alignment."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'My Profile' },
          ]}
          actions={
            <button
              id="edit-profile-btn"
              onClick={() => setIsEditModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-sm font-medium shadow-lg shadow-cyan-500/20 transition"
            >
              <Edit3 className="w-4 h-4" />
              Edit Profile
            </button>
          }
        />

        <div className="space-y-6">
          {/* PROFILE HERO CARD */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0F172A] via-[#0B1220] to-[#070A13] border border-cyan-500/20 p-6 md:p-8 shadow-xl"
          >
            {/* Background ambient lighting */}
            <div className="pointer-events-none absolute -top-24 -right-24 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl" />
            <div className="pointer-events-none absolute -bottom-24 -left-24 w-72 h-72 bg-violet-500/10 rounded-full blur-3xl" />

            <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex items-start md:items-center gap-5">
                {/* Avatar with Status Glow */}
                <div className="relative shrink-0">
                  <div className="w-20 h-20 md:w-24 md:h-24 rounded-2xl bg-gradient-to-tr from-cyan-500/30 to-violet-500/30 border-2 border-cyan-400/40 p-1 flex items-center justify-center overflow-hidden shadow-inner">
                    {employee.profile_image_url ? (
                      <img
                        src={employee.profile_image_url}
                        alt={employee.full_name}
                        className="w-full h-full object-cover rounded-xl"
                      />
                    ) : (
                      <User className="w-10 h-10 text-cyan-400" />
                    )}
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-[#0F172A] flex items-center justify-center">
                    <ShieldCheck className="w-3 h-3 text-white" />
                  </div>
                </div>

                {/* Officer Details */}
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h1 className="text-2xl md:text-3xl font-bold text-slate-100 tracking-tight">
                      {employee.full_name}
                    </h1>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                      {employee.employee_code}
                    </span>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Verified Cadre
                    </span>
                  </div>

                  <p className="text-base text-cyan-200 font-medium">
                    {employee.designation}
                  </p>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1.5">
                      <Building2 className="w-4 h-4 text-cyan-400/80" />
                      {employee.department_name}
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-700" />
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-cyan-400/80" />
                      {employee.experience_years} Years Experience
                    </span>
                  </div>
                </div>
              </div>

              {/* Current Assignment Callout */}
              <div className="w-full md:w-auto p-4 rounded-xl bg-slate-900/80 border border-slate-800/90 md:min-w-[260px]">
                <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
                  Current Assignment
                </div>
                <div className="text-sm font-semibold text-slate-100">
                  {employee.current_assignment || 'General Cadre Pool'}
                </div>
                <div className="text-[11px] text-cyan-400/80 mt-0.5">
                  MoSPI Statistical Survey Division
                </div>
              </div>
            </div>
          </motion.div>

          {/* MAIN GRID: SECTION 1 TO 4 + SECTION 6 (COMPLETENESS) */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Columns: Core Cadre & Learning Attributes */}
            <div className="lg:col-span-2 space-y-6">
              {/* SECTION 1: Professional Information */}
              <div className="p-6 rounded-2xl bg-[#0F172A]/80 border border-slate-800 shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-cyan-400" />
                    Section 1: Professional Information
                  </h3>
                  <span className="text-xs font-mono text-slate-400">
                    Dept Code: {employee.department_code || 'N/A'}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <span className="text-xs text-slate-400">Cadre Designation</span>
                    <p className="text-sm font-medium text-slate-200 mt-1">
                      {employee.designation}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <span className="text-xs text-slate-400">Department / Division</span>
                    <p className="text-sm font-medium text-slate-200 mt-1">
                      {employee.department_name}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <span className="text-xs text-slate-400">Official Job Role</span>
                    <p className="text-sm font-medium text-slate-200 mt-1">
                      {employee.job_role_name} ({employee.job_role_code})
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <span className="text-xs text-slate-400">Total Statistical Experience</span>
                    <p className="text-sm font-medium text-slate-200 mt-1">
                      {employee.experience_years} Years
                    </p>
                  </div>

                  <div className="sm:col-span-2 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <span className="text-xs text-slate-400">Current Assignment</span>
                    <p className="text-sm font-medium text-slate-200 mt-1">
                      {employee.current_assignment || 'Unassigned'}
                    </p>
                  </div>
                </div>
              </div>

              {/* SECTION 2 & 4: Education & Learning Preferences (2-column layout) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* SECTION 2: Education */}
                <div className="p-6 rounded-2xl bg-[#0F172A]/80 border border-slate-800 shadow-sm space-y-4">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                    <GraduationCap className="w-4 h-4 text-violet-400" />
                    <h3 className="text-base font-semibold text-slate-100">
                      Section 2: Education
                    </h3>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start gap-3">
                    <div className="p-2.5 rounded-lg bg-violet-500/10 text-violet-400 shrink-0">
                      <BookOpen className="w-5 h-5" />
                    </div>
                    <div>
                      <span className="text-xs text-slate-400">Highest Qualification</span>
                      <p className="text-sm font-semibold text-slate-100 mt-0.5">
                        {employee.education || 'Not specified'}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Verified by Department of Economics & Statistics
                      </p>
                    </div>
                  </div>
                </div>

                {/* SECTION 4: Learning Preferences */}
                <div className="p-6 rounded-2xl bg-[#0F172A]/80 border border-slate-800 shadow-sm space-y-4">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                    <Globe className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-base font-semibold text-slate-100">
                      Section 4: Learning Preferences
                    </h3>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                    <div>
                      <span className="text-xs text-slate-400">Preferred Instructional Language</span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                          {employee.preferred_language}
                        </span>
                        <span className="text-xs text-slate-400">Supported by iGOT Karmayogi</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-400">
                      Digital coursework, assessments, and AI tutoring will default to this medium.
                    </p>
                  </div>
                </div>
              </div>

              {/* SECTION 3: Career Direction */}
              <div className="p-6 rounded-2xl bg-[#0F172A]/80 border border-slate-800 shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Compass className="w-4 h-4 text-cyan-400" />
                    Section 3: Career Direction & Cadre Progression
                  </h3>
                  <span className="text-xs text-cyan-400">MoSPI Cadre Hierarchy</span>
                </div>

                <div className="p-5 rounded-xl bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-900/90 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
                  {/* Current Role */}
                  <div className="flex-1 w-full text-center md:text-left">
                    <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">
                      Current Cadre Role
                    </span>
                    <div className="text-base font-bold text-slate-100 mt-1">
                      {employee.job_role_name}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      {employee.department_name}
                    </div>
                  </div>

                  {/* Transition Indicator */}
                  <div className="flex flex-col items-center justify-center px-4 shrink-0">
                    <div className="w-10 h-10 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-sm">
                      <ArrowRight className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] text-cyan-400/80 font-mono mt-1">
                      Promotion Track
                    </span>
                  </div>

                  {/* Target Role */}
                  <div className="flex-1 w-full text-center md:text-right">
                    <span className="text-xs text-slate-400 uppercase tracking-wider font-mono">
                      Target Role (Aspiration)
                    </span>
                    <div className="text-base font-bold text-cyan-300 mt-1">
                      {employee.target_role_name || 'Not Configured'}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      Competency Gap Analysis Target
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: SECTION 6 Profile Completeness */}
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-[#0F172A]/80 border border-slate-800 shadow-sm space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Award className="w-4 h-4 text-cyan-400" />
                    Section 6: Profile Completeness
                  </h3>
                  <span className="text-xs font-mono text-cyan-400 font-semibold">
                    {completenessScore}%
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${completenessScore}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-emerald-400 rounded-full"
                    />
                  </div>
                  <p className="text-xs text-slate-400 flex items-center justify-between">
                    <span>Deterministic Cadre Profile Metric</span>
                    <span className="text-emerald-400 font-medium">
                      {completenessScore >= 80 ? 'Ready for Assessment' : 'Needs Completion'}
                    </span>
                  </p>
                </div>

                {/* Checklist items */}
                <div className="space-y-2.5 pt-2">
                  {completenessItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-xs py-1.5 px-2.5 rounded-lg bg-slate-900/40 border border-slate-800/60"
                    >
                      <span className="text-slate-300">{item.label}</span>
                      {item.completed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <span className="text-[11px] text-amber-400 font-medium shrink-0">
                          Pending
                        </span>
                      )}
                    </div>
                  ))}
                </div>

                {completenessScore < 100 && (
                  <button
                    onClick={() => setIsEditModalOpen(true)}
                    className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition flex items-center justify-center gap-1.5"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-cyan-400" />
                    Complete Missing Attributes
                  </button>
                )}
              </div>

              {/* Ecosystem Integrity Badge */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/20 via-slate-900/50 to-slate-900/80 border border-cyan-500/20 text-xs text-slate-400 space-y-2">
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  PostgreSQL Native Record
                </div>
                <p>
                  This profile is directly synchronized with the PRAGYA PostgreSQL instance (`pragya`).
                  Changes made via Edit Profile are persisted through SQLAlchemy 2.0 and versioned FastAPI services.
                </p>
              </div>
            </div>
          </div>

          {/* SECTION 5: TRAINING HISTORY */}
          <div className="p-6 rounded-2xl bg-[#0F172A]/80 border border-slate-800 shadow-sm space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                  <GraduationCap className="w-4 h-4 text-cyan-400" />
                  Section 5: Verified Training History
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Historical and completed learning modules across iGOT Karmayogi and NSSTA Training Academy.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-mono">
                  {trainingHistory.length} Records on File
                </span>
              </div>
            </div>

            {trainingLoading ? (
              <div className="h-32 flex items-center justify-center text-xs text-slate-400 animate-pulse">
                Loading verified training records from PostgreSQL...
              </div>
            ) : trainingHistory.length === 0 ? (
              <div className="p-8 text-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400 text-xs">
                No historical training records found for this officer.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono">
                      <th className="py-3 px-4">Course / Programme</th>
                      <th className="py-3 px-4">Provider</th>
                      <th className="py-3 px-4">Type</th>
                      <th className="py-3 px-4">Completion Date</th>
                      <th className="py-3 px-4">Score</th>
                      <th className="py-3 px-4">Duration</th>
                      <th className="py-3 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {trainingHistory.map((record) => {
                      const completedDate = record.completed_at
                        ? new Date(record.completed_at).toLocaleDateString('en-IN', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          })
                        : '—';

                      return (
                        <tr key={record.id} className="hover:bg-slate-900/40 transition">
                          <td className="py-3.5 px-4">
                            <div className="font-semibold text-slate-100">{record.title}</div>
                            {record.certificate_reference && (
                              <span className="text-[10px] text-cyan-400 font-mono">
                                Ref: {record.certificate_reference}
                              </span>
                            )}
                          </td>
                          <td className="py-3.5 px-4 font-medium text-slate-300">
                            {record.provider}
                          </td>
                          <td className="py-3.5 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[11px] font-mono font-medium ${
                                record.provider_type === 'IGOT'
                                  ? 'bg-orange-500/15 text-orange-300 border border-orange-500/30'
                                  : record.provider_type === 'NSSTA_TPAC'
                                  ? 'bg-blue-500/15 text-blue-300 border border-blue-500/30'
                                  : 'bg-slate-700/40 text-slate-300 border border-slate-700'
                              }`}
                            >
                              {record.provider_type}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 whitespace-nowrap text-slate-400">
                            {completedDate}
                          </td>
                          <td className="py-3.5 px-4">
                            {record.score ? (
                              <span className="font-semibold text-emerald-400">
                                {record.score}%
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>
                          <td className="py-3.5 px-4 whitespace-nowrap text-slate-400">
                            {record.duration_hours ? `${record.duration_hours} hrs` : '—'}
                          </td>
                          <td className="py-3.5 px-4">
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                              <CheckCircle2 className="w-3 h-3" />
                              {record.status}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* EDIT PROFILE MODAL */}
        <EditProfileModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          employee={employee}
        />
      </PageContainer>
    </AppShell>
  );
}
