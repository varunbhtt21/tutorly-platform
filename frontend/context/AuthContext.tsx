/**
 * Authentication Context
 *
 * Provides authentication state and methods throughout the app using:
 * - React Query for data fetching
 * - Real API integration
 * - Token management
 * - Persistent authentication
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { authAPI, TokenManager, formatAPIError } from '../services';
import type {
  User,
  LoginRequest,
  RegisterRequest,
} from '../types/api';

// ============================================================================
// Context Type Definition
// ============================================================================

interface AuthContextType {
  // State
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;

  // Methods
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (data: RegisterRequest, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  refetchUser: () => Promise<void>;
}

// ============================================================================
// Context Creation
// ============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const queryClient = useQueryClient();

  // ==========================================================================
  // Fetch current user - React Query as single source of truth
  // ==========================================================================
  //
  // Architecture: React Query handles ALL auth state management
  // - If tokens exist, fetch user data
  // - If token is expired, axios interceptor will refresh it automatically
  // - If refresh fails, interceptor rejects and we clear tokens
  // - No separate initialization logic needed - React Query IS the initialization
  //
  const {
    data: user = null,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      // Only attempt to fetch if we have tokens
      if (!TokenManager.isAuthenticated()) {
        return null;
      }
      try {
        return await authAPI.getCurrentUser();
      } catch (err) {
        // If fetching fails (even after interceptor tried refresh), clear tokens
        console.log('[Auth] Failed to fetch user, clearing tokens');
        TokenManager.clearTokens();
        return null;
      }
    },
    retry: false, // Don't retry - axios interceptor handles token refresh
    staleTime: Infinity, // User data rarely changes during session
    gcTime: Infinity, // Keep cached data
    refetchOnWindowFocus: false, // Don't refetch on tab focus
    refetchOnMount: true, // Always fetch on mount to validate session
  });

  // ==========================================================================
  // Login Mutation
  // ==========================================================================

  const loginMutation = useMutation({
    mutationFn: ({ credentials, rememberMe }: { credentials: LoginRequest; rememberMe: boolean }) =>
      authAPI.login(credentials, rememberMe),
    onSuccess: (data) => {
      // Set user in cache
      queryClient.setQueryData(['currentUser'], data.user);
      toast.success(`Welcome back, ${data.user.first_name}!`);
    },
    onError: (error) => {
      const formattedError = formatAPIError(error);
      toast.error(formattedError.message);
    },
  });

  // ==========================================================================
  // Register Mutation
  // ==========================================================================

  const registerMutation = useMutation({
    mutationFn: ({ data, rememberMe }: { data: RegisterRequest; rememberMe: boolean }) =>
      authAPI.register(data, rememberMe),
    onSuccess: (data) => {
      // Set user in cache
      queryClient.setQueryData(['currentUser'], data.user);
      toast.success(`Welcome to Tutorly, ${data.user.first_name}!`);
    },
    onError: (error) => {
      const formattedError = formatAPIError(error);
      toast.error(formattedError.message);
    },
  });

  // ==========================================================================
  // Logout Mutation
  // ==========================================================================

  const logoutMutation = useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      // Clear user from cache
      queryClient.setQueryData(['currentUser'], null);
      // Clear all queries
      queryClient.clear();
      toast.success('Logged out successfully');
    },
    onError: (error) => {
      // Still log out on client side even if API call fails
      TokenManager.clearTokens();
      queryClient.setQueryData(['currentUser'], null);
      queryClient.clear();

      const formattedError = formatAPIError(error);
      console.error('Logout error:', formattedError.message);
    },
  });

  // ==========================================================================
  // Context Methods
  // ==========================================================================

  const login = async (email: string, password: string, rememberMe: boolean = true): Promise<void> => {
    await loginMutation.mutateAsync({ credentials: { email, password }, rememberMe });
  };

  const register = async (data: RegisterRequest, rememberMe: boolean = true): Promise<void> => {
    await registerMutation.mutateAsync({ data, rememberMe });
  };

  const logout = async (): Promise<void> => {
    await logoutMutation.mutateAsync();
  };

  const refetchUser = async (): Promise<void> => {
    await refetch();
  };

  // ==========================================================================
  // Context Value
  // ==========================================================================

  const contextValue: AuthContextType = {
    user,
    isAuthenticated: !!user && TokenManager.isAuthenticated(),
    // isLoading is true during initial fetch, isPending during mutations
    loading: isLoading || loginMutation.isPending || registerMutation.isPending,
    login,
    register,
    logout,
    refetchUser,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

// ============================================================================
// Custom Hook
// ============================================================================

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
