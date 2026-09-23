'use client';

import React from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Shield, Sparkles, Activity, Layers, ArrowRight, CheckCircle2 } from 'lucide-react';
import { fetchV1Health } from '@/lib/api-client';

export default function HomePage() {
  const { data: health, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchV1Health,
    retry: 1,
  });

  return (
    <div className="flex flex-col items-center justify-center min-h-[90vh] px-4 py-12 text-center max-w-5xl mx-auto">
      {/* GovTech / MoSPI badge */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-panel border-cyan-500/20 text-xs text-cyan-300 font-medium mb-8">
        <Shield className="w-3.5 h-3.5 text-cyan-400" />
        <span>India&apos;s Official Statistical System • MoSPI Capacity Building</span>
      </div>

      {/* Main Branding */}
      <div className="relative mb-4">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-cyan-300">
          PRAGYA
        </h1>
        <div className="inline-flex items-center gap-1.5 mt-3 text-cyan-400 font-mono text-sm tracking-widest uppercase">
          <Sparkles className="w-4 h-4" />
          <span>Assess • Learn • Improve • Predict</span>
        </div>
      </div>

      <p className="max-w-2xl text-slate-300 text-lg md:text-xl font-normal leading-relaxed mt-4 mb-10">
        AI-Powered Competency-Based Personalized Learning and Workforce Intelligence Platform
      </p>

      {/* Foundation Status Card */}
      <div className="w-full max-w-md p-6 glass-panel-glow text-left mb-10 border-white/10">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium text-slate-200">System Foundation</span>
          </div>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Ready
          </span>
        </div>

        <div className="mt-4 space-y-2.5 text-xs text-slate-400">
          <div className="flex justify-between">
            <span>Architecture:</span>
            <span className="text-slate-200 font-medium">Modular Monolith + AI Abstraction</span>
          </div>
          <div className="flex justify-between">
            <span>Frontend Shell:</span>
            <span className="text-cyan-400 font-medium">Next.js App Router + Tailwind</span>
          </div>
          <div className="flex justify-between">
            <span>Backend Core:</span>
            <span className="text-cyan-400 font-medium">FastAPI + Python 3.11</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Backend API Status:</span>
            {isLoading ? (
              <span className="text-amber-400">Connecting...</span>
            ) : isError ? (
              <span className="text-slate-500">Offline / Standalone</span>
            ) : (
              <span className="text-emerald-400 font-semibold uppercase">
                {health?.status || 'Connected'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Navigation to initial views */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl">
        <Link
          href="/employee"
          className="group flex flex-col items-center justify-between p-5 rounded-xl glass-panel hover:border-cyan-500/40 transition-all duration-200 text-left"
        >
          <div className="w-full flex items-center justify-between mb-3">
            <Layers className="w-5 h-5 text-cyan-400" />
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
          <div className="w-full text-left">
            <h2 className="text-base font-semibold text-slate-100 mb-1">Employee View</h2>
            <p className="text-xs text-slate-400">&ldquo;What should I learn next?&rdquo;</p>
          </div>
        </Link>

        <Link
          href="/admin"
          className="group flex flex-col items-center justify-between p-5 rounded-xl glass-panel hover:border-violet-500/40 transition-all duration-200 text-left"
        >
          <div className="w-full flex items-center justify-between mb-3">
            <Activity className="w-5 h-5 text-violet-400" />
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-violet-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
          <div className="w-full text-left">
            <h2 className="text-base font-semibold text-slate-100 mb-1">Admin View</h2>
            <p className="text-xs text-slate-400">&ldquo;What does workforce need?&rdquo;</p>
          </div>
        </Link>

        <Link
          href="/login"
          className="group flex flex-col items-center justify-between p-5 rounded-xl glass-panel hover:border-magenta-500/40 transition-all duration-200 text-left"
        >
          <div className="w-full flex items-center justify-between mb-3">
            <Shield className="w-5 h-5 text-fuchsia-400" />
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-fuchsia-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
          <div className="w-full text-left">
            <h2 className="text-base font-semibold text-slate-100 mb-1">Authentication</h2>
            <p className="text-xs text-slate-400">RBAC Identity Gateway</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
