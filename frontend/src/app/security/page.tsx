'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { SecurityTest } from '@/components/security/SecurityTest';

export default function SecurityPage() {
  return (
    <DashboardLayout currentPath="/security">
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Security Testing</h1>
          <p className="mt-1 text-sm text-gray-600">
            Test and validate the security features of the application
          </p>
        </div>
        
        <SecurityTest />
      </div>
    </DashboardLayout>
  );
}
