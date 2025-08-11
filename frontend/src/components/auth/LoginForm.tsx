'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'react-hot-toast';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { apiClient, LoginRequest } from '@/lib/api';
import { useAuthActions } from '@/store/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Checkbox } from '@/components/ui/Checkbox';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  remember_me: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

export function LoginForm({ onSuccess, redirectTo = '/dashboard' }: LoginFormProps) {
  const router = useRouter();
  const { login } = useAuthActions();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [show2FA, setShow2FA] = useState(false);
  const [tempToken, setTempToken] = useState<string>('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      remember_me: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    
    try {
      const response = await apiClient.login(data);
      
      // Check if 2FA is required
      if (response.message === 'Two-factor authentication required') {
        setShow2FA(true);
        setTempToken(response.token.access_token);
        toast.success('Please enter your 2FA code');
        return;
      }
      
      // Normal login success
      login(response.user);
      toast.success('Login successful!');
      
      if (onSuccess) {
        onSuccess();
      } else {
        router.push(redirectTo);
      }
    } catch (error: any) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FASubmit = async (code: string) => {
    setIsLoading(true);
    
    try {
      // Set temporary token for 2FA verification
      const originalToken = localStorage.getItem('access_token');
      localStorage.setItem('access_token', tempToken);
      
      const response = await apiClient.login2FA(code);

      // Update with real tokens
      const { user, token } = response;
      localStorage.setItem('access_token', token.access_token);
      localStorage.setItem('refresh_token', token.refresh_token);
      
      login(user);
      toast.success('Login successful!');
      
      if (onSuccess) {
        onSuccess();
      } else {
        router.push(redirectTo);
      }
    } catch (error: any) {
      console.error('2FA verification error:', error);
      toast.error(error.response?.data?.detail || '2FA verification failed');
      
      // Restore original token or clear
      const originalToken = localStorage.getItem('access_token');
      if (originalToken && originalToken !== tempToken) {
        localStorage.setItem('access_token', originalToken);
      } else {
        localStorage.removeItem('access_token');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (show2FA) {
    return <TwoFactorForm onSubmit={handle2FASubmit} isLoading={isLoading} onBack={() => setShow2FA(false)} />;
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Sign in to your account</h2>
        <p className="mt-2 text-sm text-gray-600">
          Enter your credentials to access the user management system
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email address
          </label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            {...register('email')}
            error={errors.email?.message}
            placeholder="Enter your email"
            className="mt-1"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <div className="relative mt-1">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              {...register('password')}
              error={errors.password?.message}
              placeholder="Enter your password"
              className="pr-10"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 flex items-center pr-3"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Checkbox
            id="remember_me"
            {...register('remember_me')}
            label="Remember me"
          />
          
          <a
            href="/forgot-password"
            className="text-sm text-blue-600 hover:text-blue-500"
          >
            Forgot your password?
          </a>
        </div>

        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
          disabled={isLoading}
        >
          {isLoading ? 'Signing in...' : 'Sign in'}
        </Button>
      </form>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Don't have an account?{' '}
          <a href="/register" className="font-medium text-blue-600 hover:text-blue-500">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}

// Two-Factor Authentication Form Component
interface TwoFactorFormProps {
  onSubmit: (code: string) => void;
  isLoading: boolean;
  onBack: () => void;
}

function TwoFactorForm({ onSubmit, isLoading, onBack }: TwoFactorFormProps) {
  const [code, setCode] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length === 6) {
      onSubmit(code);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Two-Factor Authentication</h2>
        <p className="mt-2 text-sm text-gray-600">
          Enter the 6-digit code from your authenticator app
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="code" className="block text-sm font-medium text-gray-700">
            Authentication Code
          </label>
          <Input
            id="code"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="000000"
            className="mt-1 text-center text-2xl tracking-widest"
            maxLength={6}
            autoComplete="one-time-code"
          />
        </div>

        <div className="flex space-x-3">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onBack}
            disabled={isLoading}
          >
            Back
          </Button>
          
          <Button
            type="submit"
            className="flex-1"
            isLoading={isLoading}
            disabled={isLoading || code.length !== 6}
          >
            {isLoading ? 'Verifying...' : 'Verify'}
          </Button>
        </div>
      </form>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Lost your device?{' '}
          <a href="/support" className="font-medium text-blue-600 hover:text-blue-500">
            Contact support
          </a>
        </p>
      </div>
    </div>
  );
}
