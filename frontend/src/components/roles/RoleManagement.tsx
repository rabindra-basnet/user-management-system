'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ShieldCheckIcon,
  UsersIcon
} from '@heroicons/react/24/outline';
import { apiClient, Role, Permission } from '@/lib/api';
import { useHasPermission } from '@/store/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { toast } from 'react-hot-toast';
import { RoleForm } from './RoleForm';

export function RoleManagement() {
  const [search, setSearch] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);

  const queryClient = useQueryClient();
  
  // Permissions
  const canCreateRoles = useHasPermission('roles.create');
  const canUpdateRoles = useHasPermission('roles.update');
  const canDeleteRoles = useHasPermission('roles.delete');

  // Fetch roles
  const { data: roles, isLoading: rolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: () => apiClient.getRoles(),
  });

  // Fetch permissions for role creation/editing
  const { data: permissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => apiClient.getPermissions(),
  });

  // Delete role mutation
  const deleteRoleMutation = useMutation({
    mutationFn: (roleId: string) => apiClient.deleteRole(roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      toast.success('Role deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete role');
    },
  });

  const handleDeleteRole = async (role: Role) => {
    if (role.is_system_role) {
      toast.error('Cannot delete system roles');
      return;
    }

    if (window.confirm(`Are you sure you want to delete the role "${role.name}"?`)) {
      deleteRoleMutation.mutate(role.id);
    }
  };

  const handleEditRole = (role: Role) => {
    setEditingRole(role);
    setShowCreateForm(true);
  };

  const handleCloseForm = () => {
    setShowCreateForm(false);
    setEditingRole(null);
  };

  const filteredRoles = roles?.filter(role =>
    role.name.toLowerCase().includes(search.toLowerCase()) ||
    role.description?.toLowerCase().includes(search.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Role Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage roles and their permissions
          </p>
        </div>
        
        {canCreateRoles && (
          <Button onClick={() => setShowCreateForm(true)}>
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Role
          </Button>
        )}
      </div>

      {/* Search */}
      <Card className="p-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search roles..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </Card>

      {/* Roles Grid */}
      {rolesLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading roles...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRoles.map((role) => (
            <Card key={role.id} className="p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {role.name}
                    </h3>
                    {role.description && (
                      <p className="text-sm text-gray-500 mt-1">
                        {role.description}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {canUpdateRoles && !role.is_system_role && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditRole(role)}
                    >
                      <PencilIcon className="h-4 w-4" />
                    </Button>
                  )}
                  
                  {canDeleteRoles && !role.is_system_role && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteRole(role)}
                      disabled={deleteRoleMutation.isPending}
                    >
                      <TrashIcon className="h-4 w-4 text-red-600" />
                    </Button>
                  )}
                </div>
              </div>

              <div className="mt-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Permissions:</span>
                  <span className="font-medium">{role.permissions.length}</span>
                </div>
                
                {role.is_system_role && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      System Role
                    </span>
                  </div>
                )}
              </div>

              {/* Permissions Preview */}
              {role.permissions.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Permissions:</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {role.permissions.slice(0, 5).map((permission) => (
                      <div
                        key={permission.id}
                        className="text-xs bg-gray-100 rounded px-2 py-1"
                      >
                        {permission.name}
                      </div>
                    ))}
                    {role.permissions.length > 5 && (
                      <div className="text-xs text-gray-500">
                        +{role.permissions.length - 5} more
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Users Count (if available) */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center text-sm text-gray-500">
                  <UsersIcon className="h-4 w-4 mr-1" />
                  <span>Users with this role</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {filteredRoles.length === 0 && !rolesLoading && (
        <div className="text-center py-8">
          <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No roles found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {search ? 'Try adjusting your search terms.' : 'Get started by creating a new role.'}
          </p>
          {canCreateRoles && !search && (
            <div className="mt-6">
              <Button onClick={() => setShowCreateForm(true)}>
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Role
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Role Form Modal */}
      {showCreateForm && (
        <RoleForm
          role={editingRole}
          permissions={permissions || []}
          onClose={handleCloseForm}
          onSuccess={() => {
            handleCloseForm();
            queryClient.invalidateQueries({ queryKey: ['roles'] });
          }}
        />
      )}
    </div>
  );
}
