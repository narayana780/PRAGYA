'use client';

import React from 'react';
import { Clock, BookOpen, ExternalLink, Sparkles } from 'lucide-react';
import { GlassCard } from './glass-card';
import { Badge } from './badge';
import { Button } from './button';

export interface RecommendationCardProps {
  title: string;
  provider: 'iGOT' | 'NSSTA' | 'PRAGYA';
  targetCompetency: string;
  duration?: string;
  difficulty?: 'Foundational' | 'Intermediate' | 'Advanced';
  explanation?: string;
  className?: string;
}

export function RecommendationCard({
  title,
  provider,
  targetCompetency,
  duration,
  difficulty = 'Intermediate',
  explanation,
  className = '',
}: RecommendationCardProps) {
  const providerColors = {
    iGOT: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    NSSTA: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
    PRAGYA: 'bg-violet-500/10 text-violet-300 border-violet-500/30',
  };

  return (
    <GlassCard variant="interactive" className={`flex flex-col justify-between gap-4 ${className}`}>
      <div className="space-y-2.5">
        <div className="flex items-center justify-between gap-2">
          <Badge className={providerColors[provider]}>{provider} Module</Badge>
          <span className="text-[11px] font-mono text-slate-400">{difficulty}</span>
        </div>

        <h4 className="text-sm font-semibold text-white leading-snug line-clamp-2">{title}</h4>

        <div className="flex items-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <BookOpen className="w-3 h-3 text-cyan-400" />
            {targetCompetency}
          </span>
          {duration && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-500" />
              {duration}
            </span>
          )}
        </div>

        {explanation && (
          <div className="p-2.5 rounded-lg bg-cyan-950/20 border border-cyan-500/20 text-[11px] text-cyan-200/90 leading-relaxed flex items-start gap-1.5">
            <Sparkles className="w-3 h-3 text-cyan-400 shrink-0 mt-0.5" />
            <span>{explanation}</span>
          </div>
        )}
      </div>

      <div className="pt-2 border-t border-white/5 flex items-center justify-between">
        <span className="text-[11px] text-slate-500">Government Portal Adapter</span>
        <Button variant="outline" size="sm" className="text-xs">
          <span>View Details</span>
          <ExternalLink className="w-3 h-3" />
        </Button>
      </div>
    </GlassCard>
  );
}
