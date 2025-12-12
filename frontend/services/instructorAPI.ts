/**
 * Instructor API Service
 *
 * All instructor-related API calls:
 * - Onboarding (7 steps)
 * - Profile management
 * - Search instructors
 */

import apiClient from '../lib/axios';
import type {
  OnboardingStep1Request,
  OnboardingStep1Response,
  OnboardingStep2Request,
  OnboardingStep2Response,
  OnboardingStep3Request,
  OnboardingStep3Response,
  OnboardingStep4Request,
  OnboardingStep4Response,
  OnboardingStep5Request,
  OnboardingStep5Response,
  OnboardingStep6Request,
  OnboardingStep6Response,
  OnboardingStep7Request,
  OnboardingStep7Response,
  InstructorProfile,
  InstructorSearchParams,
  InstructorSearchResponse,
  InstructorDashboardResponse,
} from '../types/api';

// ============================================================================
// Instructor API
// ============================================================================

export const instructorAPI = {
  // ==========================================================================
  // Onboarding Steps
  // ==========================================================================

  /**
   * Step 1: Basic information (about)
   */
  async onboardingStep1(data: OnboardingStep1Request): Promise<OnboardingStep1Response> {
    const response = await apiClient.post<OnboardingStep1Response>(
      '/instructor/onboarding/step-1',
      data
    );
    return response.data;
  },

  /**
   * Step 2: Profile photo upload
   */
  async onboardingStep2(data: OnboardingStep2Request): Promise<OnboardingStep2Response> {
    const response = await apiClient.post<OnboardingStep2Response>(
      '/instructor/onboarding/step-2',
      data
    );
    return response.data;
  },

  /**
   * Step 3: Bio and teaching information
   */
  async onboardingStep3(data: OnboardingStep3Request): Promise<OnboardingStep3Response> {
    const response = await apiClient.post<OnboardingStep3Response>(
      '/instructor/onboarding/step-3',
      data
    );
    return response.data;
  },

  /**
   * Step 4: Introduction video upload
   */
  async onboardingStep4(data: OnboardingStep4Request): Promise<OnboardingStep4Response> {
    const response = await apiClient.post<OnboardingStep4Response>(
      '/instructor/onboarding/step-4',
      data
    );
    return response.data;
  },

  /**
   * Step 5: Subject selection
   */
  async onboardingStep5(data: OnboardingStep5Request): Promise<OnboardingStep5Response> {
    const response = await apiClient.post<OnboardingStep5Response>(
      '/instructor/onboarding/step-5',
      data
    );
    return response.data;
  },

  /**
   * Step 6: Pricing configuration
   */
  async onboardingStep6(data: OnboardingStep6Request): Promise<OnboardingStep6Response> {
    const response = await apiClient.post<OnboardingStep6Response>(
      '/instructor/onboarding/step-6',
      data
    );
    return response.data;
  },

  /**
   * Step 7: Education and experience (final step)
   */
  async onboardingStep7(data: OnboardingStep7Request): Promise<OnboardingStep7Response> {
    const response = await apiClient.post<OnboardingStep7Response>(
      '/instructor/onboarding/step-7',
      data
    );
    return response.data;
  },

  // ==========================================================================
  // Profile Management
  // ==========================================================================

  /**
   * Get my instructor profile (requires auth + instructor role)
   */
  async getMyProfile(): Promise<InstructorProfile> {
    const response = await apiClient.get<InstructorProfile>('/instructor/profile/me');
    return response.data;
  },

  /**
   * Get instructor profile by ID (public)
   */
  async getProfileById(instructorId: number): Promise<InstructorProfile> {
    const response = await apiClient.get<InstructorProfile>(`/instructor/profile/${instructorId}`);
    return response.data;
  },

  // ==========================================================================
  // Search
  // ==========================================================================

  /**
   * Search for instructors with filters
   */
  async searchInstructors(params?: InstructorSearchParams): Promise<InstructorSearchResponse> {
    const response = await apiClient.get<InstructorSearchResponse>('/instructor/search', {
      params,
    });
    return response.data;
  },

  // ==========================================================================
  // Dashboard
  // ==========================================================================

  /**
   * Get instructor dashboard data
   * Returns profile, user info, stats, and upcoming sessions
   */
  async getDashboard(): Promise<InstructorDashboardResponse> {
    const response = await apiClient.get<InstructorDashboardResponse>('/instructor/dashboard');
    return response.data;
  },
};
