'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Code2, Shield, Users2, Sparkles } from 'lucide-react';
import type { CompetencyDomain } from '@pragya/types';

interface DomainVisualizerProps {
  domains: CompetencyDomain[];
  selectedDomain: string | null;
  onSelectDomain: (domainCode: string | null) => void;
}

export function DomainVisualizer({
  domains,
  selectedDomain,
  onSelectDomain,
}: DomainVisualizerProps) {
  const domainConfig: Record<
    string,
    { icon: React.ReactNode; color: string; border: string; glow: string; text: string }
  > = {
    STATISTICAL: {
      icon: <BarChart3 className="w-5 h-5" />,
      color: 'from-cyan-500/20 to-blue-500/10',
      border: 'border-cyan-500/40',
      glow: 'shadow-cyan-500/20',
      text: 'text-cyan-300',
    },
    TECHNICAL: {
      icon: <Code2 className="w-5 h-5" />,
      color: 'from-violet-500/20 to-purple-500/10',
      border: 'border-violet-500/40',
      glow: 'shadow-violet-500/20',
      text: 'text-violet-300',
    },
    DIGITAL_GOVERNANCE: {
      icon: <Shield className="w-5 h-5" />,
      color: 'from-emerald-500/20 to-teal-500/10',
      border: 'border-emerald-500/40',
      glow: 'shadow-emerald-500/20',
      text: 'text-emerald-300',
    },
    BEHAVIOURAL_MANAGERIAL: {
      icon: <Users2 className="w-5 h-5" />,
      color: 'from-amber-500/20 to-orange-500/10',
      border: 'border-amber-500/40',
      glow: 'shadow-amber-500/20',
      text: 'text-amber-300',
    },
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-[#0F172A]/90 to-[#070A13] border border-slate-800/90 p-6 shadow-xl">
      {/* Background ambient constellation lines */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <line x1="20%" y1="50%" x2="50%" y2="50%" stroke="#06B6D4" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="80%" y1="50%" x2="50%" y2="50%" stroke="#8B5CF6" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="50%" y1="20%" x2="50%" y2="50%" stroke="#10B981" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="50%" y1="80%" x2="50%" y2="50%" stroke="#F59E0B" strokeWidth="1" strokeDasharray="4 4" />
        </svg>
      </div>

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              PRAGYA 4-Pillar Competency Architecture
            </span>
          </div>
          {selectedDomain && (
            <button
              onClick={() => onSelectDomain(null)}
              className="text-[11px] text-cyan-400 hover:text-cyan-300 underline"
            >
              Reset Domain Filter
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {domains.map((dom) => {
            const isSelected = selectedDomain === dom.code;
            const cfg = domainConfig[dom.code] || {
              icon: <Sparkles className="w-5 h-5" />,
              color: 'from-slate-800 to-slate-900',
              border: 'border-slate-700',
              glow: 'shadow-none',
              text: 'text-slate-300',
            };

            return (
              <motion.button
                key={dom.id}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() =>
                  onSelectDomain(isSelected ? null : dom.code)
                }
                className={`p-4 rounded-xl text-left border transition-all duration-200 flex flex-col justify-between ${
                  isSelected
                    ? `bg-gradient-to-br ${cfg.color} ${cfg.border} shadow-lg ${cfg.glow} ring-1 ring-white/20`
                    : 'bg-slate-900/60 border-slate-800/90 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between w-full mb-3">
                  <div
                    className={`p-2 rounded-lg bg-slate-900/80 border ${cfg.border} ${cfg.text}`}
                  >
                    {cfg.icon}
                  </div>
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-950/80 border border-slate-800 text-slate-300">
                    {dom.competency_count} Competencies
                  </span>
                </div>

                <div>
                  <h3 className={`text-sm font-bold ${cfg.text} tracking-tight`}>
                    {dom.name}
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {dom.description}
                  </p>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>{dom.code}</span>
                  <span className={isSelected ? cfg.text : 'text-slate-500'}>
                    {isSelected ? '● Active' : 'Click to filter'}
                  </span>
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
