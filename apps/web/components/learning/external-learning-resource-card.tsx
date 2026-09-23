'use client';

import React, { useState } from 'react';
import {
  ExternalLink,
  CheckCircle2,
  Clock,
  AlertCircle,
  RefreshCw,
  Sparkles,
  ShieldCheck,
  Video,
  Info,
} from 'lucide-react';
import type { CourseResource } from '@pragya/types';
import { useLaunchResource, useSyncResource } from '@/hooks/use-courses';

interface ExternalLearningResourceCardProps {
  resource: CourseResource;
  courseId: string;
  employeeId?: string;
  isCompleted?: boolean;
  progressPercentage?: number;
  progressStatus?: string;
  verificationStatus?: string;
  onOpenExternal?: () => void;
}

export function ExternalLearningResourceCard({
  resource,
  courseId,
  employeeId,
  isCompleted = false,
  progressStatus = 'NOT_STARTED',
  verificationStatus = 'NOT_VERIFIED',
}: ExternalLearningResourceCardProps) {
  const { mutateAsync: launchResource, isPending: isLaunching } = useLaunchResource(courseId, employeeId);
  const { mutateAsync: syncResource, isPending: isSyncing } = useSyncResource(courseId, employeeId);

  const [syncFeedback, setSyncFeedback] = useState<{
    type: 'success' | 'info' | 'warning';
    message: string;
  } | null>(null);

  const hasConfiguredUrl = !!resource.external_url && resource.external_url.trim().length > 0;

  // Truthful provider-learning state machine
  // States: NOT_CONFIGURED | NOT_STARTED | LAUNCHED | IN_PROGRESS | VERIFIED_COMPLETED | VERIFICATION_FAILED
  const effectiveState:
    | 'NOT_CONFIGURED'
    | 'NOT_STARTED'
    | 'LAUNCHED'
    | 'IN_PROGRESS'
    | 'VERIFIED_COMPLETED'
    | 'VERIFICATION_FAILED' = (() => {
    if (isCompleted || verificationStatus === 'VERIFIED' || progressStatus === 'VERIFIED_COMPLETED') {
      return 'VERIFIED_COMPLETED';
    }
    if (verificationStatus === 'FAILED' || progressStatus === 'VERIFICATION_FAILED') {
      return 'VERIFICATION_FAILED';
    }
    if (!hasConfiguredUrl || progressStatus === 'NOT_CONFIGURED') {
      return 'NOT_CONFIGURED';
    }
    if (progressStatus === 'IN_PROGRESS') {
      return 'IN_PROGRESS';
    }
    if (progressStatus === 'LAUNCHED') {
      return 'LAUNCHED';
    }
    return 'NOT_STARTED';
  })();

  const handleLaunch = async () => {
    try {
      // 1. Authoritative backend launch registration (records LAUNCHED without fake completion)
      await launchResource(resource.id);

      // 2. Open external URL in a new tab if configured
      if (hasConfiguredUrl && resource.external_url) {
        window.open(resource.external_url, '_blank', 'noopener,noreferrer');
      } else {
        setSyncFeedback({
          type: 'info',
          message: 'Specific iGOT resource link is not configured for this item.',
        });
      }
    } catch (err: unknown) {
      console.error('Failed to register resource launch:', err);
    }
  };

  const handleSyncStatus = async () => {
    setSyncFeedback(null);
    try {
      const res = await syncResource(resource.id);
      if (res.verified) {
        setSyncFeedback({
          type: 'success',
          message: res.message || 'iGOT completion verified by external provider.',
        });
      } else {
        setSyncFeedback({
          type: 'info',
          message:
            res.message ||
            'iGOT completion verification is not configured for this prototype. Official iGOT completion verification requires provider API integration.',
        });
      }
    } catch (err: unknown) {
      setSyncFeedback({
        type: 'warning',
        message: (err as Error)?.message || 'Failed to sync with provider API.',
      });
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A]/95 p-6 shadow-2xl backdrop-blur-md space-y-6">
      {/* Header section with Provider & Type Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span>Provider: iGOT Karmayogi</span>
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium bg-slate-800/80 text-slate-300 border border-slate-700">
            <Video className="w-3 h-3 text-indigo-400" />
            <span>{resource.type}</span>
          </span>
          {resource.external_resource_id && (
            <span className="text-[11px] font-mono text-slate-400">
              ID: {resource.external_resource_id}
            </span>
          )}
        </div>

        {/* Verification Status Pill */}
        <div>
          {effectiveState === 'VERIFIED_COMPLETED' ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>✓ Completed on iGOT</span>
            </span>
          ) : effectiveState === 'IN_PROGRESS' ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>◐ Learning in Progress on iGOT</span>
            </span>
          ) : effectiveState === 'LAUNCHED' ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
              <ExternalLink className="w-3.5 h-3.5 text-blue-400" />
              <span>↗ Learning Launched on iGOT</span>
            </span>
          ) : effectiveState === 'VERIFICATION_FAILED' ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-500/15 text-red-300 border border-red-500/30">
              <AlertCircle className="w-3.5 h-3.5 text-red-400" />
              <span>⚠ Verification Failed</span>
            </span>
          ) : effectiveState === 'NOT_CONFIGURED' ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-800/80 text-amber-300/90 border border-amber-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>○ iGOT Resource Not Configured</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-800/80 text-slate-300 border border-slate-700">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
              <span>○ Not Started</span>
            </span>
          )}
        </div>
      </div>

      {/* Main Content Info */}
      <div className="space-y-3">
        <h2 className="text-xl font-bold text-white tracking-tight leading-snug">
          {resource.title}
        </h2>
        {resource.description && (
          <p className="text-xs text-slate-300 leading-relaxed">
            {resource.description}
          </p>
        )}
        <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>Estimated Duration: {resource.duration_display || '45 mins'}</span>
          </span>
          <span>•</span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
            <span>
              {hasConfiguredUrl
                ? 'Official iGOT Learning Resource'
                : 'Required Learning Resource'}
            </span>
          </span>
        </div>
      </div>

      {/* Primary Interaction Action Area */}
      <div className="p-5 sm:p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Descriptive Content Area: flex-1 min-w-0 */}
          <div className="flex-1 min-w-0 space-y-2">
            <div className="text-xs font-semibold text-white flex items-center gap-1.5">
              <span>Official Learning Ecosystem</span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {hasConfiguredUrl
                ? 'Study the official lecture and curriculum content on the official iGOT Karmayogi platform.'
                : 'This learning activity is intended to be delivered through the iGOT Karmayogi platform. The specific iGOT resource link has not yet been configured.'}
            </p>
            {(!hasConfiguredUrl || effectiveState === 'NOT_CONFIGURED') && (
              <div className="pt-1 flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px] font-mono font-medium">
                  Specific iGOT resource link is not configured.
                </span>
                <span className="text-[10px] sm:text-[11px] text-slate-500 font-mono">
                  Official iGOT completion verification requires provider integration.
                </span>
              </div>
            )}
          </div>

          {/* Action Buttons Area: shrink-0 */}
          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            {effectiveState === 'NOT_CONFIGURED' || !hasConfiguredUrl ? (
              <button
                disabled={true}
                className="px-4 py-2.5 rounded-xl bg-slate-800/60 text-slate-500 font-semibold text-xs border border-slate-800 cursor-not-allowed flex items-center gap-2 opacity-60 shadow-sm"
                title="Specific iGOT resource link is not configured"
              >
                <span>Launch iGOT Learning</span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-600" />
              </button>
            ) : effectiveState === 'LAUNCHED' || effectiveState === 'IN_PROGRESS' ? (
              <button
                onClick={handleLaunch}
                disabled={isLaunching}
                className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-950/50"
              >
                <span>Open iGOT Again ↗</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            ) : effectiveState === 'VERIFIED_COMPLETED' ? (
              <button
                onClick={handleLaunch}
                disabled={isLaunching}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition flex items-center gap-2"
              >
                <span>View on iGOT ↗</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                onClick={handleLaunch}
                disabled={isLaunching}
                className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-950/50"
              >
                <span>Launch iGOT Learning ↗</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            )}

            <button
              onClick={handleSyncStatus}
              disabled={!hasConfiguredUrl || isSyncing}
              className={`px-3.5 py-2.5 rounded-xl border text-xs font-medium transition flex items-center gap-2 ${
                !hasConfiguredUrl
                  ? 'bg-slate-800/40 border-slate-800 text-slate-500 cursor-not-allowed opacity-60'
                  : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300 hover:text-white'
              }`}
              title={
                !hasConfiguredUrl
                  ? 'iGOT provider integration is not configured.'
                  : 'Synchronize verified completion with iGOT'
              }
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin text-indigo-400' : ''}`} />
              <span className="hidden sm:inline">Sync iGOT Status</span>
            </button>
          </div>
        </div>

        {/* Sync Feedback Message */}
        {syncFeedback && (
          <div
            className={`p-3 rounded-xl text-xs flex items-start gap-2.5 border ${
              syncFeedback.type === 'success'
                ? 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
                : syncFeedback.type === 'warning'
                ? 'bg-amber-950/30 border-amber-500/30 text-amber-300'
                : 'bg-indigo-950/30 border-indigo-500/30 text-indigo-300'
            }`}
          >
            {syncFeedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            ) : syncFeedback.type === 'warning' ? (
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            ) : (
              <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            )}
            <span className="leading-relaxed">{syncFeedback.message}</span>
          </div>
        )}
      </div>

      {/* Educational Notice explaining PRAGYA vs iGOT Role */}
      <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/20 flex items-start gap-3 text-xs text-slate-300">
        <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-white">
            PRAGYA Architectural Integration Notice
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            PRAGYA provides the competency intelligence, personalization layer, practical knowledge checks, and Virtual Lab simulations. Official video lectures and theoretical training are delivered via the iGOT Karmayogi ecosystem. After learning on iGOT, return to PRAGYA to complete your module knowledge checks and practical simulations.
          </p>
        </div>
      </div>
    </div>
  );
}
