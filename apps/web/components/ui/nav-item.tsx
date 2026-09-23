'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

export interface NavItemProps {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: string | number;
  collapsed?: boolean;
}

export function NavItem({ label, href, icon, badge, collapsed = false }: NavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href || (href !== '/employee' && href !== '/admin' && pathname.startsWith(href));

  return (
    <Link
      href={href}
      title={collapsed ? label : undefined}
      className={`relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 select-none group focus-visible:ring-2 focus-visible:ring-cyan-400 ${
        isActive
          ? 'text-cyan-200 font-semibold'
          : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
      }`}
    >
      {isActive && (
        <motion.div
          layoutId="activeNavHighlight"
          className="absolute inset-0 rounded-xl bg-cyan-500/15 border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]"
          transition={{ type: 'spring', stiffness: 450, damping: 35 }}
        />
      )}

      <div className={`relative z-10 shrink-0 ${isActive ? 'text-cyan-300' : 'text-slate-400 group-hover:text-slate-200'}`}>
        {icon}
      </div>

      {!collapsed && (
        <div className="relative z-10 flex-1 flex items-center justify-between overflow-hidden">
          <span className="truncate">{label}</span>
          {badge !== undefined && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
              {badge}
            </span>
          )}
        </div>
      )}
    </Link>
  );
}
