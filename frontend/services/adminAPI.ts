/**
 * Admin API Service
 *
 * All admin-related API calls:
 * - Dashboard statistics
 * - Instructor management (verify, reject, suspend)
 * - User management (suspend, ban, activate)
 */

import apiClient from '../lib/axios';

// ============================================================================
// Types
// ============================================================================

export interface AdminDashboardStats {
  total_users: number;
  total_students: number;
  total_instructors: number;
  total_admins: number;
  active_users: number;
  suspended_users: number;
  banned_users: number;
  pending_instructors: number;
  verified_instructors: number;
  rejected_instructors: number;
  suspended_instructors: number;
}

export interface AdminUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  email_verified: boolean;
  created_at: string | null;
  last_login_at: string | null;
}

export interface AdminInstructorProfile {
  id: number;
  user_id: number;
  status: string;
  headline: string | null;
  bio: string | null;
  country_of_birth: string | null;
  profile_photo_url: string | null;
  intro_video_url: string | null;
  onboarding_step: number;
  is_onboarding_complete: boolean;
  created_at: string | null;
}

export interface PendingInstructor {
  profile: AdminInstructorProfile;
  user: AdminUser;
}

export interface ActionResponse {
  success: boolean;
  message: string;
}

// ============================================================================
// Admin API
// ============================================================================

export const adminAPI = {
  /**
   * Get admin dashboard statistics
   */
  async getDashboardStats(): Promise<AdminDashboardStats> {
    const response = await apiClient.get<AdminDashboardStats>('/admin/dashboard/stats');
    return response.data;
  },

  /**
   * Get all instructor profiles pending review
   */
  async getPendingInstructors(skip = 0, limit = 50): Promise<PendingInstructor[]> {
    const response = await apiClient.get<PendingInstructor[]>('/admin/instructors/pending', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get all instructors with optional status filter
   */
  async getAllInstructors(
    status?: string,
    skip = 0,
    limit = 50
  ): Promise<PendingInstructor[]> {
    const response = await apiClient.get<PendingInstructor[]>('/admin/instructors', {
      params: { status, skip, limit },
    });
    return response.data;
  },

  /**
   * Verify an instructor profile
   */
  async verifyInstructor(instructorId: number): Promise<ActionResponse> {
    const response = await apiClient.post<ActionResponse>(
      `/admin/instructors/${instructorId}/verify`
    );
    return response.data;
  },

  /**
   * Reject an instructor profile
   */
  async rejectInstructor(instructorId: number, reason: string): Promise<ActionResponse> {
    const response = await apiClient.post<ActionResponse>(
      `/admin/instructors/${instructorId}/reject`,
      { reason }
    );
    return response.data;
  },

  /**
   * Suspend an instructor profile
   */
  async suspendInstructor(instructorId: number, reason: string): Promise<ActionResponse> {
    const response = await apiClient.post<ActionResponse>(
      `/admin/instructors/${instructorId}/suspend`,
      { reason }
    );
    return response.data;
  },

  /**
   * Get all users with optional filters
   */
  async getAllUsers(
    role?: string,
    status?: string,
    skip = 0,
    limit = 50
  ): Promise<AdminUser[]> {
    const response = await apiClient.get<AdminUser[]>('/admin/users', {
      params: { role, status, skip, limit },
    });
    return response.data;
  },

  /**
   * Get a specific user by ID
   */
  async getUser(userId: number): Promise<AdminUser> {
    const response = await apiClient.get<AdminUser>(`/admin/users/${userId}`);
    return response.data;
  },

  /**
   * Suspend a user account
   */
  async suspendUser(userId: number, reason: string): Promise<ActionResponse> {
    const response = await apiClient.post<ActionResponse>(`/admin/users/${userId}/suspend`, {
      reason,
    });
    return response.data;
  },

  /**
   * Ban a user account
   */
  async banUser(userId: number, reason: string): Promise<ActionResponse> {
    const response = await apiClient.post<ActionResponse>(`/admin/users/${userId}/ban`, {
      reason,
    });
    return response.data;
  },

  /**
   * Activate a user account
   */
  async activateUser(userId: number): Promise<ActionResponse> {
    const response = await apiClient.post<ActionResponse>(`/admin/users/${userId}/activate`);
    return response.data;
  },
};
