'use client';

import React from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { EmptyState } from '@/components/ui/empty-state';
import { Bell } from 'lucide-react';

export default function EmployeeNotificationsPage() {
  return (
    <AppShell role="EMPLOYEE" pageTitle="Notifications">
      <PageContainer>
        <PageHeader
          title="System & Cadre Notifications"
          subtitle="Alerts for required assessments, newly released statistical courses, and training calendar updates."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'Notifications' },
          ]}
        />

        <EmptyState
          icon={<Bell className="w-6 h-6 text-cyan-400" />}
          title="Notification Dispatcher Ready"
          description="Ecosystem event triggers from iGOT, NSSTA, and local training deadlines will be populated in Stage 21 (Notifications)."
        />
      </PageContainer>
    </AppShell>
  );
}
