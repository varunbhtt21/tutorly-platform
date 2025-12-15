/**
 * Messaging API Service
 *
 * All messaging-related API calls:
 * - Conversations
 * - Messages
 * - Feature access
 * - Unread counts
 */

import apiClient from '../lib/axios';
import type {
  Conversation,
  Message,
  FeatureAccess,
  UnreadCountResponse,
  StartConversationRequest,
  SendMessageRequest,
  MarkReadRequest,
} from '../types/api';

// ============================================================================
// Messaging API
// ============================================================================

export const messagingAPI = {
  // ========================================================================
  // Conversations
  // ========================================================================

  /**
   * Get all conversations for current user
   * @param skip - Number to skip (pagination)
   * @param limit - Max to return
   */
  async getConversations(skip: number = 0, limit: number = 50): Promise<Conversation[]> {
    const response = await apiClient.get<Conversation[]>('/messaging/conversations', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Get a specific conversation
   * @param conversationId - Conversation ID
   */
  async getConversation(conversationId: number): Promise<Conversation> {
    const response = await apiClient.get<Conversation>(
      `/messaging/conversations/${conversationId}`
    );
    return response.data;
  },

  /**
   * Start a new conversation or get existing one
   * @param data - Contains recipient_id
   */
  async startConversation(data: StartConversationRequest): Promise<Conversation> {
    const response = await apiClient.post<Conversation>('/messaging/conversations', data);
    return response.data;
  },

  // ========================================================================
  // Messages
  // ========================================================================

  /**
   * Get messages for a conversation
   * @param conversationId - Conversation ID
   * @param skip - Number to skip (pagination)
   * @param limit - Max to return
   */
  async getMessages(
    conversationId: number,
    skip: number = 0,
    limit: number = 50
  ): Promise<Message[]> {
    const response = await apiClient.get<Message[]>(
      `/messaging/conversations/${conversationId}/messages`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  /**
   * Send a message in a conversation
   * @param conversationId - Conversation ID
   * @param data - Message content and optional type/reply_to
   */
  async sendMessage(conversationId: number, data: SendMessageRequest): Promise<Message> {
    const response = await apiClient.post<Message>(
      `/messaging/conversations/${conversationId}/messages`,
      data
    );
    return response.data;
  },

  /**
   * Mark messages as read up to a certain message
   * @param conversationId - Conversation ID
   * @param data - Contains message_id
   */
  async markRead(
    conversationId: number,
    data: MarkReadRequest
  ): Promise<{ updated_count: number }> {
    const response = await apiClient.put<{ updated_count: number }>(
      `/messaging/conversations/${conversationId}/read`,
      data
    );
    return response.data;
  },

  // ========================================================================
  // Feature Access & Counts
  // ========================================================================

  /**
   * Check what messaging features are available with another user
   * Based on whether a session has been booked
   * @param otherUserId - The other user's ID
   */
  async getFeatureAccess(otherUserId: number): Promise<FeatureAccess> {
    const response = await apiClient.get<FeatureAccess>(
      `/messaging/feature-access/${otherUserId}`
    );
    return response.data;
  },

  /**
   * Get total unread message count (for notification badge)
   */
  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<UnreadCountResponse>('/messaging/unread-count');
    return response.data.unread_count;
  },

  /**
   * Check if a user is online
   * @param userId - User ID to check
   */
  async checkUserOnline(userId: number): Promise<boolean> {
    const response = await apiClient.get<{ user_id: number; online: boolean }>(
      `/online/${userId}`
    );
    return response.data.online;
  },
};

export default messagingAPI;
