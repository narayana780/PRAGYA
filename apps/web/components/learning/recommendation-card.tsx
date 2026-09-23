'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  Sparkles,
  ChevronRight,
  ArrowUpRight,
  Zap,
} from 'lucide-react';
import Link from 'next/link';
import { ProviderBadge } from './provider-badge';
import { GapPriorityBadge } from '@/components/gaps/gap-priority-badge';
import { RecommendationExplanationDrawer } from './recommendation-explanation-drawer';
import { getCourseLaunchUrl, isExternalLaunchUrl } from '@/lib/course-utils';
import type { LearningRecommendation } from '@pragya/types';

interface RecommendationCardProps {
  recommendation: LearningRecommendation;
  isTopRank?: boolean;
  onStart?: (recId: string) => void;
}

export function RecommendationCard({
  recommendation,
  isTopRank = false,
  onStart,
}: RecommendationCardProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const item = recommendation.learning_item;

  const durationHours = Math.round(item.duration_minutes / 60);

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`relative group rounded-xl transition-all duration-200 border ${
          isTopRank
            ? 'bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900/90 border-indigo-500/40 shadow-lg shadow-indigo-950/30'
            : 'bg-slate-900/70 hover:bg-slate-900/90 border-slate-800 hover:border-slate-700'
        }`}
      >
        {isTopRank && (
          <div className="absolute -top-3 left-6 z-10 px-3 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-gradient-to-r from-amber-500 to-indigo-600 text-slate-950 shadow-md flex items-center gap-1">
            <Zap className="w-3 h-3 fill-slate-950" />
            Next Best Learning Action
          </div>
        )}

        <div className="p-5 flex flex-col justify-between h-full space-y-4">
          {/* Header Row */}
          <div className="space-y-2.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <ProviderBadge provider={item.provider} sourceMode={item.source_mode} size="sm" />
                <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                  Level {item.level}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <GapPriorityBadge priority={recommendation.priority_level} size="sm" />
                <div
                  className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/30 text-xs font-bold font-mono"
                  title="Deterministic Recommendation Score"
                >
                  <Sparkles className="w-3 h-3 text-amber-400" />
                  <span>{recommendation.score.toFixed(1)}</span>
                </div>
              </div>
            </div>

            {/* Title & Target */}
            <div>
              <h3 className="text-base font-bold text-slate-100 group-hover:text-amber-300 transition-colors line-clamp-2">
                {item.title}
              </h3>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                <span>Targets:</span>
                <span className="text-slate-200 font-medium">{recommendation.target_competency_name}</span>
                <span className="text-slate-500">({recommendation.domain_name})</span>
              </p>
            </div>
          </div>

          {/* Description snippet */}
          <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
            {item.description}
          </p>

          {/* Why Recommended Pill / Snippet */}
          <div
            onClick={() => setDrawerOpen(true)}
            className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 cursor-pointer group/why transition-colors"
          >
            <div className="flex items-center justify-between text-[11px] font-semibold text-amber-400 mb-1">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                Why PRAGYA Recommended This
              </span>
              <span className="text-[10px] text-slate-400 group-hover/why:text-amber-300 flex items-center">
                Details <ChevronRight className="w-3 h-3 ml-0.5" />
              </span>
            </div>
            <p className="text-[11px] text-slate-300 line-clamp-2 leading-snug">
              {recommendation.reason}
            </p>
          </div>

          {/* Meta & Actions Row */}
          <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                {durationHours > 0 ? `${durationHours}h` : `${item.duration_minutes}m`}
              </span>
              <span className="capitalize text-slate-400">
                {item.format.toLowerCase().replace('_', ' ')}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setDrawerOpen(true)}
                className="px-2.5 py-1 rounded text-[11px] font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
              >
                Why recommended?
              </button>
              {(() => {
                const launchUrl = getCourseLaunchUrl(item);
                const isExternal = isExternalLaunchUrl(launchUrl);
                return isExternal ? (
                  <a
                    href={launchUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-1 shadow-sm transition-all"
                    onClick={() => onStart && onStart(recommendation.id)}
                  >
                    <span>Start</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </a>
                ) : (
                  <Link
                    href={launchUrl}
                    className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-1 shadow-sm transition-all"
                    onClick={() => onStart && onStart(recommendation.id)}
                  >
                    <span>Start</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </Link>
                );
              })()}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Detail & Explanation Drawer */}
      <RecommendationExplanationDrawer
        recommendation={drawerOpen ? recommendation : null}
        onClose={() => setDrawerOpen(false)}
        onStart={onStart}
      />
    </>
  );
}
