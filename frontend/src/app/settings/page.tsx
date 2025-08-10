'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { UserSettings } from '@/components/settings/UserSettings';

export default function SettingsPage() {
  return (
    <DashboardLayout currentPath="/settings">
      <UserSettings />
    </DashboardLayout>
  );
}
