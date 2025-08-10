'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useIsAuthenticated, useIsLoading, useHasPermission, useHasRole } from '@/store/auth';
import { Spinner } from '@/components/ui/Spinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredPermissions?: string[];
  requiredRoles?: string[];
  fallbackUrl?: string;
  requireAll?: boolean; // If true, user must have ALL permissions/roles. If false, ANY will suffice.
}

export function ProtectedRoute({
  children,
  requireAuth = true,
  requiredPermissions = [],
  requiredRoles = [],
  fallbackUrl = '/login',
  requireAll = false,
}: ProtectedRouteProps) {
  const router = useRouter();
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useIsLoading();

  useEffect(() => {
    if (!isLoading && requireAuth && !isAuthenticated) {
      router.push(fallbackUrl);
    }
  }, [isAuthenticated, isLoading, requireAuth, router, fallbackUrl]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect if authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return null;
  }

  // Check permissions and roles if user is authenticated
  if (isAuthenticated && (requiredPermissions.length > 0 || requiredRoles.length > 0)) {
    return (
      <PermissionGate
        requiredPermissions={requiredPermissions}
        requiredRoles={requiredRoles}
        requireAll={requireAll}
        fallbackUrl="/unauthorized"
      >
        {children}
      </PermissionGate>
    );
  }

  return <>{children}</>;
}

interface PermissionGateProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  requiredRoles?: string[];
  requireAll?: boolean;
  fallbackUrl?: string;
}

function PermissionGate({
  children,
  requiredPermissions = [],
  requiredRoles = [],
  requireAll = false,
  fallbackUrl = '/unauthorized',
}: PermissionGateProps) {
  const router = useRouter();

  // Check permissions
  const hasRequiredPermissions = requiredPermissions.length === 0 || (
    requireAll
      ? requiredPermissions.every(permission => useHasPermission(permission))
      : requiredPermissions.some(permission => useHasPermission(permission))
  );

  // Check roles
  const hasRequiredRoles = requiredRoles.length === 0 || (
    requireAll
      ? requiredRoles.every(role => useHasRole(role))
      : requiredRoles.some(role => useHasRole(role))
  );

  const hasAccess = hasRequiredPermissions && hasRequiredRoles;

  useEffect(() => {
    if (!hasAccess) {
      router.push(fallbackUrl);
    }
  }, [hasAccess, router, fallbackUrl]);

  if (!hasAccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg
              className="h-6 w-6 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">
            You don't have permission to access this page.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

// Higher-order component for easier usage
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<ProtectedRouteProps, 'children'>
) {
  return function AuthenticatedComponent(props: P) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

// Hook for checking permissions in components
export function useRequireAuth(options?: {
  requiredPermissions?: string[];
  requiredRoles?: string[];
  requireAll?: boolean;
}) {
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useIsLoading();

  const hasRequiredPermissions = !options?.requiredPermissions?.length || (
    options.requireAll
      ? options.requiredPermissions.every(permission => useHasPermission(permission))
      : options.requiredPermissions.some(permission => useHasPermission(permission))
  );

  const hasRequiredRoles = !options?.requiredRoles?.length || (
    options.requireAll
      ? options.requiredRoles.every(role => useHasRole(role))
      : options.requiredRoles.some(role => useHasRole(role))
  );

  return {
    isAuthenticated,
    isLoading,
    hasAccess: isAuthenticated && hasRequiredPermissions && hasRequiredRoles,
    hasRequiredPermissions,
    hasRequiredRoles,
  };
}
