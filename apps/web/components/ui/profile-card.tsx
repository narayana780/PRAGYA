'use client';

import React from 'react';
import { Shield, MapPin, Briefcase, Award } from 'lucide-react';
import { GlassCard } from './glass-card';

export interface ProfileCardProps {
  name: string;
  role: string;
  department: string;
  location?: string;
  avatarUrl?: string;
  verifiedStatus?: boolean;
  className?: string;
}

export function ProfileCard({
  name,
  role,
  department,
  location,
  verifiedStatus = true,
  className = '',
}: ProfileCardProps) {
  return (
    <GlassCard variant="elevated" className={`flex flex-col sm:flex-row items-start sm:items-center gap-4 ${className}`}>
      <div className="relative shrink-0">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-violet-600 p-0.5 shadow-lg shadow-cyan-500/10">
          <div className="w-full h-full rounded-[14px] bg-[#070A13] flex items-center justify-center font-bold text-lg text-cyan-300">
            {name.charAt(0)}
          </div>
        </div>
        {verifiedStatus && (
          <div className="absolute -bottom-1 -right-1 p-1 rounded-full bg-[#070A13] text-cyan-400">
            <Shield className="w-3.5 h-3.5 fill-cyan-400/20" />
          </div>
        )}
      </div>

      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <h3 className="text-base font-bold text-white tracking-tight">{name}</h3>
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
            MoSPI Cadre
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Briefcase className="w-3 h-3 text-slate-500" />
            {role}
          </span>
          <span className="flex items-center gap-1">
            <Award className="w-3 h-3 text-slate-500" />
            {department}
          </span>
          {location && (
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3 text-slate-500" />
              {location}
            </span>
          )}
        </div>
      </div>
    </GlassCard>
  );
}
