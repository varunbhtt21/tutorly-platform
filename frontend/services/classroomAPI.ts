/**
 * Classroom API Service
 *
 * All video classroom-related API calls:
 * - Create classroom for a session
 * - Join classroom (get meeting token)
 * - End classroom session
 * - Get classroom status
 */

import apiClient from '../lib/axios';

// ============================================================================
// Types
// ============================================================================

export interface CreateClassroomResponse {
  classroom_id: number;
  session_id: number;
  room_name: string;
  room_url: string;
  provider: string;
  status: string;
  expires_at: string | null;
}

export interface JoinClassroomResponse {
  room_url: string;
  token: string;
  room_id: string;  // Provider-specific room ID (needed for 100ms SDK)
  room_name: string;
  participant_name: string;
  participant_role: 'instructor' | 'student';
  expires_at: string;
  provider: 'daily' | 'hundredms' | 'mock';
}

export interface EndClassroomResponse {
  success: boolean;
  message: string;
}

export interface ClassroomStatusResponse {
  session_id: number;
  room_name: string;
  status: 'pending' | 'created' | 'active' | 'ended' | 'expired' | 'failed';
  is_joinable: boolean;
  provider: string;
  created_at: string;
  expires_at: string | null;
  started_at: string | null;
}

// ============================================================================
// Classroom API
// ============================================================================

export const classroomAPI = {
  /**
   * Create a classroom for a tutoring session.
   *
   * This creates the video room with the provider (Daily.co).
   * Idempotent - returns existing room if already created.
   *
   * @param sessionId - The tutoring session ID
   */
  async createClassroom(sessionId: number): Promise<CreateClassroomResponse> {
    const response = await apiClient.post<CreateClassroomResponse>(
      `/classroom/${sessionId}/create`
    );
    return response.data;
  },

  /**
   * Join a classroom and get a meeting token.
   *
   * Returns a URL with authentication token for the video call.
   * The room_url can be used directly or embedded in an iframe.
   *
   * @param sessionId - The tutoring session ID
   */
  async joinClassroom(sessionId: number): Promise<JoinClassroomResponse> {
    const response = await apiClient.post<JoinClassroomResponse>(
      `/classroom/${sessionId}/join`
    );
    return response.data;
  },

  /**
   * End a classroom session.
   *
   * Only instructors can end sessions.
   * This marks the classroom as ended and cleans up resources.
   *
   * @param sessionId - The tutoring session ID
   */
  async endClassroom(sessionId: number): Promise<EndClassroomResponse> {
    const response = await apiClient.post<EndClassroomResponse>(
      `/classroom/${sessionId}/end`
    );
    return response.data;
  },

  /**
   * Get the current status of a classroom.
   *
   * Use this to check if a classroom exists and is joinable.
   *
   * @param sessionId - The tutoring session ID
   */
  async getClassroomStatus(sessionId: number): Promise<ClassroomStatusResponse> {
    const response = await apiClient.get<ClassroomStatusResponse>(
      `/classroom/${sessionId}/status`
    );
    return response.data;
  },
};

export default classroomAPI;
