/**
 * Axios HTTP Client Configuration
 *
 * Centralized Axios instance with:
 * - Request/response interceptors
 * - Automatic token management
 * - Error handling
 * - Request/response logging (dev mode)
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import type { APIErrorResponse } from '../types/api';

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const BACKEND_BASE_URL = API_BASE_URL.replace('/api', ''); // Remove /api suffix for static files
const REQUEST_TIMEOUT = 30000; // 30 seconds

/**
 * Get full URL for media files (images, videos) stored on the backend
 * Handles relative paths from the API (e.g., /storage/uploads/...)
 */
export const getMediaUrl = (path: string | null | undefined): string | undefined => {
  if (!path) return undefined;
  // If already a full URL, return as-is
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  // Prepend backend base URL for relative paths
  return `${BACKEND_BASE_URL}${path}`;
};

// ============================================================================
// Token Management
// ============================================================================

const STORAGE_KEY_PREFIX = 'tutorly_';
const ACCESS_TOKEN_KEY = `${STORAGE_KEY_PREFIX}access_token`;
const REFRESH_TOKEN_KEY = `${STORAGE_KEY_PREFIX}refresh_token`;
const PERSIST_KEY = `${STORAGE_KEY_PREFIX}persist_session`;

export const TokenManager = {
  /**
   * Get the appropriate storage based on persistence preference
   */
  getStorage(): Storage {
    const shouldPersist = localStorage.getItem(PERSIST_KEY) === 'true';
    return shouldPersist ? localStorage : sessionStorage;
  },

  /**
   * Get access token from storage
   */
  getAccessToken(): string | null {
    // Check both storages (localStorage takes priority if both exist)
    return localStorage.getItem(ACCESS_TOKEN_KEY) || sessionStorage.getItem(ACCESS_TOKEN_KEY);
  },

  /**
   * Get refresh token from storage
   */
  getRefreshToken(): string | null {
    // Check both storages (localStorage takes priority if both exist)
    return localStorage.getItem(REFRESH_TOKEN_KEY) || sessionStorage.getItem(REFRESH_TOKEN_KEY);
  },

  /**
   * Save tokens to appropriate storage based on rememberMe preference
   * @param accessToken - JWT access token
   * @param refreshToken - JWT refresh token
   * @param rememberMe - If true, persist tokens in localStorage; otherwise use sessionStorage
   */
  setTokens(accessToken: string, refreshToken: string, rememberMe: boolean = true): void {
    // Clear tokens from both storages first
    this.clearTokens();

    // Store persistence preference
    if (rememberMe) {
      localStorage.setItem(PERSIST_KEY, 'true');
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    } else {
      localStorage.setItem(PERSIST_KEY, 'false');
      sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  },

  /**
   * Update tokens while maintaining the same storage preference
   */
  updateTokens(accessToken: string, refreshToken: string): void {
    const shouldPersist = localStorage.getItem(PERSIST_KEY) === 'true';
    const storage = shouldPersist ? localStorage : sessionStorage;

    // Clear from both storages
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);

    // Save to appropriate storage
    storage.setItem(ACCESS_TOKEN_KEY, accessToken);
    storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  /**
   * Clear all tokens from both storages
   */
  clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(PERSIST_KEY);
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  /**
   * Check if user is authenticated (has a token)
   */
  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  },

  /**
   * Check if session should persist across browser restarts
   */
  isPersistent(): boolean {
    return localStorage.getItem(PERSIST_KEY) === 'true';
  },
};

// ============================================================================
// Axios Instance
// ============================================================================

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Request Interceptor
// ============================================================================

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add access token to headers if available
    const accessToken = TokenManager.getAccessToken();
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Log request in development mode
    if (import.meta.env.DEV) {
      console.log('[API Request]', {
        method: config.method?.toUpperCase(),
        url: config.url,
        data: config.data,
        params: config.params,
      });
    }

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// ============================================================================
// Response Interceptor
// ============================================================================

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development mode
    if (import.meta.env.DEV) {
      console.log('[API Response]', {
        status: response.status,
        url: response.config.url,
        data: response.data,
      });
    }

    return response;
  },
  async (error: AxiosError<APIErrorResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Log error in development mode
    if (import.meta.env.DEV) {
      console.error('[API Response Error]', {
        status: error.response?.status,
        url: error.config?.url,
        error: error.response?.data,
      });
    }

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = TokenManager.getRefreshToken();

      if (!refreshToken) {
        // No refresh token available, clear tokens and redirect to login
        TokenManager.clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // Attempt to refresh the token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: new_refresh_token } = response.data;

        // Save new tokens (maintain same storage preference)
        TokenManager.updateTokens(access_token, new_refresh_token);

        // Update the authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }

        // Process queued requests
        processQueue(null, access_token);

        // Retry the original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        processQueue(refreshError as Error, null);
        TokenManager.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // For all other errors, reject with formatted error
    return Promise.reject(error);
  }
);

// ============================================================================
// Error Handler Utility
// ============================================================================

export interface FormattedError {
  message: string;
  code?: string;
  status?: number;
}

/**
 * Format API errors into a consistent structure
 */
export const formatAPIError = (error: unknown): FormattedError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIErrorResponse>;

    // Extract error details
    const status = axiosError.response?.status;
    const detail = axiosError.response?.data?.detail;

    // Handle structured error response
    if (detail && typeof detail === 'object' && 'error_code' in detail) {
      return {
        message: detail.message || 'An error occurred',
        code: detail.error_code,
        status,
      };
    }

    // Handle string error response
    if (typeof detail === 'string') {
      return {
        message: detail,
        status,
      };
    }

    // Handle network errors
    if (axiosError.code === 'ECONNABORTED') {
      return {
        message: 'Request timed out. Please try again.',
        code: 'TIMEOUT',
      };
    }

    if (axiosError.code === 'ERR_NETWORK') {
      return {
        message: 'Network error. Please check your connection.',
        code: 'NETWORK_ERROR',
      };
    }

    // Default error message based on status
    if (status) {
      const statusMessages: Record<number, string> = {
        400: 'Invalid request. Please check your input.',
        401: 'Unauthorized. Please login again.',
        403: 'Access forbidden.',
        404: 'Resource not found.',
        409: 'Conflict. Resource already exists.',
        422: 'Validation error. Please check your input.',
        500: 'Server error. Please try again later.',
        502: 'Bad gateway. Please try again later.',
        503: 'Service unavailable. Please try again later.',
      };

      return {
        message: statusMessages[status] || 'An error occurred',
        status,
      };
    }

    return {
      message: axiosError.message || 'An unexpected error occurred',
    };
  }

  // Handle non-Axios errors
  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }

  return {
    message: 'An unknown error occurred',
  };
};

// ============================================================================
// Export
// ============================================================================

export default apiClient;
