import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/lib/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  login: (user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  
  // Permissions
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => 
        set({ 
          user, 
          isAuthenticated: !!user 
        }),

      setLoading: (isLoading) => 
        set({ isLoading }),

      login: (user) => 
        set({ 
          user, 
          isAuthenticated: true, 
          isLoading: false 
        }),

      logout: () => 
        set({ 
          user: null, 
          isAuthenticated: false, 
          isLoading: false 
        }),

      updateUser: (updates) => 
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null
        })),

      hasPermission: (permission) => {
        const { user } = get();
        if (!user || !user.roles) return false;
        
        // Superuser has all permissions
        if (user.is_superuser) return true;
        
        // Check if any role has the permission
        return user.roles.some(role => 
          role.permissions.some(perm => perm.name === permission)
        );
      },

      hasRole: (roleName) => {
        const { user } = get();
        if (!user || !user.roles) return false;
        
        return user.roles.some(role => role.name === roleName);
      },

      hasAnyRole: (roleNames) => {
        const { user } = get();
        if (!user || !user.roles) return false;
        
        return user.roles.some(role => roleNames.includes(role.name));
      },

      hasAnyPermission: (permissions) => {
        const { user } = get();
        if (!user || !user.roles) return false;
        
        // Superuser has all permissions
        if (user.is_superuser) return true;
        
        // Check if user has any of the specified permissions
        return permissions.some(permission => get().hasPermission(permission));
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors for easier access
export const useUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useIsLoading = () => useAuthStore((state) => state.isLoading);

// Permission hooks
export const useHasPermission = (permission: string) => 
  useAuthStore((state) => state.hasPermission(permission));

export const useHasRole = (role: string) => 
  useAuthStore((state) => state.hasRole(role));

export const useHasAnyRole = (roles: string[]) => 
  useAuthStore((state) => state.hasAnyRole(roles));

export const useHasAnyPermission = (permissions: string[]) => 
  useAuthStore((state) => state.hasAnyPermission(permissions));

// Auth actions
export const useAuthActions = () => useAuthStore((state) => ({
  setUser: state.setUser,
  setLoading: state.setLoading,
  login: state.login,
  logout: state.logout,
  updateUser: state.updateUser,
}));
