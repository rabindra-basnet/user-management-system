'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { ExclamationTriangleIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Access Denied</h2>
          <p className="mt-2 text-sm text-gray-600">
            You don't have permission to access the requested page.
          </p>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            If you believe this is an error, please contact your administrator or try logging in with a different account.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              variant="outline"
              onClick={() => router.back()}
              leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
            >
              Go Back
            </Button>
            
            <Button
              onClick={() => router.push('/dashboard')}
            >
              Go to Dashboard
            </Button>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <p className="text-xs text-gray-400">
            If you need additional permissions, please contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  );
}
