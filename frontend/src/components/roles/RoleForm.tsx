'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { apiClient, Role, Permission } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Checkbox } from '@/components/ui/Checkbox';
import { toast } from 'react-hot-toast';

const roleSchema = z.object({
  name: z.string().min(1, 'Role name is required').max(50, 'Role name is too long'),
  description: z.string().optional(),
  permission_ids: z.array(z.string()).min(1, 'At least one permission is required'),
});

type RoleFormData = z.infer<typeof roleSchema>;

interface RoleFormProps {
  role?: Role | null;
  permissions: Permission[];
  onClose: () => void;
  onSuccess: () => void;
}

export function RoleForm({ role, permissions, onClose, onSuccess }: RoleFormProps) {
  const [selectedPermissions, setSelectedPermissions] = useState<Set<string>>(new Set());
  const [permissionFilter, setPermissionFilter] = useState('');

  const isEditing = !!role;

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<RoleFormData>({
    resolver: zodResolver(roleSchema),
    defaultValues: {
      name: role?.name || '',
      description: role?.description || '',
      permission_ids: role?.permissions.map(p => p.id) || [],
    },
  });

  // Initialize selected permissions
  useEffect(() => {
    if (role) {
      const permissionIds = new Set(role.permissions.map(p => p.id));
      setSelectedPermissions(permissionIds);
      setValue('permission_ids', Array.from(permissionIds));
    }
  }, [role, setValue]);

  // Create role mutation
  const createRoleMutation = useMutation({
    mutationFn: (data: { name: string; description?: string; permission_ids: string[] }) =>
      apiClient.createRole(data),
    onSuccess: () => {
      toast.success('Role created successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create role');
    },
  });

  // Update role mutation
  const updateRoleMutation = useMutation({
    mutationFn: (data: { name?: string; description?: string; permission_ids?: string[] }) =>
      apiClient.updateRole(role!.id, data),
    onSuccess: () => {
      toast.success('Role updated successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update role');
    },
  });

  const handlePermissionToggle = (permissionId: string) => {
    const newSelected = new Set(selectedPermissions);
    if (newSelected.has(permissionId)) {
      newSelected.delete(permissionId);
    } else {
      newSelected.add(permissionId);
    }
    setSelectedPermissions(newSelected);
    setValue('permission_ids', Array.from(newSelected));
  };

  const handleSelectAll = () => {
    const filteredPermissionIds = filteredPermissions.map(p => p.id);
    const newSelected = new Set([...selectedPermissions, ...filteredPermissionIds]);
    setSelectedPermissions(newSelected);
    setValue('permission_ids', Array.from(newSelected));
  };

  const handleDeselectAll = () => {
    const filteredPermissionIds = new Set(filteredPermissions.map(p => p.id));
    const newSelected = new Set(Array.from(selectedPermissions).filter(id => !filteredPermissionIds.has(id)));
    setSelectedPermissions(newSelected);
    setValue('permission_ids', Array.from(newSelected));
  };

  const onSubmit = (data: RoleFormData) => {
    if (isEditing) {
      updateRoleMutation.mutate(data);
    } else {
      createRoleMutation.mutate(data);
    }
  };

  const filteredPermissions = permissions.filter(permission =>
    permission.name.toLowerCase().includes(permissionFilter.toLowerCase()) ||
    permission.description?.toLowerCase().includes(permissionFilter.toLowerCase()) ||
    permission.resource.toLowerCase().includes(permissionFilter.toLowerCase())
  );

  // Group permissions by resource
  const groupedPermissions = filteredPermissions.reduce((acc, permission) => {
    const resource = permission.resource;
    if (!acc[resource]) {
      acc[resource] = [];
    }
    acc[resource].push(permission);
    return acc;
  }, {} as Record<string, Permission[]>);

  const isLoading = createRoleMutation.isPending || updateRoleMutation.isPending;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                {isEditing ? 'Edit Role' : 'Create New Role'}
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Role Name
                  </label>
                  <Input
                    {...register('name')}
                    error={errors.name?.message}
                    placeholder="Enter role name"
                    className="mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <Input
                    {...register('description')}
                    error={errors.description?.message}
                    placeholder="Enter role description"
                    className="mt-1"
                  />
                </div>
              </div>

              {/* Permissions Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-sm font-medium text-gray-700">
                    Permissions ({selectedPermissions.size} selected)
                  </h4>
                  <div className="flex space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleSelectAll}
                    >
                      Select All Visible
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleDeselectAll}
                    >
                      Deselect All Visible
                    </Button>
                  </div>
                </div>

                {/* Permission Filter */}
                <div className="mb-4">
                  <Input
                    type="text"
                    placeholder="Filter permissions..."
                    value={permissionFilter}
                    onChange={(e) => setPermissionFilter(e.target.value)}
                  />
                </div>

                {/* Permissions List */}
                <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-md">
                  {Object.entries(groupedPermissions).map(([resource, resourcePermissions]) => (
                    <div key={resource} className="border-b border-gray-200 last:border-b-0">
                      <div className="bg-gray-50 px-4 py-2">
                        <h5 className="text-sm font-medium text-gray-900 capitalize">
                          {resource}
                        </h5>
                      </div>
                      <div className="p-4 space-y-3">
                        {resourcePermissions.map((permission) => (
                          <div key={permission.id} className="flex items-start space-x-3">
                            <Checkbox
                              id={permission.id}
                              checked={selectedPermissions.has(permission.id)}
                              onChange={() => handlePermissionToggle(permission.id)}
                            />
                            <div className="flex-1 min-w-0">
                              <label
                                htmlFor={permission.id}
                                className="text-sm font-medium text-gray-700 cursor-pointer"
                              >
                                {permission.name}
                              </label>
                              {permission.description && (
                                <p className="text-xs text-gray-500 mt-1">
                                  {permission.description}
                                </p>
                              )}
                              <div className="flex items-center space-x-2 mt-1">
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                  {permission.action}
                                </span>
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                  {permission.resource}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {errors.permission_ids && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.permission_ids.message}
                  </p>
                )}
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  isLoading={isLoading}
                  disabled={isLoading}
                >
                  {isEditing ? 'Update Role' : 'Create Role'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
