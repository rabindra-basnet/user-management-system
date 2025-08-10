'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { RoleManagement } from '@/components/roles/RoleManagement';

export default function RolesPage() {
  return (
    <DashboardLayout currentPath="/roles">
      <RoleManagement />
    </DashboardLayout>
  );
}
