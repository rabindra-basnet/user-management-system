import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { toast } from 'react-hot-toast';
import Cookies from 'js-cookie';

// Types
export interface APIResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  details?: any;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginResponse {
  user: User;
  token: Token;
  message: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  username?: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  bio?: string;
  timezone: string;
  language: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  is_2fa_enabled: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
  roles: Role[];
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  is_system_role: boolean;
  created_at: string;
  updated_at: string;
  permissions: Permission[];
}

export interface Permission {
  id: string;
  name: string;
  description?: string;
  resource: string;
  action: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  username?: string;
  first_name: string;
  last_name: string;
  password: string;
  confirm_password: string;
  phone_number?: string;
  bio?: string;
  timezone?: string;
  language?: string;
  is_active?: boolean;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  bio?: string;
  timezone?: string;
  language?: string;
  is_active?: boolean;
}

export interface UserList {
  users: User[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

class APIClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_VERSION}`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for token refresh and error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAccessToken();
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  private handleError(error: AxiosError) {
    if (error.response?.data) {
      const errorData = error.response.data as any;
      const message = errorData.message || errorData.detail || 'An error occurred';
      
      // Don't show toast for 401 errors (handled by interceptor)
      if (error.response.status !== 401) {
        toast.error(message);
      }
    } else if (error.request) {
      toast.error('Network error. Please check your connection.');
    } else {
      toast.error('An unexpected error occurred.');
    }
  }

  private getAccessToken(): string | null {
    return Cookies.get('access_token') || localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return Cookies.get('refresh_token') || localStorage.getItem('refresh_token');
  }

  private setTokens(accessToken: string, refreshToken: string, rememberMe: boolean = false) {
    if (rememberMe) {
      // Store in cookies for persistent login
      Cookies.set('access_token', accessToken, { expires: 7, secure: true, sameSite: 'strict' });
      Cookies.set('refresh_token', refreshToken, { expires: 7, secure: true, sameSite: 'strict' });
    } else {
      // Store in localStorage for session-only
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  private clearTokens() {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private async refreshAccessToken(): Promise<string | null> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    this.refreshPromise = this.client
      .post('/auth/refresh', { refresh_token: refreshToken })
      .then((response) => {
        const { access_token } = response.data;
        
        // Update access token
        if (Cookies.get('access_token')) {
          Cookies.set('access_token', access_token, { expires: 7, secure: true, sameSite: 'strict' });
        } else {
          localStorage.setItem('access_token', access_token);
        }
        
        return access_token;
      })
      .catch(() => {
        this.clearTokens();
        return null;
      })
      .finally(() => {
        this.refreshPromise = null;
      });

    return this.refreshPromise;
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/auth/login', credentials);
    const { token } = response.data;
    
    this.setTokens(token.access_token, token.refresh_token, credentials.remember_me);
    
    return response.data;
  }

  async register(userData: UserCreate): Promise<User> {
    const response = await this.client.post<User>('/auth/register', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    
    if (refreshToken) {
      try {
        await this.client.post('/auth/logout', { refresh_token: refreshToken });
      } catch (error) {
        // Ignore logout errors
      }
    }
    
    this.clearTokens();
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  async changePassword(data: { current_password: string; new_password: string; confirm_password: string }): Promise<void> {
    await this.client.post('/auth/change-password', data);
  }

  // User management methods
  async getUsers(params: {
    skip?: number;
    limit?: number;
    search?: string;
    is_active?: boolean;
  } = {}): Promise<UserList> {
    const response = await this.client.get<UserList>('/users/', { params });
    return response.data;
  }

  async getUser(userId: string): Promise<User> {
    const response = await this.client.get<User>(`/users/${userId}`);
    return response.data;
  }

  async createUser(userData: UserCreate): Promise<User> {
    const response = await this.client.post<User>('/users/', userData);
    return response.data;
  }

  async updateUser(userId: string, userData: UserUpdate): Promise<User> {
    const response = await this.client.put<User>(`/users/${userId}`, userData);
    return response.data;
  }

  async deleteUser(userId: string): Promise<void> {
    await this.client.delete(`/users/${userId}`);
  }

  async activateUser(userId: string): Promise<void> {
    await this.client.post(`/users/${userId}/activate`);
  }

  async deactivateUser(userId: string): Promise<void> {
    await this.client.post(`/users/${userId}/deactivate`);
  }

  // Role management methods
  async getRoles(): Promise<Role[]> {
    const response = await this.client.get<Role[]>('/roles/');
    return response.data;
  }

  async getRole(roleId: string): Promise<Role> {
    const response = await this.client.get<Role>(`/roles/${roleId}`);
    return response.data;
  }

  async createRole(roleData: { name: string; description?: string; permission_ids: string[] }): Promise<Role> {
    const response = await this.client.post<Role>('/roles/', roleData);
    return response.data;
  }

  async updateRole(roleId: string, roleData: { name?: string; description?: string; permission_ids?: string[] }): Promise<Role> {
    const response = await this.client.put<Role>(`/roles/${roleId}`, roleData);
    return response.data;
  }

  async deleteRole(roleId: string): Promise<void> {
    await this.client.delete(`/roles/${roleId}`);
  }

  // Permission methods
  async getPermissions(): Promise<Permission[]> {
    const response = await this.client.get<Permission[]>('/permissions/');
    return response.data;
  }

  // Two-factor authentication
  async setup2FA(): Promise<{ secret: string; qr_code: string; backup_codes: string[] }> {
    const response = await this.client.post('/auth/2fa/setup');
    return response.data;
  }

  async verify2FA(code: string): Promise<void> {
    await this.client.post('/auth/2fa/verify', { code });
  }

  // Login with 2FA
  async login2FA(code: string): Promise<any> {
    const response = await this.client.post('/auth/login/2fa', { code });
    return response.data;
  }

  async disable2FA(password: string, code: string): Promise<void> {
    await this.client.post('/auth/2fa/disable', { password, code });
  }

  // Admin Statistics
  async getStatistics(): Promise<any> {
    const response = await this.client.get('/admin/statistics');
    return response.data;
  }

  // Audit Logs
  async getAuditLogs(params: {
    skip?: number;
    limit?: number;
    action?: string;
    status?: string;
  }): Promise<any> {
    const response = await this.client.get('/admin/audit-logs', { params });
    return response.data;
  }

  // Public getter for client (for advanced usage)
  get httpClient(): AxiosInstance {
    return this.client;
  }
}

// Create and export API client instance
export const apiClient = new APIClient();
export default apiClient;
