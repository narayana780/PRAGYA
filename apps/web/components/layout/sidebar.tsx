'use client';

import React from 'react';
import { ChevronLeft, ChevronRight, LogOut, Shield } from 'lucide-react';
import { PragyaLogo } from '../brand/pragya-logo';
import { NavItem } from '../ui/nav-item';
import { NavSection } from '../ui/nav-section';
import { NavIcon } from './nav-icon';
import { NavSectionConfig } from '@/lib/navigation';
import Link from 'next/link';

export interface SidebarProps {
  sections: NavSectionConfig[];
  role: 'EMPLOYEE' | 'ADMIN';
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  className?: string;
}

export function Sidebar({
  sections,
  role,
  isCollapsed,
  onToggleCollapse,
  className = '',
}: SidebarProps) {
  const homeHref = role === 'ADMIN' ? '/admin' : '/employee';

  return (
    <aside
      className={`relative flex flex-col h-screen bg-[#070A13] border-r border-white/10 transition-all duration-300 select-none z-30 ${
        isCollapsed ? 'w-20' : 'w-64'
      } ${className}`}
    >
      {/* Sidebar Header with PRAGYA Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-white/10 shrink-0">
        <PragyaLogo size={isCollapsed ? 'sm' : 'md'} showDescriptor={!isCollapsed} href={homeHref} />
        <button
          type="button"
          onClick={onToggleCollapse}
          className="hidden md:flex items-center justify-center w-7 h-7 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Role Badge Indicator */}
      <div className="px-3 pt-3 pb-1">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 text-[11px] font-mono text-slate-300">
          <Shield className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          {!isCollapsed && <span className="truncate">{role} WORKSPACE</span>}
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-4 scrollbar-thin scrollbar-thumb-slate-800">
        {sections.map((section, idx) => (
          <NavSection key={idx} title={section.title} collapsed={isCollapsed}>
            {section.items.map((item) => (
              <NavItem
                key={item.href}
                label={item.label}
                href={item.href}
                icon={<NavIcon name={item.iconName} />}
                badge={item.badge}
                collapsed={isCollapsed}
              />
            ))}
          </NavSection>
        ))}
      </div>

      {/* Sidebar Footer with Logout & Security Status */}
      <div className="p-3 border-t border-white/10 shrink-0 space-y-1">
        <Link
          href="/login"
          className="flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          title={isCollapsed ? 'Exit Session' : undefined}
        >
          <LogOut className="w-4 h-4 shrink-0" />
          {!isCollapsed && <span>Exit Session</span>}
        </Link>
      </div>
    </aside>
  );
}
