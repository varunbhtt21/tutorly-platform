/**
 * Student Dashboard API Service
 *
 * Handles all API calls related to student dashboard functionality.
 */

import api from '../lib/axios';

// ============================================================================
// Types
// ============================================================================

export interface UpcomingSession {
  session_id: number;
  instructor_id: number;
  instructor_name: string;
  instructor_photo_url: string | null;
  subject: string | null;
  start_at: string;
  end_at: string;
  duration_minutes: number;
  session_type: 'trial' | 'single' | 'recurring';
  status: string;
  meeting_link: string | null;
  timezone: string;
  can_join: boolean;
  can_cancel: boolean;
  can_reschedule: boolean;
  amount: number;
  currency: string;
}

export interface StudentStats {
  total_sessions_completed: number;
  total_hours_learning: number;
  current_streak_weeks: number;
  total_spent: number;
  currency: string;
  total_instructors: number;
  trial_sessions_used: number;
}

export interface MyInstructor {
  instructor_id: number;
  user_id: number;
  name: string;
  photo_url: string | null;
  headline: string | null;
  total_sessions_with: number;
  last_session_date: string | null;
  average_rating: number | null;
  regular_session_price: number | null;
  trial_session_price: number | null;
  currency: string;
}

export interface SessionHistory {
  session_id: number;
  instructor_id: number;
  instructor_name: string;
  instructor_photo_url: string | null;
  subject: string | null;
  start_at: string;
  end_at: string;
  duration_minutes: number;
  session_type: string;
  status: 'completed' | 'cancelled' | 'no_show';
  amount: number;
  currency: string;
  can_review: boolean;
  has_review: boolean;
  instructor_notes: string | null;
}

export interface PaymentHistory {
  payment_id: number;
  instructor_name: string;
  amount: number;
  currency: string;
  status: 'completed' | 'refunded' | 'failed' | 'pending' | 'processing';
  lesson_type: 'trial' | 'regular';
  payment_method: string | null;
  created_at: string;
  completed_at: string | null;
  session_id: number | null;
  session_date: string | null;
  refund_status: string | null;
}

export interface StudentDashboardResponse {
  upcoming_sessions: UpcomingSession[];
  stats: StudentStats;
  my_instructors: MyInstructor[];
  session_history: SessionHistory[];
  payment_history: PaymentHistory[];
}

// ============================================================================
// API Functions
// ============================================================================

export const studentAPI = {
  /**
   * Get complete student dashboard data
   */
  getDashboard: async (): Promise<StudentDashboardResponse> => {
    const response = await api.get<StudentDashboardResponse>('/student/dashboard');
    return response.data;
  },

  /**
   * Get only upcoming sessions
   */
  getUpcomingSessions: async (limit = 10): Promise<UpcomingSession[]> => {
    const response = await api.get<UpcomingSession[]>('/student/dashboard/upcoming-sessions', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get only student stats
   */
  getStats: async (): Promise<StudentStats> => {
    const response = await api.get<StudentStats>('/student/dashboard/stats');
    return response.data;
  },

  /**
   * Get instructors the student has worked with
   */
  getMyInstructors: async (limit = 10): Promise<MyInstructor[]> => {
    const response = await api.get<MyInstructor[]>('/student/dashboard/my-instructors', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Get session history
   */
  getSessionHistory: async (limit = 20, offset = 0): Promise<SessionHistory[]> => {
    const response = await api.get<SessionHistory[]>('/student/dashboard/session-history', {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Get payment history
   */
  getPaymentHistory: async (limit = 20, offset = 0): Promise<PaymentHistory[]> => {
    const response = await api.get<PaymentHistory[]>('/student/dashboard/payment-history', {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Cancel a session
   */
  cancelSession: async (sessionId: number, reason?: string): Promise<void> => {
    await api.post(`/session/${sessionId}/cancel`, { reason });
  },

  /**
   * Submit a review for a session
   */
  submitReview: async (sessionId: number, rating: number, comment?: string): Promise<void> => {
    await api.post(`/session/${sessionId}/review`, { rating, comment });
  },
};

export default studentAPI;
