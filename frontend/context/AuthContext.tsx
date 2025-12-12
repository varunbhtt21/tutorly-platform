/**
 * Authentication Context
 *
 * Provides authentication state and methods throughout the app using:
 * - React Query for data fetching
 * - Real API integration
 * - Token management
 * - Persistent authentication
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
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
  const [isInitialized, setIsInitialized] = useState(false);
  const [isRefreshingSession, setIsRefreshingSession] = useState(false);

  // ==========================================================================
  // Fetch current user (only if authenticated)
  // ==========================================================================

  const {
    data: user = null,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: authAPI.getCurrentUser,
    enabled: TokenManager.isAuthenticated() && isInitialized && !isRefreshingSession,
    retry: false, // Don't retry on failure
    staleTime: Infinity, // User data rarely changes
  });

  // ==========================================================================
  // Initialize auth state on mount - Try to restore session
  // ==========================================================================

  useEffect(() => {
    const initializeAuth = async () => {
      // Check if we have a refresh token (from "Keep me signed in")
      const refreshToken = TokenManager.getRefreshToken();

      if (refreshToken) {
        // Try to refresh the session silently
        setIsRefreshingSession(true);
        try {
          await authAPI.refreshToken({ refresh_token: refreshToken });
          console.log('[Auth] Session restored successfully');
        } catch (error) {
          // Refresh failed - tokens are invalid/expired
          console.log('[Auth] Session restoration failed, clearing tokens');
          TokenManager.clearTokens();
        } finally {
          setIsRefreshingSession(false);
        }
      }

      setIsInitialized(true);
    };

    initializeAuth();
  }, []);

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
    loading: isLoading || loginMutation.isPending || registerMutation.isPending || isRefreshingSession,
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
