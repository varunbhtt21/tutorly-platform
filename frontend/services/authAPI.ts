/**
 * Authentication API Service
 *
 * All authentication-related API calls:
 * - Register
 * - Login
 * - Refresh token
 * - Password reset
 * - Email verification
 * - Change password
 * - Logout
 */

import apiClient, { TokenManager } from '../lib/axios';
import type {
  RegisterRequest,
  LoginRequest,
  RefreshTokenRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  EmailVerificationRequest,
  ChangePasswordRequest,
  AuthUserResponse,
  TokenResponse,
  MessageResponse,
  User,
} from '../types/api';

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
  /**
   * Register a new user
   * @param data - Registration data
   * @param rememberMe - If true, persist session across browser restarts (default: true)
   */
  async register(data: RegisterRequest, rememberMe: boolean = true): Promise<AuthUserResponse> {
    const response = await apiClient.post<AuthUserResponse>('/auth/register', data);

    // Save tokens to storage based on rememberMe preference
    TokenManager.setTokens(response.data.access_token, response.data.refresh_token, rememberMe);

    return response.data;
  },

  /**
   * Login user
   * @param data - Login credentials
   * @param rememberMe - If true, persist session across browser restarts (default: true)
   */
  async login(data: LoginRequest, rememberMe: boolean = true): Promise<AuthUserResponse> {
    const response = await apiClient.post<AuthUserResponse>('/auth/login', {
      ...data,
      remember_me: rememberMe,
    });

    // Save tokens to storage based on rememberMe preference
    TokenManager.setTokens(response.data.access_token, response.data.refresh_token, rememberMe);

    return response.data;
  },

  /**
   * Refresh access token (maintains existing storage preference)
   */
  async refreshToken(data: RefreshTokenRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', data);

    // Update tokens while maintaining storage preference
    TokenManager.updateTokens(response.data.access_token, response.data.refresh_token);

    return response.data;
  },

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>('/auth/password-reset/request', data);
    return response.data;
  },

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(data: PasswordResetConfirm): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>('/auth/password-reset/confirm', data);
    return response.data;
  },

  /**
   * Verify email address
   */
  async verifyEmail(data: EmailVerificationRequest): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>('/auth/verify-email', data);
    return response.data;
  },

  /**
   * Change password (requires authentication)
   */
  async changePassword(data: ChangePasswordRequest): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>('/auth/change-password', data);
    return response.data;
  },

  /**
   * Logout user
   */
  async logout(): Promise<MessageResponse> {
    try {
      const response = await apiClient.post<MessageResponse>('/auth/logout');
      return response.data;
    } finally {
      // Always clear tokens on logout
      TokenManager.clearTokens();
    }
  },
};
