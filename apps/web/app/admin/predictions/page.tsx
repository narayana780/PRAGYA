'use client';

import React from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { LineChart, ArrowRight, Zap, ShieldCheck } from 'lucide-react';

export default function AdminPredictionsPage() {
  return (
    <AppShell role="ADMIN" pageTitle="Workforce Planning & Forecasting">
      <PageContainer>
        <PageHeader
          title="Predictive Workforce Analytics & Planning"
          subtitle="Forecast future cadre skill requirements, capacity pressure, and recommended training investments."
          breadcrumbs={[
            { label: 'Workforce Console', href: '/admin' },
            { label: 'Predictive Analytics' },
          ]}
        />

        <GlassCard variant="elevated" className="p-8 max-w-2xl mx-auto text-center mt-6">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto mb-4">
            <Zap className="w-6 h-6 text-cyan-400" />
          </div>

          <h2 className="text-xl font-bold text-white mb-2">
            Workforce Planning & Capacity Forecasting Active
          </h2>
          <p className="text-sm text-slate-300 mb-6 leading-relaxed">
            The deterministic workforce planning engine (Stage 17) models cadre readiness, gap pressures, emerging skill signals, and departmental capacity forecasts.
          </p>

          <Link
            href="/admin/planning"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold hover:opacity-90 transition-all shadow-lg shadow-cyan-500/20"
          >
            <span>Open Workforce Planning Console</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <div className="mt-6 pt-6 border-t border-slate-800 text-xs text-slate-500 flex items-center justify-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Deterministic MoSPI-compliant capacity modeling</span>
          </div>
        </GlassCard>
      </PageContainer>
    </AppShell>
  );
}
