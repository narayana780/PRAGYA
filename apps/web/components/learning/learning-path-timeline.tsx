'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  ExternalLink,
  Milestone,
  Sparkles,
} from 'lucide-react';
import { ProviderBadge } from './provider-badge';
import type { LearningPath } from '@pragya/types';

interface LearningPathTimelineProps {
  learningPath: LearningPath | null;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export function LearningPathTimeline({
  learningPath,
  onRefresh,
  isRefreshing = false,
}: LearningPathTimelineProps) {
  if (!learningPath || !learningPath.items || learningPath.items.length === 0) {
    return (
      <div className="p-8 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-3">
        <Milestone className="w-10 h-10 text-slate-600 mx-auto" />
        <h4 className="text-base font-semibold text-slate-200">No Learning Pathway Generated</h4>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          PRAGYA automatically curates a multi-provider progression based on your demonstrated competency gaps.
        </p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md transition-all"
          >
            {isRefreshing ? 'Generating Pathway...' : 'Generate Learning Pathway'}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Path Header */}
      <div className="p-6 rounded-xl bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
              Personalized Cadre Progression
            </span>
            <span className="text-xs text-slate-500 font-mono">
              {learningPath.items.length} Structured Milestones
            </span>
          </div>
          <h3 className="text-xl font-bold text-slate-100">{learningPath.title}</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            {learningPath.description}
          </p>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all shrink-0 flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>{isRefreshing ? 'Recalculating...' : 'Refresh Pathway'}</span>
          </button>
        )}
      </div>

      {/* Progressive Step Timeline */}
      <div className="relative pl-6 md:pl-10 space-y-8 before:absolute before:left-3 md:before:left-5 before:top-4 before:bottom-4 before:w-0.5 before:bg-gradient-to-b before:from-indigo-500 before:via-amber-500 before:to-teal-500">
        {learningPath.items.map((milestone, idx) => {
          const item = milestone.learning_item;
          const durationHours = Math.round(milestone.estimated_duration / 60);

          return (
            <motion.div
              key={milestone.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="relative group"
            >
              {/* Step circle marker */}
              <div className="absolute -left-6 md:-left-10 top-3 -translate-x-1/2 w-7 h-7 rounded-full bg-slate-900 border-2 border-indigo-500 flex items-center justify-center text-xs font-bold font-mono text-indigo-300 shadow-md group-hover:border-amber-400 group-hover:text-amber-300 transition-colors">
                {milestone.sequence_order}
              </div>

              {/* Milestone Card */}
              <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <ProviderBadge provider={item.provider} sourceMode={item.source_mode} size="sm" />
                    <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      Step {milestone.sequence_order} of {learningPath.items.length}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      {durationHours > 0 ? `${durationHours} hrs` : `${milestone.estimated_duration} mins`}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-slate-800 text-slate-300">
                      {milestone.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <div>
                  <h4 className="text-base font-bold text-slate-100 group-hover:text-amber-300 transition-colors">
                    {item.title}
                  </h4>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {milestone.reason}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2 text-slate-400">
                    <span className="text-slate-500">Format:</span>
                    <span className="capitalize text-slate-300">{item.format.toLowerCase().replace('_', ' ')}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-500">Difficulty:</span>
                    <span className="capitalize text-slate-300">{item.difficulty.toLowerCase()}</span>
                  </div>

                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 transition-colors"
                    >
                      <span>Open Module</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
