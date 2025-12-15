/**
 * WebSocket Manager - Singleton Pattern
 *
 * This class manages WebSocket connections outside of React's render cycle.
 * Benefits:
 * - No re-renders affect the connection
 * - Single source of truth for connection state
 * - Event-driven architecture with typed events
 * - Automatic reconnection with exponential backoff
 *
 * Usage:
 * - Import the singleton: import { wsManager } from './lib/WebSocketManager'
 * - Connect: wsManager.connect(token)
 * - Subscribe to events: wsManager.on('message', callback)
 * - Send messages: wsManager.send({ type: 'send_message', ... })
 */

import type { Message, WSEvent } from '../types/api';
import { TokenManager } from './axios';

// ============================================================================
// Types
// ============================================================================

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'reconnecting';

export type WSManagerEvent =
  | { type: 'connectionStateChange'; state: ConnectionState }
  | { type: 'authenticated'; userId: number }
  | { type: 'newMessage'; message: Message; conversationId: number }
  | { type: 'messageSent'; message: Message; tempId?: string }
  | { type: 'messageDelivered'; messageId: number }
  | { type: 'messageRead'; conversationId: number; messageId: number; readBy: number }
  | { type: 'userTyping'; conversationId: number; userId: number }
  | { type: 'userStoppedTyping'; conversationId: number; userId: number }
  | { type: 'userOnline'; userId: number }
  | { type: 'userOffline'; userId: number }
  | { type: 'error'; message: string };

type EventCallback = (event: WSManagerEvent) => void;

// ============================================================================
// Configuration
// ============================================================================

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api';
const INITIAL_RECONNECT_DELAY = 1000;
const MAX_RECONNECT_DELAY = 30000;
const MAX_RECONNECT_ATTEMPTS = 10;

// ============================================================================
// WebSocket Manager Class
// ============================================================================

class WebSocketManager {
  private static instance: WebSocketManager | null = null;

  private ws: WebSocket | null = null;
  private connectionState: ConnectionState = 'disconnected';
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private listeners: Set<EventCallback> = new Set();
  private connectionRequested = false;

  // Online users and typing tracking
  private _onlineUsers: Set<number> = new Set();
  private _typingUsers: Map<number, Set<number>> = new Map();

  private constructor() {
    // Private constructor for singleton
  }

  /**
   * Get the singleton instance
   */
  public static getInstance(): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager();
    }
    return WebSocketManager.instance;
  }

  // ========================================================================
  // Public API
  // ========================================================================

  /**
   * Get current connection state
   */
  public getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.connectionState === 'connected';
  }

  /**
   * Get online users
   */
  public get onlineUsers(): Set<number> {
    return new Set(this._onlineUsers);
  }

  /**
   * Check if a user is online
   */
  public isUserOnline(userId: number): boolean {
    return this._onlineUsers.has(userId);
  }

  /**
   * Get typing users for a conversation
   */
  public getTypingUsers(conversationId: number): Set<number> {
    return new Set(this._typingUsers.get(conversationId) || []);
  }

  /**
   * Check if a user is typing in a conversation
   */
  public isUserTyping(conversationId: number, userId: number): boolean {
    const users = this._typingUsers.get(conversationId);
    return users?.has(userId) ?? false;
  }

  /**
   * Subscribe to WebSocket events
   */
  public on(callback: EventCallback): () => void {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Connect to WebSocket server
   */
  public connect(): void {
    if (this.connectionRequested) {
      console.log('[WSManager] Connection already requested');
      return;
    }

    const token = TokenManager.getAccessToken();
    if (!token) {
      console.log('[WSManager] No token available');
      return;
    }

    this.connectionRequested = true;
    this.reconnectAttempts = 0;
    this.createConnection();
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    if (!this.connectionRequested) {
      return;
    }

    console.log('[WSManager] Disconnecting...');
    this.connectionRequested = false;

    // Clear reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    // Close WebSocket
    if (this.ws) {
      this.ws.close(1000, 'User disconnected');
      this.ws = null;
    }

    this.setConnectionState('disconnected');
    this._onlineUsers.clear();
    this._typingUsers.clear();
  }

  /**
   * Send a message through WebSocket
   */
  public send(data: object): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
      return true;
    }
    console.warn('[WSManager] Cannot send: not connected');
    return false;
  }

  // Convenience methods for common actions

  public sendMessage(conversationId: number, content: string, tempId?: string): void {
    this.send({
      type: 'send_message',
      conversation_id: conversationId,
      content,
      message_type: 'text',
      temp_id: tempId,
    });
  }

  public markAsRead(conversationId: number, messageId: number): void {
    this.send({
      type: 'mark_read',
      conversation_id: conversationId,
      message_id: messageId,
    });
  }

  public joinConversation(conversationId: number): void {
    this.send({
      type: 'join_conversation',
      conversation_id: conversationId,
    });
  }

  public leaveConversation(conversationId: number): void {
    this.send({
      type: 'leave_conversation',
      conversation_id: conversationId,
    });
  }

  public startTyping(conversationId: number): void {
    this.send({
      type: 'typing_start',
      conversation_id: conversationId,
    });
  }

  public stopTyping(conversationId: number): void {
    this.send({
      type: 'typing_stop',
      conversation_id: conversationId,
    });
  }

  // ========================================================================
  // Private Methods
  // ========================================================================

  private setConnectionState(state: ConnectionState): void {
    if (this.connectionState !== state) {
      this.connectionState = state;
      this.emit({ type: 'connectionStateChange', state });
    }
  }

  private emit(event: WSManagerEvent): void {
    this.listeners.forEach((callback) => {
      try {
        callback(event);
      } catch (error) {
        console.error('[WSManager] Error in event callback:', error);
      }
    });
  }

  private createConnection(): void {
    const token = TokenManager.getAccessToken();
    if (!token) {
      console.log('[WSManager] No token available');
      return;
    }

    // Prevent duplicate connections
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WSManager] Already connected');
      this.setConnectionState('connected');
      return;
    }

    if (this.ws?.readyState === WebSocket.CONNECTING) {
      console.log('[WSManager] Already connecting');
      return;
    }

    this.setConnectionState(
      this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting'
    );

    try {
      console.log('[WSManager] Creating connection...');
      const ws = new WebSocket(`${WS_BASE_URL}/ws?token=${token}`);

      ws.onopen = () => {
        if (this.ws === ws) {
          console.log('[WSManager] Connected');
          this.setConnectionState('connected');
          this.reconnectAttempts = 0;
        } else {
          // Stale connection
          ws.close(1000, 'Stale connection');
        }
      };

      ws.onclose = (event) => {
        console.log('[WSManager] Disconnected', event.code, event.reason);

        if (this.ws === ws) {
          this.ws = null;

          // Reconnect if needed
          if (this.connectionRequested && event.code !== 1000 && event.code !== 4001) {
            this.scheduleReconnect();
          } else {
            this.setConnectionState('disconnected');
          }
        }
      };

      ws.onerror = (error) => {
        console.error('[WSManager] Error', error);
      };

      ws.onmessage = (event) => {
        try {
          const data: WSEvent = JSON.parse(event.data);
          this.handleServerEvent(data);
        } catch (e) {
          console.error('[WSManager] Failed to parse message', e);
        }
      };

      this.ws = ws;
    } catch (error) {
      console.error('[WSManager] Connection error', error);
      this.setConnectionState('disconnected');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.log('[WSManager] Max reconnect attempts reached');
      this.setConnectionState('disconnected');
      this.connectionRequested = false;
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      INITIAL_RECONNECT_DELAY * Math.pow(2, this.reconnectAttempts - 1),
      MAX_RECONNECT_DELAY
    );

    console.log(`[WSManager] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.setConnectionState('reconnecting');

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.createConnection();
    }, delay);
  }

  private handleServerEvent(event: WSEvent): void {
    switch (event.type) {
      case 'connected':
        this.emit({ type: 'authenticated', userId: event.user_id });
        console.log('[WSManager] Authenticated as user', event.user_id);
        break;

      case 'new_message':
        this.emit({
          type: 'newMessage',
          message: event.message,
          conversationId: event.message.conversation_id,
        });
        break;

      case 'message_sent':
        this.emit({
          type: 'messageSent',
          message: event.message,
          tempId: event.temp_id,
        });
        break;

      case 'message_delivered':
        this.emit({
          type: 'messageDelivered',
          messageId: event.message_id,
        });
        break;

      case 'message_read':
        this.emit({
          type: 'messageRead',
          conversationId: event.conversation_id,
          messageId: event.message_id,
          readBy: event.read_by,
        });
        break;

      case 'user_typing': {
        const convUsers = this._typingUsers.get(event.conversation_id) || new Set();
        convUsers.add(event.user_id);
        this._typingUsers.set(event.conversation_id, convUsers);
        this.emit({
          type: 'userTyping',
          conversationId: event.conversation_id,
          userId: event.user_id,
        });
        break;
      }

      case 'user_stopped_typing': {
        const convUsers = this._typingUsers.get(event.conversation_id);
        if (convUsers) {
          convUsers.delete(event.user_id);
          if (convUsers.size === 0) {
            this._typingUsers.delete(event.conversation_id);
          }
        }
        this.emit({
          type: 'userStoppedTyping',
          conversationId: event.conversation_id,
          userId: event.user_id,
        });
        break;
      }

      case 'user_online':
        this._onlineUsers.add(event.user_id);
        this.emit({ type: 'userOnline', userId: event.user_id });
        break;

      case 'user_offline':
        this._onlineUsers.delete(event.user_id);
        this.emit({ type: 'userOffline', userId: event.user_id });
        break;

      case 'error':
        this.emit({ type: 'error', message: event.message });
        console.error('[WSManager] Server error:', event.message);
        break;
    }
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const wsManager = WebSocketManager.getInstance();
export default wsManager;
