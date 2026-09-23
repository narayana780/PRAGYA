'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, Lock, Mail, ArrowRight, Building2, CheckCircle2 } from 'lucide-react';
import { PragyaLogo } from '@/components/brand/pragya-logo';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { AIOrb } from '@/components/ui/ai-orb';

export default function LoginPage() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState('officer@mospi.gov.in');
  const [password, setPassword] = useState('••••••••••••');
  const [selectedRole, setSelectedRole] = useState<'EMPLOYEE' | 'ADMIN'>('EMPLOYEE');
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      router.push(selectedRole === 'ADMIN' ? '/admin' : '/employee');
    }, 600);
  };

  const handleSsoClick = () => {
    router.push(selectedRole === 'ADMIN' ? '/admin' : '/employee');
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#070A13] text-[#F8FAFC] pragya-bg-mesh select-none">
      {/* LEFT COLUMN: PRAGYA Brand, Animated AI Data Visual & Mission */}
      <div className="lg:w-1/2 flex flex-col justify-between p-8 md:p-12 lg:p-16 border-b lg:border-b-0 lg:border-r border-white/10 relative overflow-hidden">
        {/* Background glow orb */}
        <div className="pointer-events-none absolute -top-24 -left-24 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl" />
        <div className="pointer-events-none absolute bottom-12 right-12 w-80 h-80 bg-violet-600/15 rounded-full blur-3xl" />

        {/* Top: Logo & MoSPI Cadre Tag */}
        <div className="relative z-10 text-left">
          <PragyaLogo size="lg" showDescriptor />
          <div className="inline-flex items-center gap-2 mt-4 px-3 py-1 rounded-full glass-panel border-cyan-500/20 text-[11px] text-cyan-300 font-mono">
            <Building2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Ministry of Statistics & Programme Implementation (MoSPI)</span>
          </div>
        </div>

        {/* Middle: Data & Competency Visualization Geometric Graphic */}
        <div className="relative z-10 my-10 max-w-md text-left">
          <div className="p-6 rounded-2xl glass-panel-elevated border-white/10 relative overflow-hidden mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <AIOrb size="sm" isThinking />
                <span className="text-xs font-semibold text-white">Closed-Loop Competency Engine</span>
              </div>
              <span className="text-[10px] font-mono text-cyan-400">SIH26101</span>
            </div>

            {/* Abstract connected competency nodes graphic */}
            <div className="grid grid-cols-3 gap-2 text-center text-[10px] font-mono py-2">
              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                1. Assessment
              </div>
              <div className="p-2 rounded-lg bg-violet-500/10 border border-violet-500/30 text-violet-300">
                2. Skill Gap
              </div>
              <div className="p-2 rounded-lg bg-fuchsia-500/10 border border-fuchsia-500/30 text-fuchsia-300">
                3. Learning
              </div>
              <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-300">
                4. Recalibration
              </div>
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                5. Prediction
              </div>
              <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300">
                6. Evidence
              </div>
            </div>

            <p className="text-xs text-slate-300 mt-4 leading-relaxed">
              Evidence-based capacity building designed for India’s Official Statistical System. Not a generic LMS, but an explainable workforce intelligence platform.
            </p>
          </div>

          <div className="space-y-2 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              <span>Diagnostic, verified training & experience-backed scoring</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-violet-400" />
              <span>iGOT Karmayogi & NSSTA-TPAC ecosystem interoperability</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Workforce-level capability intelligence & gap prediction</span>
            </div>
          </div>
        </div>

        {/* Bottom Tagline */}
        <div className="relative z-10 text-left text-xs font-mono text-slate-500">
          Assess • Learn • Improve • Predict
        </div>
      </div>

      {/* RIGHT COLUMN: Login Card & Single Sign-On */}
      <div className="lg:w-1/2 flex items-center justify-center p-6 sm:p-12 lg:p-16">
        <div className="w-full max-w-md p-8 rounded-2xl glass-panel-elevated border-white/10 shadow-2xl text-left relative overflow-hidden">
          {/* Subtle accent glow */}
          <div className="pointer-events-none absolute -top-12 -right-12 w-32 h-32 bg-cyan-500/15 rounded-full blur-2xl" />

          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white tracking-tight">Welcome to PRAGYA</h2>
            <p className="text-xs text-slate-400 mt-1">
              Sign in to access your competency workspace or workforce console.
            </p>
          </div>

          {/* Role Preview Selector */}
          <div className="mb-5">
            <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">
              Choose Workspace View:
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSelectedRole('EMPLOYEE')}
                className={`py-2 px-3 rounded-lg text-xs font-medium border transition-all text-center ${
                  selectedRole === 'EMPLOYEE'
                    ? 'bg-cyan-500/20 border-cyan-400 text-cyan-200 shadow-[0_0_12px_rgba(6,182,212,0.2)]'
                    : 'bg-[#0B1021] border-white/10 text-slate-400 hover:text-slate-200'
                }`}
              >
                Employee / Learner
              </button>
              <button
                type="button"
                onClick={() => setSelectedRole('ADMIN')}
                className={`py-2 px-3 rounded-lg text-xs font-medium border transition-all text-center ${
                  selectedRole === 'ADMIN'
                    ? 'bg-violet-500/20 border-violet-400 text-violet-200 shadow-[0_0_12px_rgba(139,92,246,0.2)]'
                    : 'bg-[#0B1021] border-white/10 text-slate-400 hover:text-slate-200'
                }`}
              >
                Workforce Admin
              </button>
            </div>
          </div>

          {/* Primary Button: Sign in with Government SSO (UI Prototype Only) */}
          <div className="space-y-4">
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={handleSsoClick}
              className="w-full justify-center gap-2.5 py-3 border-cyan-500/40 text-cyan-200 hover:bg-cyan-500/10 font-medium text-xs sm:text-sm"
            >
              <Shield className="w-4 h-4 text-cyan-400" />
              <span>Sign in with Government SSO</span>
            </Button>
            <p className="text-[10px] text-center text-slate-500 italic">
              (Ecosystem integration adapter placeholder for Parichay / Jan Parichay SSO)
            </p>

            {/* Divider */}
            <div className="relative flex items-center justify-center my-4">
              <div className="w-full border-t border-white/10" />
              <span className="absolute px-3 bg-[#11182E] text-[10px] font-mono text-slate-500 uppercase">
                OR
              </span>
            </div>

            {/* Direct Credential Form */}
            <form onSubmit={handleSignIn} className="space-y-4">
              <Input
                label="Employee ID or MoSPI Email"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="officer@mospi.gov.in"
                icon={<Mail className="w-4 h-4" />}
                required
              />

              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                icon={<Lock className="w-4 h-4" />}
                required
              />

              <div className="flex items-center justify-between text-xs pt-1">
                <Checkbox label="Remember me on this device" defaultChecked />
                <button
                  type="button"
                  className="text-cyan-400 hover:text-cyan-300 transition-colors text-[11px]"
                >
                  Forgot password?
                </button>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                className="w-full justify-center gap-2 mt-2"
              >
                <span>Sign In to {selectedRole} Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </form>
          </div>

          {/* Footer Badge */}
          <div className="mt-8 pt-4 border-t border-white/5 flex items-center justify-center gap-2 text-[11px] text-slate-500 font-mono">
            <Shield className="w-3.5 h-3.5 text-cyan-500/60" />
            <span>Secure • Trusted • Government Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
}
