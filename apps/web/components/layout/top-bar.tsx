'use client';

import React, { useState } from 'react';
import { Search, Bell, Globe, Menu } from 'lucide-react';
import { Dropdown } from '../ui/dropdown';
import { Drawer } from '../ui/drawer';
import { AIOrb } from '../ui/ai-orb';
import { useCurrentEmployee } from '@/hooks/use-employee';

export interface TopBarProps {
  role: 'EMPLOYEE' | 'ADMIN';
  pageTitle?: string;
  onMobileMenuToggle?: () => void;
  className?: string;
}

export function TopBar({ role, pageTitle, onMobileMenuToggle, className = '' }: TopBarProps) {
  const [isNotificationDrawerOpen, setIsNotificationDrawerOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const { data: currentEmployee } = useCurrentEmployee();

  const languageItems = [
    { id: 'en', label: 'English', onClick: () => setSelectedLanguage('English') },
    { id: 'hi', label: 'हिन्दी (Hindi)', onClick: () => setSelectedLanguage('हिन्दी') },
  ];

  const profileName =
    role === 'ADMIN'
      ? 'Dr. R. K. Verma'
      : (currentEmployee?.full_name || 'Ananya Sharma');
  const roleTitle =
    role === 'ADMIN'
      ? 'Director (Training & Capability)'
      : (currentEmployee?.designation || 'Statistical Officer');

  return (
    <header className={`h-16 bg-[#070A13]/90 backdrop-blur-md border-b border-white/10 px-4 md:px-6 flex items-center justify-between gap-4 sticky top-0 z-20 ${className}`}>
      {/* Left side: Mobile Menu Trigger + Page Context */}
      <div className="flex items-center gap-3">
        {onMobileMenuToggle && (
          <button
            type="button"
            onClick={onMobileMenuToggle}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        {pageTitle && (
          <h1 className="text-sm md:text-base font-semibold text-white tracking-tight">
            {pageTitle}
          </h1>
        )}
      </div>

      {/* Global Search Bar (GovTech intelligence search) */}
      <div className="hidden lg:flex items-center flex-1 max-w-md mx-4">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search competencies, official standards, courses, reports..."
            className="w-full bg-[#0B1021]/80 border border-white/10 rounded-xl pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-400"
          />
        </div>
      </div>

      {/* Right Actions: AI Orb, Notifications, Language, Profile */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* Abstract AI Orb status in topbar */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full glass-panel border-cyan-500/20">
          <AIOrb size="sm" />
          <span className="text-[10px] font-mono text-cyan-300">PRAGYA AI</span>
        </div>

        {/* Language Selector */}
        <Dropdown
          align="right"
          trigger={
            <button
              type="button"
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
            >
              <Globe className="w-4 h-4 text-cyan-400" />
              <span className="hidden sm:inline">{selectedLanguage}</span>
            </button>
          }
          items={languageItems}
        />

        {/* Notifications Trigger */}
        <button
          type="button"
          onClick={() => setIsNotificationDrawerOpen(true)}
          className="relative p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
          aria-label="View system notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_#06B6D4]" />
        </button>

        {/* Profile Card / Avatar */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-white/10">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-violet-600 p-[1px]">
            <div className="w-full h-full rounded-full bg-[#070A13] flex items-center justify-center font-semibold text-xs text-cyan-300">
              {profileName.charAt(0)}
            </div>
          </div>
          <div className="hidden sm:flex flex-col text-left">
            <span className="text-xs font-medium text-white truncate max-w-[130px]">
              {profileName}
            </span>
            <span className="text-[10px] text-cyan-400 truncate max-w-[130px]">
              {roleTitle}
            </span>
          </div>
        </div>
      </div>

      {/* Notifications Drawer */}
      <Drawer
        isOpen={isNotificationDrawerOpen}
        onClose={() => setIsNotificationDrawerOpen(false)}
        title="Official Notifications"
      >
        <div className="space-y-3 text-left">
          <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-xs">
            <div className="flex items-center justify-between text-cyan-300 font-semibold mb-1">
              <span>Platform Foundation Initialized</span>
              <span className="text-[10px] font-mono text-slate-500">Just now</span>
            </div>
            <p className="text-slate-300 leading-relaxed">
              PRAGYA Stage 2 Design System and AppShell verified.
            </p>
          </div>
          <div className="p-3 rounded-xl glass-panel text-xs text-slate-400">
            <div className="flex items-center justify-between text-slate-200 font-medium mb-1">
              <span>MoSPI Cadre Alignment</span>
              <span className="text-[10px] font-mono text-slate-500">2h ago</span>
            </div>
            <p>System ready for upcoming competency assessment calibration.</p>
          </div>
        </div>
      </Drawer>
    </header>
  );
}
