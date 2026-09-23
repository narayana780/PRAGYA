'use client';

import React, { useState } from 'react';
import { Sidebar } from './sidebar';
import { TopBar } from './top-bar';
import { getNavigationForRole } from '@/lib/navigation';
import { AnimatePresence, motion } from 'framer-motion';

export interface AppShellProps {
  role: 'EMPLOYEE' | 'ADMIN';
  pageTitle?: string;
  children: React.ReactNode;
}

export function AppShell({ role, pageTitle, children }: AppShellProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigationSections = getNavigationForRole(role);

  return (
    <div className="min-h-screen bg-[#070A13] text-[#F8FAFC] flex relative overflow-x-hidden pragya-bg-mesh">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex shrink-0">
        <Sidebar
          sections={navigationSections}
          role={role}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      </div>

      {/* Mobile Drawer Navigation */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-50 md:hidden flex">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileMenuOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 28, stiffness: 250 }}
              className="relative w-64 h-full bg-[#070A13] z-10"
            >
              <Sidebar
                sections={navigationSections}
                role={role}
                isCollapsed={false}
                onToggleCollapse={() => setIsMobileMenuOpen(false)}
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Main Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0">
        <TopBar
          role={role}
          pageTitle={pageTitle}
          onMobileMenuToggle={() => setIsMobileMenuOpen(true)}
        />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
