'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { AuditLogs } from '@/components/audit/AuditLogs';

export default function AuditPage() {
  return (
    <DashboardLayout currentPath="/audit">
      <AuditLogs />
    </DashboardLayout>
  );
}
