'use client';

import React from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { EmptyState } from '@/components/ui/empty-state';
import { Users, BarChart3, TrendingUp, ShieldAlert, ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';

export default function AdminHomePage() {
  return (
    <AppShell role="ADMIN" pageTitle="Workforce Console">
      <PageContainer>
        <PageHeader
          title="Workforce Intelligence Console"
          subtitle="Understand workforce capability and plan future capacity building."
          badge={
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-violet-500/10 text-violet-300 border border-violet-500/30 font-mono">
              MoSPI Headquarters View
            </span>
          }
        />

        {/* Strategic Overview Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <GlassCard variant="glow" className="lg:col-span-2 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-violet-400 text-xs font-mono font-medium">
                <Sparkles className="w-4 h-4" />
                <span>WORKFORCE CAPABILITY AGGREGATION</span>
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Official Statistical System Capacity Planning
              </h2>
              <p className="text-xs md:text-sm text-slate-300 leading-relaxed max-w-xl">
                Aggregate real-time competency evidence across all departments and field offices. Identify systemic skill deficits, evaluate training ROI, and forecast future capability needs.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-6 mt-4 border-t border-white/5">
              <Link
                href="/admin/workforce"
                className="p-3 rounded-xl bg-white/5 hover:bg-violet-500/10 border border-white/5 hover:border-violet-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <Users className="w-4 h-4 text-violet-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">Workforce Analytics</div>
                <div className="text-[11px] text-slate-400">Aggregated competency KPIs</div>
              </Link>

              <Link
                href="/admin/departments"
                className="p-3 rounded-xl bg-white/5 hover:bg-cyan-500/10 border border-white/5 hover:border-cyan-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <BarChart3 className="w-4 h-4 text-cyan-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">Department Gaps</div>
                <div className="text-[11px] text-slate-400">Division-wise capability</div>
              </Link>

              <Link
                href="/admin/predictions"
                className="p-3 rounded-xl bg-white/5 hover:bg-fuchsia-500/10 border border-white/5 hover:border-fuchsia-500/30 transition-colors text-left"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <TrendingUp className="w-4 h-4 text-fuchsia-400" />
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                </div>
                <div className="text-xs font-semibold text-white">Predictive Planning</div>
                <div className="text-[11px] text-slate-400">Emerging skill demand</div>
              </Link>
            </div>
          </GlassCard>

          {/* Strategic Questions Card */}
          <GlassCard variant="elevated" className="flex flex-col justify-between p-6">
            <div className="space-y-3 text-left">
              <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
                <ShieldAlert className="w-4 h-4" />
                <span>ADMINISTRATOR MANDATE</span>
              </div>
              <h3 className="text-sm font-bold text-white tracking-tight">Workforce Training Answers</h3>
              <ul className="space-y-2 text-xs text-slate-300">
                <li className="flex items-start gap-1.5">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>What skills are weak across the workforce?</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>Which departments have high-priority gaps?</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>Which iGOT & NSSTA training is most effective?</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>What statistical skills are emerging in future?</span>
                </li>
              </ul>
            </div>

            <div className="mt-6 pt-4 border-t border-white/5 text-[11px] font-mono text-slate-500">
              Federated Analytics Engine
            </div>
          </GlassCard>
        </div>

        {/* Polished Empty State for Live Aggregations */}
        <div className="mt-8">
          <EmptyState
            icon={<BarChart3 className="w-6 h-6 text-violet-400" />}
            title="Workforce Intelligence Layer Ready"
            description="Aggregated workforce distributions and department gap metrics will be populated in Stage 17 (Administrator Workforce Analytics) and Stage 24 (Predictive Analytics)."
          />
        </div>
      </PageContainer>
    </AppShell>
  );
}
