'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { UserManagement } from '@/components/users/UserManagement';

export default function UsersPage() {
  return (
    <DashboardLayout currentPath="/users">
      <UserManagement />
    </DashboardLayout>
  );
}
