/**
 * Subjects API Service
 *
 * Handles all subject-related API calls.
 * Public endpoint - no authentication required.
 */

import axios from '../lib/axios';

// ============================================================================
// Types
// ============================================================================

export interface Subject {
  id: number;
  name: string;
  slug: string;
  description?: string;
  category?: string;
}

export interface SubjectListResponse {
  subjects: Subject[];
  total: number;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get all available subjects
 */
export const getSubjects = async (params?: {
  category?: string;
  active_only?: boolean;
}): Promise<SubjectListResponse> => {
  const response = await axios.get<SubjectListResponse>('/subjects', { params });
  return response.data;
};

/**
 * Get all subject categories
 */
export const getSubjectCategories = async (): Promise<string[]> => {
  const response = await axios.get<string[]>('/subjects/categories');
  return response.data;
};

/**
 * Get a specific subject by ID
 */
export const getSubject = async (subjectId: number): Promise<Subject> => {
  const response = await axios.get<Subject>(`/subjects/${subjectId}`);
  return response.data;
};

// ============================================================================
// Export
// ============================================================================

export const subjectsAPI = {
  getSubjects,
  getSubjectCategories,
  getSubject,
};
