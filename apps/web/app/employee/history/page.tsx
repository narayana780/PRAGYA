'use client';

import React, { useState } from 'react';
import {
  History,
  Activity,
  Brain,
  GraduationCap,
  FlaskConical,
  BookOpen,
  RefreshCw,
  TrendingUp,
  Search,
  HelpCircle,
  Clock,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useEmployeePerformanceTimeline } from '@/hooks/use-performance';

export default function EmployeeHistoryPage() {
  const { data: employee, isLoading: empLoading } = useCurrentEmployee();
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const {
    data: timelineData,
    isLoading: timelineLoading,
    error: timelineError,
    refetch,
  } = useEmployeePerformanceTimeline(employee?.id);

  const isLoading = empLoading || timelineLoading;

  // Filter events by category and search
  const filteredEvents = (() => {
    if (!timelineData?.events) return [];
    return timelineData.events.filter((ev) => {
      // Category filter mapping
      let matchesCategory = true;
      if (selectedCategory === 'ASSESSMENTS') {
        matchesCategory =
          ev.type === 'DIAGNOSTIC_ASSESSMENT' || ev.type === 'ADAPTIVE_ASSESSMENT';
      } else if (selectedCategory === 'QUIZZES') {
        matchesCategory = ev.type === 'QUIZ';
      } else if (selectedCategory === 'LABS') {
        matchesCategory = ev.type === 'VIRTUAL_LAB';
      } else if (selectedCategory === 'COURSES') {
        matchesCategory = ev.type === 'COURSE_ACTIVITY';
      } else if (selectedCategory === 'COMPETENCY') {
        matchesCategory =
          ev.type === 'COMPETENCY_RECALIBRATION' || ev.type === 'SCORE_UPDATE';
      }

      // Search query filter
      const matchesSearch =
        searchQuery === '' ||
        ev.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ev.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (ev.competency_name &&
          ev.competency_name.toLowerCase().includes(searchQuery.toLowerCase()));

      return matchesCategory && matchesSearch;
    });
  })();

  // Icon & color helper for timeline events
  const getEventVisuals = (type: string) => {
    switch (type) {
      case 'DIAGNOSTIC_ASSESSMENT':
        return {
          icon: <Activity className="w-4 h-4 text-cyan-400" />,
          bgColor: 'bg-cyan-500/10 border-cyan-500/30',
          badgeClass: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
          label: 'Diagnostic',
        };
      case 'QUIZ':
        return {
          icon: <Brain className="w-4 h-4 text-purple-400" />,
          bgColor: 'bg-purple-500/10 border-purple-500/30',
          badgeClass: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
          label: 'Quiz',
        };
      case 'ADAPTIVE_ASSESSMENT':
        return {
          icon: <GraduationCap className="w-4 h-4 text-blue-400" />,
          bgColor: 'bg-blue-500/10 border-blue-500/30',
          badgeClass: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
          label: 'Adaptive CAT',
        };
      case 'VIRTUAL_LAB':
        return {
          icon: <FlaskConical className="w-4 h-4 text-teal-400" />,
          bgColor: 'bg-teal-500/10 border-teal-500/30',
          badgeClass: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
          label: 'Virtual Lab',
        };
      case 'COURSE_ACTIVITY':
        return {
          icon: <BookOpen className="w-4 h-4 text-amber-400" />,
          bgColor: 'bg-amber-500/10 border-amber-500/30',
          badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
          label: 'Course Activity',
        };
      case 'COMPETENCY_RECALIBRATION':
        return {
          icon: <TrendingUp className="w-4 h-4 text-emerald-400" />,
          bgColor: 'bg-emerald-500/10 border-emerald-500/30',
          badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
          label: 'Recalibration',
        };
      default:
        return {
          icon: <History className="w-4 h-4 text-slate-400" />,
          bgColor: 'bg-slate-500/10 border-slate-500/30',
          badgeClass: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
          label: 'Score Update',
        };
    }
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Learning History">
      <PageContainer>
        <PageHeader
          title="Activity & Learning History"
          subtitle="Audit-compliant, chronological activity log across assessments, virtual labs, quizzes, course completions, and recalibrations."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'History' },
          ]}
          actions={
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
              title="Refresh timeline"
            >
              <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
              Sync Timeline
            </button>
          }
        />

        {isLoading ? (
          <div className="py-20 flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
            <p className="text-sm text-slate-400 font-mono">
              Fetching chronological learning activity logs...
            </p>
          </div>
        ) : timelineError ? (
          <div className="p-8 rounded-xl bg-rose-950/20 border border-rose-800/40 text-center max-w-lg mx-auto my-12">
            <History className="w-10 h-10 text-rose-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-rose-200 mb-1">
              Unable to Load Activity Timeline
            </h3>
            <p className="text-sm text-rose-300/80 mb-4">
              An error occurred while loading learning and assessment records.
            </p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 text-xs font-medium rounded-lg bg-rose-600 hover:bg-rose-500 text-white transition"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="space-y-6 pb-12">
            {/* Filter Tabs & Search Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800/80">
              <div className="flex flex-wrap items-center gap-1.5">
                {[
                  { id: 'ALL', label: 'All Records' },
                  { id: 'ASSESSMENTS', label: 'Assessments' },
                  { id: 'QUIZZES', label: 'AI Quizzes' },
                  { id: 'LABS', label: 'Virtual Labs' },
                  { id: 'COURSES', label: 'Course Progress' },
                  { id: 'COMPETENCY', label: 'Competency Updates' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setSelectedCategory(tab.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      selectedCategory === tab.id
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                        : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Filter events..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-full sm:w-56"
                />
              </div>
            </div>

            {/* Timeline Events List */}
            {filteredEvents.length > 0 ? (
              <div className="relative border-l-2 border-slate-800/90 ml-4 sm:ml-6 space-y-6 py-2">
                {filteredEvents.map((event) => {
                  const visuals = getEventVisuals(event.type);
                  const dateObj = new Date(event.timestamp);
                  const formattedDateTime = !isNaN(dateObj.getTime())
                    ? dateObj.toLocaleString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                    : 'Recorded';

                  return (
                    <div key={event.id} className="relative pl-6 sm:pl-8 group">
                      {/* Timeline Node Point */}
                      <div
                        className={`absolute -left-[17px] top-1.5 w-8 h-8 rounded-full border flex items-center justify-center bg-[#0B1120] shadow-md transition-transform group-hover:scale-110 ${visuals.bgColor}`}
                      >
                        {visuals.icon}
                      </div>

                      {/* Event Content Card */}
                      <div className="p-4 sm:p-5 rounded-2xl bg-[#0B1120]/90 border border-slate-800 shadow-lg hover:border-slate-700 transition">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                          <div className="flex flex-wrap items-center gap-2">
                            <span
                              className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${visuals.badgeClass}`}
                            >
                              {visuals.label}
                            </span>
                            <h4 className="text-sm font-bold text-slate-100">
                              {event.title}
                            </h4>
                            {event.competency_name && (
                              <span className="text-[11px] text-cyan-400 bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-900/40">
                                {event.competency_name}
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                            <Clock className="w-3 h-3 text-slate-500" />
                            <span>{formattedDateTime}</span>
                          </div>
                        </div>

                        <p className="text-xs text-slate-300 mb-3">
                          {event.description}
                        </p>

                        <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] pt-3 border-t border-slate-800/60">
                          <div className="flex items-center gap-3">
                            <span className="text-slate-500">
                              Source: <span className="text-slate-400">{event.source}</span>
                            </span>
                            {event.status && (
                              <span className="text-slate-500">
                                Status:{' '}
                                <span
                                  className={`font-semibold ${
                                    event.status === 'COMPLETED' ||
                                    event.status === 'PASSED' ||
                                    event.status === 'RECALIBRATED'
                                      ? 'text-emerald-400'
                                      : 'text-cyan-400'
                                  }`}
                                >
                                  {event.status}
                                </span>
                              </span>
                            )}
                          </div>

                          {event.percentage !== null && event.percentage !== undefined && (
                            <div className="flex items-center gap-1.5 font-mono">
                              <span className="text-slate-400">Score:</span>
                              <span className="text-xs font-bold text-cyan-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                                {event.percentage.toFixed(1)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 my-8 max-w-md mx-auto">
                <HelpCircle className="w-12 h-12 text-slate-500 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-slate-200">
                  No Events Found
                </h3>
                <p className="text-xs text-slate-400 mt-1 mb-4">
                  {searchQuery || selectedCategory !== 'ALL'
                    ? 'No activity matches the current category or search keyword.'
                    : 'No learning or assessment events have been recorded yet.'}
                </p>
                {(searchQuery || selectedCategory !== 'ALL') && (
                  <button
                    onClick={() => {
                      setSelectedCategory('ALL');
                      setSearchQuery('');
                    }}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </PageContainer>
    </AppShell>
  );
}
