'use client';

import React, { useState, Suspense } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  Clock,
  ExternalLink,
  FileCode2,
  FileText,
  FlaskConical,
  GraduationCap,
  HelpCircle,
  Layers,
  Loader2,
  Lock,
  Sparkles,
  Target,
  Trophy,
  Video,
} from 'lucide-react';
import type { CourseModule, CourseResource } from '@pragya/types';
import { AppShell } from '@/components/layout/app-shell';
import { PageContainer } from '@/components/layout/page-container';
import { useLearningItem } from '@/hooks/use-recommendations';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useMyLabSessions } from '@/hooks/use-labs';
import {
  useCourseCurriculum,
  useCourseProgress,
  useUpdateResourceProgress,
  useSubmitKnowledgeCheck,
  useSubmitAssignment,
  useSubmitFinalAssessment,
  useCompleteCourse,
  useRecalibrateCourse,
} from '@/hooks/use-courses';
import { CourseVideoPlayer } from '@/components/learning/course-video-player';
import { CourseReadingViewer } from '@/components/learning/course-reading-viewer';
import { ExternalLearningResourceCard } from '@/components/learning/external-learning-resource-card';
import { ModuleKnowledgeCheck } from '@/components/learning/module-knowledge-check';
import { ModuleAssignment } from '@/components/learning/module-assignment';
import { CourseFinalAssessment } from '@/components/learning/course-final-assessment';
import { CourseCompletionCelebration } from '@/components/learning/course-completion-celebration';

function CoursePlayerContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const courseId = params.id as string;
  const labCompletedParam = searchParams.get('labCompleted') === 'true';

  const { data: item, isLoading: itemLoading } = useLearningItem(courseId);
  const { data: employee } = useCurrentEmployee();
  const { data: labSessions } = useMyLabSessions(employee?.id);
  const { data: curriculum } = useCourseCurriculum(courseId);
  const { data: progress } = useCourseProgress(courseId, employee?.id);

  const { mutateAsync: updateResourceProgress } = useUpdateResourceProgress(courseId, employee?.id);
  const { mutateAsync: submitKnowledgeCheck } = useSubmitKnowledgeCheck(courseId, employee?.id);
  const { mutateAsync: submitAssignment } = useSubmitAssignment(courseId, employee?.id);
  const { mutateAsync: submitFinalAssessment } = useSubmitFinalAssessment(courseId, employee?.id);
  const { mutateAsync: completeCourseAction } = useCompleteCourse(courseId, employee?.id);
  const { mutateAsync: recalibrateAction } = useRecalibrateCourse(courseId, employee?.id);

  const [activeTab, setActiveTab] = useState<'curriculum' | 'resource' | 'assignment' | 'knowledge_check' | 'final_assessment' | 'completion'>('curriculum');
  const [selectedModuleId, setSelectedModuleId] = useState<number>(1);
  const [selectedResource, setSelectedResource] = useState<CourseResource | null>(null);
  const [isFinalizing, setIsFinalizing] = useState(false);

  // Check if a linked Virtual Lab session was completed and verified
  const matchingLabSession = (labSessions || []).find((s) => s.status === 'COMPLETED' && (s.percentage ?? 0) >= 60.0);
  const isLabVerified = !!matchingLabSession || labCompletedParam || !!progress?.is_lab_verified;

  if (itemLoading || !item) {
    return (
      <AppShell role="EMPLOYEE" pageTitle="Interactive Course Player">
        <PageContainer>
          <div className="flex flex-col items-center justify-center p-24 space-y-4">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-xs text-slate-400">Loading interactive course module...</p>
          </div>
        </PageContainer>
      </AppShell>
    );
  }

  const durationHours = (item.duration_minutes / 60).toFixed(1);
  const modules = curriculum?.modules || [];
  const completedModules = progress?.completed_modules || [];
  const unlockedModules = progress?.unlocked_modules || [1];
  const progressPercent = Math.round(progress?.progress_percentage || (completedModules.length / 4) * 100);
  const canCompleteCourse =
    completedModules.includes(1) &&
    completedModules.includes(2) &&
    completedModules.includes(3) &&
    isLabVerified &&
    progress?.final_assessment_passed;

  const handleFinalizeCourse = async () => {
    setIsFinalizing(true);
    try {
      await completeCourseAction();
      setActiveTab('completion');
    } catch (e: unknown) {
      alert((e as Error)?.message || 'Cannot complete course yet. Complete all mandatory learning and practical requirements.');
    } finally {
      setIsFinalizing(false);
    }
  };

  const currentModule = modules.find((m: CourseModule) => m.id === selectedModuleId) || modules[0];

  return (
    <AppShell role="EMPLOYEE" pageTitle={`Course: ${item.title}`}>
      <PageContainer>
        <div className="space-y-6 max-w-7xl mx-auto pb-16">
          {/* Header Bar */}
          <div className="bg-[#0A0E1A]/95 border border-slate-800 p-5 rounded-2xl shadow-xl backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Link
                href={`/employee/courses/${item.id}`}
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition shrink-0"
              >
                <ChevronLeft className="w-4 h-4" />
              </Link>
              <div>
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-[10px] font-semibold">
                    <Sparkles className="w-3 h-3 text-indigo-400" />
                    <span>Learning Path: PRAGYA Demonstration</span>
                  </span>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[10px] font-semibold">
                    <span>Provider: iGOT & PRAGYA</span>
                  </span>
                  <span className="text-[11px] font-mono text-indigo-400">
                    {item.provider_item_id || 'PRAGYA-MOD'}
                  </span>
                  <span className="text-slate-600">•</span>
                  <span className="text-[11px] text-slate-400 capitalize">
                    {item.difficulty.toLowerCase()} Level
                  </span>
                </div>
                <h1 className="text-lg font-bold text-white tracking-tight leading-snug">
                  {item.title}
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <div className="text-right hidden sm:block">
                <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                  Verified Learning Progress
                </div>
                <div className="text-sm font-bold font-mono text-emerald-400">
                  {completedModules.length} / 4 Modules ({progressPercent}%)
                </div>
              </div>

              {progress?.course_completed ? (
                <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Course Certified</span>
                </div>
              ) : canCompleteCourse ? (
                <button
                  onClick={handleFinalizeCourse}
                  disabled={isFinalizing}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-semibold shadow-lg shadow-emerald-950/50 flex items-center gap-2 transition"
                >
                  {isFinalizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trophy className="w-4 h-4" />}
                  <span>Finalize & Certify Course</span>
                </button>
              ) : (
                <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-xs font-medium">
                  <Clock className="w-4 h-4 text-amber-400" />
                  <span>Learning in Progress</span>
                </div>
              )}
            </div>
          </div>

          {/* Demonstration Course Notice & Official iGOT Banner */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5 text-slate-300">
              <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>
                <strong className="text-white">PRAGYA Interactive Demonstration Course:</strong> Prototype learning environment demonstrating competency intelligence, knowledge checks, practice assignments, and practical Virtual Lab integration.
              </span>
            </div>
            {item.url && !item.url.includes('mock.') && (
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-[11px] flex items-center gap-1.5 shrink-0 transition"
              >
                <span>Launch Official iGOT Course</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>

          {/* Navigation Bar */}
          <div className="flex border-b border-slate-800 bg-slate-900/60 rounded-t-xl px-2 pt-2 gap-2 text-xs overflow-x-auto">
            <button
              onClick={() => setActiveTab('curriculum')}
              className={`px-4 py-2.5 font-medium rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'curriculum'
                  ? 'bg-slate-900 text-indigo-300 border-t-2 border-indigo-500 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Curriculum & Modules</span>
            </button>

            {selectedResource && (
              <button
                onClick={() => setActiveTab('resource')}
                className={`px-4 py-2.5 font-medium rounded-t-lg transition flex items-center gap-2 ${
                  activeTab === 'resource'
                    ? 'bg-slate-900 text-indigo-300 border-t-2 border-indigo-500 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {selectedResource.type === 'VIDEO' ? <Video className="w-3.5 h-3.5" /> : <BookOpen className="w-3.5 h-3.5" />}
                <span className="truncate max-w-[160px]">{selectedResource.title}</span>
              </button>
            )}

            <button
              onClick={() => {
                if (unlockedModules.includes(5)) {
                  setActiveTab('final_assessment');
                } else {
                  alert('Final Assessment is locked. Complete Modules 1, 2, and 3 first.');
                }
              }}
              className={`px-4 py-2.5 font-medium rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'final_assessment'
                  ? 'bg-slate-900 text-emerald-300 border-t-2 border-emerald-500 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <GraduationCap className="w-3.5 h-3.5" />
              <span>Final Assessment</span>
              {!unlockedModules.includes(5) && <Lock className="w-3 h-3 text-slate-500" />}
            </button>

            {progress?.course_completed && (
              <button
                onClick={() => setActiveTab('completion')}
                className={`px-4 py-2.5 font-medium rounded-t-lg transition flex items-center gap-2 ${
                  activeTab === 'completion'
                    ? 'bg-slate-900 text-emerald-300 border-t-2 border-emerald-500 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Trophy className="w-3.5 h-3.5 text-emerald-400" />
                <span>Certification & Evidence</span>
              </button>
            )}
          </div>

          {/* Main Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Center Content (8 cols) */}
            <div className="lg:col-span-8 space-y-6">
              {/* TAB: Curriculum View */}
              {activeTab === 'curriculum' && (
                <div className="space-y-4">
                  {modules.map((mod: CourseModule) => {
                    const isDone = completedModules.includes(mod.id);
                    const isUnlocked = unlockedModules.includes(mod.id);
                    const isMod4 = mod.id === 4;

                    return (
                      <div
                        key={mod.id}
                        className={`p-6 rounded-2xl border transition-all ${
                          !isUnlocked
                            ? 'bg-slate-950/40 border-slate-800/60 opacity-70'
                            : isDone
                            ? 'bg-emerald-950/15 border-emerald-500/30'
                            : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                        } space-y-4`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="space-y-1.5 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                Section {mod.id}
                              </span>
                              {mod.is_lab && (
                                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30 flex items-center gap-1">
                                  <FlaskConical className="w-3 h-3" />
                                  <span>VIRTUAL LAB DEMONSTRATION</span>
                                </span>
                              )}
                              <span className="text-xs text-slate-400 flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {mod.duration}
                              </span>
                              {!isUnlocked && (
                                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-400 flex items-center gap-1">
                                  <Lock className="w-3 h-3" />
                                  <span>Locked</span>
                                </span>
                              )}
                            </div>

                            <h3 className="text-base font-bold text-white tracking-tight">
                              {mod.title}
                            </h3>
                            <p className="text-xs text-slate-300 leading-relaxed">
                              {mod.description}
                            </p>
                          </div>

                          <div className="shrink-0">
                            {isDone ? (
                              <div className="p-2 rounded-xl bg-emerald-600/20 border border-emerald-500/40 text-emerald-300">
                                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                              </div>
                            ) : (
                              <div className="p-2 rounded-xl bg-slate-800 text-slate-500 border border-slate-700">
                                <Clock className="w-5 h-5" />
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Lock Warning if locked */}
                        {!isUnlocked && (
                          <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
                            <Lock className="w-4 h-4 text-amber-400 shrink-0" />
                            <span>
                              Complete Section {mod.id - 1} learning resources and assessments to unlock this module.
                            </span>
                          </div>
                        )}

                        {/* Unlocked Module Activities */}
                        {isUnlocked && (
                          <div className="pt-2 space-y-3">
                            {/* Resources list */}
                            {mod.resources && mod.resources.length > 0 && (
                              <div className="space-y-2">
                                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                                  Learning Resources:
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                  {mod.resources?.map((res: CourseResource) => {
                                    const resProg = progress?.resource_progress?.[res.id];
                                    const resDone = !!resProg?.is_completed;
                                    const isIgot = res.provider === 'iGOT';
                                    const hasUrl = !!res.external_url && res.external_url.trim().length > 0;
                                    const isUnconfigured = isIgot && (!hasUrl || resProg?.status === 'NOT_CONFIGURED');
                                    const isLaunched = isIgot && hasUrl && (resProg?.status === 'LAUNCHED' || resProg?.status === 'IN_PROGRESS');

                                    return (
                                      <button
                                        key={res.id}
                                        onClick={() => {
                                          setSelectedResource(res);
                                          setSelectedModuleId(mod.id);
                                          setActiveTab('resource');
                                        }}
                                        className={`p-3 rounded-xl border text-left transition flex items-center justify-between gap-2 ${
                                          resDone
                                            ? 'bg-emerald-950/20 border-emerald-500/30 hover:border-emerald-500/50'
                                            : isLaunched
                                            ? 'bg-blue-950/20 border-blue-500/30 hover:border-blue-500/50'
                                            : isUnconfigured
                                            ? 'bg-slate-950/60 border-slate-800/80 hover:border-amber-500/30'
                                            : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                                        }`}
                                      >
                                        <div className="flex items-center gap-2.5 truncate">
                                          {isIgot ? (
                                            <div className="w-7 h-7 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center shrink-0">
                                              <Video className="w-3.5 h-3.5" />
                                            </div>
                                          ) : (
                                            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0">
                                              <FileText className="w-3.5 h-3.5" />
                                            </div>
                                          )}
                                          <div className="truncate">
                                            <div className="text-xs font-semibold text-white truncate">
                                              {res.title}
                                            </div>
                                            <div className="text-[10px] text-slate-400 flex items-center gap-1.5">
                                              <span className={isIgot ? 'text-amber-400/90 font-medium' : 'text-emerald-400/90 font-medium'}>
                                                {isIgot ? 'iGOT' : 'PRAGYA'}
                                              </span>
                                              <span>•</span>
                                              <span>{res.type === 'VIDEO' ? 'Digital Video' : 'Study Guide'}</span>
                                              <span>•</span>
                                              <span>{res.duration_display}</span>
                                            </div>
                                          </div>
                                        </div>

                                        {resDone ? (
                                          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 shrink-0">
                                            <CheckCircle2 className="w-3.5 h-3.5" />
                                            <span className="hidden sm:inline">Verified</span>
                                          </span>
                                        ) : isUnconfigured ? (
                                          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-amber-400/80 shrink-0">
                                            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                                            <span>Unconfigured</span>
                                          </span>
                                        ) : isLaunched ? (
                                          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-blue-400 shrink-0">
                                            <Clock className="w-3 h-3" />
                                            <span>Launched</span>
                                          </span>
                                        ) : isIgot ? (
                                          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-indigo-400 shrink-0">
                                            <span>Open</span>
                                            <ExternalLink className="w-3 h-3" />
                                          </span>
                                        ) : (
                                          <span className="text-[10px] font-mono text-indigo-400 shrink-0">Read</span>
                                        )}
                                      </button>
                                    );
                                  })}
                                </div>
                              </div>
                            )}

                            {/* Practical Assignment Trigger (Module 2) */}
                            {mod.assignment && (
                              <div className="pt-1">
                                <button
                                  onClick={() => {
                                    setSelectedModuleId(mod.id);
                                    setActiveTab('assignment');
                                  }}
                                  className="w-full p-3 rounded-xl bg-gradient-to-r from-violet-950/40 via-slate-900 to-slate-900 border border-violet-500/30 hover:border-violet-500/50 transition flex items-center justify-between text-xs"
                                >
                                  <div className="flex items-center gap-2">
                                    <FileCode2 className="w-4 h-4 text-violet-400" />
                                    <span className="font-semibold text-white">
                                      Practical Assignment: District Household Survey Allocation
                                    </span>
                                  </div>
                                  <span className="px-2.5 py-1 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-[10px] transition">
                                    {progress?.activities_status?.m2_assignment_passed ? 'Review Assignment' : 'Open Assignment'}
                                  </span>
                                </button>
                              </div>
                            )}

                            {/* Knowledge Check Trigger */}
                            {mod.knowledge_check && (
                              <div className="pt-1">
                                <button
                                  onClick={() => {
                                    setSelectedModuleId(mod.id);
                                    setActiveTab('knowledge_check');
                                  }}
                                  className="w-full p-3 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between text-xs"
                                >
                                  <div className="flex items-center gap-2">
                                    <HelpCircle className="w-4 h-4 text-indigo-400" />
                                    <span className="font-semibold text-white">
                                      {mod.knowledge_check.title}
                                    </span>
                                  </div>
                                  <span className="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-[10px] transition">
                                    Take Knowledge Check
                                  </span>
                                </button>
                              </div>
                            )}

                            {/* Virtual Lab Launch Trigger (Module 4) */}
                            {isMod4 && (
                              <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                <div className="space-y-1">
                                  <div className="text-xs font-semibold text-white flex items-center gap-1.5">
                                    <FlaskConical className="w-4 h-4 text-violet-400" />
                                    <span>Practical Competency Demonstration Workbench</span>
                                  </div>
                                  <p className="text-[11px] text-slate-400 leading-snug">
                                    Execute all 4 analytical simulation steps to earn certified competency evidence.
                                  </p>
                                </div>

                                <div className="flex items-center gap-3 shrink-0">
                                  <Link
                                    href={`/employee/labs/${mod.lab_scenario_id || '22222222-3333-4444-5555-666666666602'}?courseId=${courseId}`}
                                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs transition shadow-md shadow-violet-950/40"
                                  >
                                    <FlaskConical className="w-3.5 h-3.5" />
                                    <span>Launch Virtual Lab Workbench</span>
                                    <ExternalLink className="w-3.5 h-3.5" />
                                  </Link>
                                  {isLabVerified && (
                                    <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                                      <CheckCircle2 className="w-3.5 h-3.5" />
                                      <span>Verified</span>
                                    </span>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* TAB: Resource Viewer (Video or Reading) */}
              {activeTab === 'resource' && selectedResource && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setActiveTab('curriculum')}
                      className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      <span>Back to Curriculum</span>
                    </button>
                  </div>

                  {selectedResource.provider === 'iGOT' ? (
                    <ExternalLearningResourceCard
                      resource={selectedResource}
                      courseId={courseId}
                      employeeId={employee?.id}
                      isCompleted={!!progress?.resource_progress?.[selectedResource.id]?.is_completed}
                      progressStatus={progress?.resource_progress?.[selectedResource.id]?.status}
                      verificationStatus={progress?.resource_progress?.[selectedResource.id]?.verification_status}
                    />
                  ) : selectedResource.type === 'VIDEO' ? (
                    <CourseVideoPlayer
                      videoId={selectedResource.id}
                      title={selectedResource.title}
                      videoUrl={selectedResource.video_url}
                      durationSeconds={selectedResource.duration_seconds || 180}
                      initialProgressSeconds={progress?.resource_progress?.[selectedResource.id]?.progress_seconds || 0}
                      isCompleted={!!progress?.resource_progress?.[selectedResource.id]?.is_completed}
                      onProgressUpdate={async (progSec, durSec, pct, isDone) => {
                        await updateResourceProgress({
                          resourceId: selectedResource.id,
                          payload: {
                            module_id: selectedModuleId,
                            resource_type: 'VIDEO',
                            progress_seconds: progSec,
                            duration_seconds: durSec,
                            progress_percentage: pct,
                            is_completed: isDone,
                          },
                        });
                      }}
                    />
                  ) : (
                    <CourseReadingViewer
                      readingId={selectedResource.id}
                      title={selectedResource.title}
                      durationDisplay={selectedResource.duration_display}
                      contentMarkdown={selectedResource.content_markdown || '# Reading Material\n\nContent details.'}
                      isCompleted={!!progress?.resource_progress?.[selectedResource.id]?.is_completed}
                      onMarkComplete={async () => {
                        await updateResourceProgress({
                          resourceId: selectedResource.id,
                          payload: {
                            module_id: selectedModuleId,
                            resource_type: 'READING',
                            progress_seconds: 300,
                            duration_seconds: 300,
                            progress_percentage: 100,
                            is_completed: true,
                          },
                        });
                      }}
                    />
                  )}
                </div>
              )}

              {/* TAB: Knowledge Check View */}
              {activeTab === 'knowledge_check' && (
                <div className="space-y-4">
                  <button
                    onClick={() => setActiveTab('curriculum')}
                    className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Back to Curriculum</span>
                  </button>

                  <ModuleKnowledgeCheck
                    moduleId={selectedModuleId}
                    title={currentModule?.knowledge_check?.title || `Module ${selectedModuleId} Knowledge Check`}
                    questions={currentModule?.knowledge_check?.questions || []}
                    passThresholdPercentage={currentModule?.knowledge_check?.pass_threshold_percentage || 75.0}
                    isAlreadyPassed={
                      selectedModuleId === 1
                        ? !!progress?.activities_status?.m1_kc_passed
                        : selectedModuleId === 2
                        ? !!progress?.activities_status?.m2_kc_passed
                        : selectedModuleId === 3
                        ? !!progress?.activities_status?.m3_kc_passed
                        : false
                    }
                    onCheckSubmit={async (answers) => {
                      return await submitKnowledgeCheck({
                        moduleId: selectedModuleId,
                        answers,
                      });
                    }}
                  />
                </div>
              )}

              {/* TAB: Practical Assignment View (Module 2) */}
              {activeTab === 'assignment' && (
                <div className="space-y-4">
                  <button
                    onClick={() => setActiveTab('curriculum')}
                    className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Back to Curriculum</span>
                  </button>

                  <ModuleAssignment
                    moduleId={2}
                    assignmentData={modules.find((m: CourseModule) => m.id === 2)?.assignment}
                    isAlreadyPassed={progress?.activities_status?.m2_assignment_passed}
                    onAssignmentSubmit={async (payload) => {
                      return await submitAssignment({
                        moduleId: 2,
                        payload,
                      });
                    }}
                  />
                </div>
              )}

              {/* TAB: Final Assessment View */}
              {activeTab === 'final_assessment' && (
                <div className="space-y-4">
                  <button
                    onClick={() => setActiveTab('curriculum')}
                    className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Back to Curriculum</span>
                  </button>

                  <CourseFinalAssessment
                    assessmentData={curriculum?.final_assessment}
                    isUnlocked={unlockedModules.includes(5)}
                    isAlreadyPassed={progress?.final_assessment_passed}
                    score={progress?.final_assessment_score}
                    onAssessmentSubmit={async (answers) => {
                      return await submitFinalAssessment(answers);
                    }}
                  />
                </div>
              )}

              {/* TAB: Completion & Recalibration View */}
              {activeTab === 'completion' && (
                <CourseCompletionCelebration
                  courseTitle={item.title}
                  provider={item.provider}
                  finalScore={progress?.final_assessment_score || 88.0}
                  onRecalibrate={async () => {
                    return await recalibrateAction();
                  }}
                />
              )}
            </div>

            {/* Right Sidebar (4 cols) */}
            <div className="lg:col-span-4 space-y-6">
              {/* Learning Journey Checklist */}
              <div className="p-5 rounded-2xl bg-[#0A0E1A]/95 border border-slate-800 space-y-4 shadow-xl">
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Target className="w-3.5 h-3.5 text-indigo-400" />
                  Learning Journey Checklist
                </div>

                <div className="space-y-2.5 text-xs">
                  <div className={`p-2.5 rounded-xl border flex items-center justify-between ${
                    completedModules.includes(1) ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-slate-950/50 border-slate-800 text-slate-400'
                  }`}>
                    <span>1. Foundations & Knowledge Check</span>
                    {completedModules.includes(1) ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Clock className="w-3.5 h-3.5" />}
                  </div>

                  <div className={`p-2.5 rounded-xl border flex items-center justify-between ${
                    completedModules.includes(2) ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-slate-950/50 border-slate-800 text-slate-400'
                  }`}>
                    <span>2. Methodology & Practical Assignment</span>
                    {completedModules.includes(2) ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Clock className="w-3.5 h-3.5" />}
                  </div>

                  <div className={`p-2.5 rounded-xl border flex items-center justify-between ${
                    completedModules.includes(3) ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-slate-950/50 border-slate-800 text-slate-400'
                  }`}>
                    <span>3. Official Standards & Assessment</span>
                    {completedModules.includes(3) ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Clock className="w-3.5 h-3.5" />}
                  </div>

                  <div className={`p-2.5 rounded-xl border flex items-center justify-between ${
                    isLabVerified ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-slate-950/50 border-slate-800 text-slate-400'
                  }`}>
                    <span>4. PRAGYA Virtual Lab Simulation</span>
                    {isLabVerified ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <FlaskConical className="w-3.5 h-3.5 text-violet-400" />}
                  </div>

                  <div className={`p-2.5 rounded-xl border flex items-center justify-between ${
                    progress?.final_assessment_passed ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-slate-950/50 border-slate-800 text-slate-400'
                  }`}>
                    <span>5. Comprehensive Final Assessment</span>
                    {progress?.final_assessment_passed ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <GraduationCap className="w-3.5 h-3.5 text-cyan-400" />}
                  </div>
                </div>
              </div>

              {/* Course Meta Card */}
              <div className="p-5 rounded-2xl bg-[#0A0E1A]/95 border border-slate-800 space-y-4">
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Course Details
                </div>

                <div className="space-y-3 text-xs">
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Provider</span>
                    <span className="font-semibold text-slate-200">{item.provider}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Total Duration</span>
                    <span className="font-mono text-slate-200">{durationHours} Hours</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Language</span>
                    <span className="text-slate-200">{item.language}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-800">
                    <span className="text-slate-400">Learning Format</span>
                    <span className="capitalize text-slate-200">
                      {item.format.toLowerCase().replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Return Buttons */}
                <div className="pt-2 space-y-2">
                  <Link
                    href={`/employee/courses/${item.id}`}
                    className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs flex items-center justify-center gap-2 transition"
                  >
                    <span>Full Syllabus & Details</span>
                  </Link>

                  <Link
                    href="/employee/learning"
                    className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 font-medium text-xs flex items-center justify-center gap-2 transition"
                  >
                    <span>Back to Recommendations</span>
                  </Link>
                </div>
              </div>

              {/* Target Competencies */}
              {item.competencies && item.competencies.length > 0 && (
                <div className="p-5 rounded-2xl bg-[#0A0E1A]/95 border border-slate-800 space-y-3">
                  <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Target className="w-3.5 h-3.5 text-indigo-400" />
                    Target Competencies
                  </div>
                  <div className="space-y-2">
                    {item.competencies.map((c, i: number) => (
                      <div
                        key={i}
                        className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs space-y-1"
                      >
                        <div className="flex justify-between font-semibold text-slate-200">
                          <span>{c.competency_name || c.competency_code}</span>
                          <span className="text-[10px] text-indigo-400 font-mono">
                            {c.coverage_level}
                          </span>
                        </div>
                        {c.learning_outcome && (
                          <p className="text-[11px] text-slate-400 leading-snug">
                            {c.learning_outcome}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
}

export default function CoursePlayerPage() {
  return (
    <Suspense
      fallback={
        <AppShell role="EMPLOYEE" pageTitle="Interactive Course Player">
          <PageContainer>
            <div className="flex items-center justify-center min-h-[50vh]">
              <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
            </div>
          </PageContainer>
        </AppShell>
      }
    >
      <CoursePlayerContent />
    </Suspense>
  );
}
