'use client';

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  UsersIcon,
  ShieldCheckIcon,
  KeyIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';
import { useUser, useHasPermission } from '@/store/auth';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

interface DashboardStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  verified_users: number;
  unverified_users: number;
  users_with_2fa: number;
  users_without_2fa: number;
}

export default function DashboardPage() {
  const user = useUser();
  const canReadUsers = useHasPermission('users.read');
  const canReadAudit = useHasPermission('audit.read');

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: async () => {
      return await apiClient.getStatistics() as DashboardStats;
    },
    enabled: canReadUsers,
  });

  const { data: recentUsers, isLoading: usersLoading } = useQuery({
    queryKey: ['recent-users'],
    queryFn: async () => {
      const response = await apiClient.getUsers({ limit: 5 });
      return response.users;
    },
    enabled: canReadUsers,
  });

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <DashboardLayout currentPath="/dashboard">
      <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user.first_name}!
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              Here's what's happening with your user management system today.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {user.is_2fa_enabled ? (
              <div className="flex items-center text-green-600">
                <CheckCircleIcon className="h-5 w-5 mr-1" />
                <span className="text-sm">2FA Enabled</span>
              </div>
            ) : (
              <div className="flex items-center text-yellow-600">
                <ExclamationTriangleIcon className="h-5 w-5 mr-1" />
                <span className="text-sm">2FA Disabled</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      {canReadUsers && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={<UsersIcon className="h-6 w-6" />}
            color="blue"
            isLoading={statsLoading}
          />
          <StatCard
            title="Active Users"
            value={stats?.active_users || 0}
            icon={<CheckCircleIcon className="h-6 w-6" />}
            color="green"
            isLoading={statsLoading}
          />
          <StatCard
            title="2FA Enabled"
            value={stats?.users_with_2fa || 0}
            icon={<ShieldCheckIcon className="h-6 w-6" />}
            color="purple"
            isLoading={statsLoading}
          />
          <StatCard
            title="Verified Users"
            value={stats?.verified_users || 0}
            icon={<KeyIcon className="h-6 w-6" />}
            color="indigo"
            isLoading={statsLoading}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Users */}
        {canReadUsers && (
          <Card title="Recent Users" className="p-6">
            {usersLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse flex space-x-4">
                    <div className="rounded-full bg-gray-200 h-10 w-10"></div>
                    <div className="flex-1 space-y-2 py-1">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {recentUsers?.map((user) => (
                  <div key={user.id} className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {user.first_name[0]}{user.last_name[0]}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {user.first_name} {user.last_name}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {user.email}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                ))}
                <div className="pt-4 border-t">
                  <Button variant="outline" className="w-full">
                    View All Users
                  </Button>
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Quick Actions */}
        <Card title="Quick Actions" className="p-6">
          <div className="space-y-4">
            {canReadUsers && (
              <Button className="w-full justify-start" variant="outline">
                <UsersIcon className="h-5 w-5 mr-2" />
                Manage Users
              </Button>
            )}
            
            <Button className="w-full justify-start" variant="outline">
              <ShieldCheckIcon className="h-5 w-5 mr-2" />
              Security Settings
            </Button>
            
            {canReadAudit && (
              <Button className="w-full justify-start" variant="outline">
                <ChartBarIcon className="h-5 w-5 mr-2" />
                View Audit Logs
              </Button>
            )}
            
            <Button className="w-full justify-start" variant="outline">
              <KeyIcon className="h-5 w-5 mr-2" />
              API Keys
            </Button>
          </div>
        </Card>
      </div>

      {/* Security Recommendations */}
      {!user.is_2fa_enabled && (
        <Card className="p-6 border-yellow-200 bg-yellow-50">
          <div className="flex items-start">
            <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mt-0.5" />
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-yellow-800">
                Security Recommendation
              </h3>
              <p className="mt-1 text-sm text-yellow-700">
                Enable two-factor authentication to secure your account. This adds an extra layer of security to prevent unauthorized access.
              </p>
              <div className="mt-3">
                <Button size="sm" variant="outline">
                  Enable 2FA
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}
      </div>
    </DashboardLayout>
  );
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'purple' | 'indigo';
  isLoading?: boolean;
}

function StatCard({ title, value, icon, color, isLoading }: StatCardProps) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    indigo: 'text-indigo-600 bg-indigo-100',
  };

  return (
    <Card className="p-6">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          {isLoading ? (
            <div className="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
          ) : (
            <p className="text-2xl font-semibold text-gray-900">{value.toLocaleString()}</p>
          )}
        </div>
      </div>
    </Card>
  );
}
