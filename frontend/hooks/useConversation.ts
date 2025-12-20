/**
 * useConversation Hook
 *
 * A reusable custom hook that encapsulates all conversation/messaging logic.
 * Provides a clean interface for real-time messaging with WebSocket support.
 *
 * Features:
 * - WebSocket connection lifecycle management
 * - Real-time message subscription
 * - Optimistic updates for instant UI feedback
 * - Conversation join/leave for presence tracking
 * - Online status tracking
 * - REST API fallback when WebSocket unavailable
 *
 * Architecture:
 * This hook follows the Custom Hooks Pattern - extracting shared stateful logic
 * that can be reused across multiple components (Messages page, Classroom, etc.)
 *
 * Usage:
 *   const { messages, sendMessage, isOnline, isConnected } = useConversation(conversationId);
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'sonner';
import { useWebSocket } from '../context/WebSocketContext';
import { useAuth } from '../context/AuthContext';
import { messagingAPI } from '../services';
import type { Message, Conversation } from '../types/api';

// Map to track tempId -> optimistic message id for proper replacement
const pendingMessages = new Map<string, number>();

interface UseConversationOptions {
  /** Whether to auto-connect WebSocket on mount (default: true) */
  autoConnect?: boolean;
  /** Whether to auto-disconnect WebSocket on unmount (default: true) */
  autoDisconnect?: boolean;
  /** Callback when a new message arrives */
  onNewMessage?: (message: Message) => void;
}

interface UseConversationReturn {
  // State
  messages: Message[];
  isLoadingMessages: boolean;
  conversation: Conversation | null;

  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionState: string;

  // Online status
  isParticipantOnline: boolean;
  onlineUsers: Set<number>;
  isUserOnline: (userId: number) => boolean;

  // Actions
  sendMessage: (content: string, replyToId?: number) => void;
  loadMessages: () => Promise<void>;
  setConversation: (conversation: Conversation | null) => void;

  // WebSocket control (for manual management)
  connect: () => void;
  disconnect: () => void;
}

export function useConversation(
  conversationId: number | null,
  options: UseConversationOptions = {}
): UseConversationReturn {
  const {
    autoConnect = true,
    autoDisconnect = true,
    onNewMessage: onNewMessageCallback,
  } = options;

  const { user } = useAuth();
  const {
    connect,
    disconnect,
    onNewMessage,
    onMessageSent,
    sendMessage: wsSendMessage,
    joinConversation,
    leaveConversation,
    isConnected,
    isConnecting,
    connectionState,
    onlineUsers,
    isUserOnline,
  } = useWebSocket();

  // Local state
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [conversation, setConversation] = useState<Conversation | null>(null);

  // Refs for tracking
  const connectionInitiatedRef = useRef(false);
  const currentConversationIdRef = useRef<number | null>(null);

  // Connect to WebSocket on mount
  useEffect(() => {
    if (autoConnect && !connectionInitiatedRef.current) {
      connectionInitiatedRef.current = true;
      connect();
    }

    return () => {
      if (autoDisconnect && connectionInitiatedRef.current) {
        disconnect();
        connectionInitiatedRef.current = false;
      }
    };
  }, [autoConnect, autoDisconnect, connect, disconnect]);

  // Join/leave conversation room when conversationId changes
  useEffect(() => {
    // Leave previous conversation
    if (currentConversationIdRef.current && currentConversationIdRef.current !== conversationId) {
      leaveConversation(currentConversationIdRef.current);
    }

    // Join new conversation
    if (conversationId && isConnected) {
      joinConversation(conversationId);
      currentConversationIdRef.current = conversationId;
    }

    return () => {
      if (currentConversationIdRef.current) {
        leaveConversation(currentConversationIdRef.current);
        currentConversationIdRef.current = null;
      }
    };
  }, [conversationId, isConnected, joinConversation, leaveConversation]);

  // Load messages from REST API
  const loadMessages = useCallback(async () => {
    if (!conversationId) return;

    setIsLoadingMessages(true);
    try {
      const msgs = await messagingAPI.getMessages(conversationId);
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast.error('Failed to load messages');
    } finally {
      setIsLoadingMessages(false);
    }
  }, [conversationId]);

  // Load messages when conversation changes
  useEffect(() => {
    if (conversationId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [conversationId, loadMessages]);

  // Subscribe to WebSocket events
  useEffect(() => {
    // Handle new messages from other users
    const unsubNew = onNewMessage((message, msgConversationId) => {
      if (msgConversationId === conversationId) {
        setMessages((prev) => {
          // Prevent duplicates
          if (prev.some((m) => m.id === message.id)) {
            return prev;
          }
          return [...prev, message];
        });

        // Call external callback if provided
        onNewMessageCallback?.(message);
      }
    });

    // Handle message sent confirmation (replace optimistic with real)
    const unsubSent = onMessageSent((message, tempId) => {
      if (message.conversation_id === conversationId) {
        setMessages((prev) => {
          // Find and remove the optimistic message using the tempId mapping
          const optimisticId = tempId ? pendingMessages.get(tempId) : undefined;

          let filtered: Message[];
          if (optimisticId !== undefined) {
            filtered = prev.filter((m) => m.id !== optimisticId);
            pendingMessages.delete(tempId!);
          } else {
            // Fallback: remove any negative ID messages (optimistic messages use negative IDs)
            filtered = prev.filter((m) => m.id > 0);
          }

          // Only add if not already present (prevent duplicates)
          if (!filtered.some((m) => m.id === message.id)) {
            return [...filtered, message];
          }
          return filtered;
        });
      }
    });

    return () => {
      unsubNew();
      unsubSent();
    };
  }, [conversationId, onNewMessage, onMessageSent, onNewMessageCallback]);

  // Send message with optimistic update
  const sendMessage = useCallback(
    (content: string, replyToId?: number) => {
      if (!conversationId || !user) return;

      // Create unique IDs for tracking
      const tempId = `temp-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
      const optimisticId = -Date.now(); // Negative ID to distinguish from real messages

      // Track this pending message for later replacement
      pendingMessages.set(tempId, optimisticId);

      const optimisticMessage: Message = {
        id: optimisticId,
        conversation_id: conversationId,
        sender: {
          id: user.id,
          first_name: user.first_name,
          last_name: user.last_name || '',
          profile_photo_url: null,
          role: user.role,
        },
        content,
        message_type: 'text',
        status: 'sent',
        reply_to_id: replyToId || null,
        created_at: new Date().toISOString(),
      };

      // Add to local state immediately (optimistic update)
      setMessages((prev) => [...prev, optimisticMessage]);

      // Try WebSocket first, fall back to REST
      if (isConnected) {
        wsSendMessage(conversationId, content, tempId);
      } else {
        // For REST fallback
        pendingMessages.delete(tempId);
        messagingAPI
          .sendMessage(conversationId, { content, message_type: 'text' })
          .then((newMessage) => {
            // Replace optimistic message with real one
            setMessages((prev) => {
              const filtered = prev.filter((m) => m.id !== optimisticId);
              return [...filtered, newMessage];
            });
          })
          .catch((error) => {
            console.error('Failed to send message:', error);
            toast.error('Failed to send message');
            // Remove optimistic message on error
            setMessages((prev) => prev.filter((m) => m.id !== optimisticId));
          });
      }
    },
    [conversationId, user, isConnected, wsSendMessage]
  );

  // Check if the other participant is online
  // Conversation has other_participant (the person you're chatting with)
  const isParticipantOnline = conversation?.other_participant
    ? onlineUsers.has(conversation.other_participant.id)
    : false;

  return {
    // State
    messages,
    isLoadingMessages,
    conversation,

    // Connection state
    isConnected,
    isConnecting,
    connectionState,

    // Online status
    isParticipantOnline,
    onlineUsers,
    isUserOnline,

    // Actions
    sendMessage,
    loadMessages,
    setConversation,

    // WebSocket control
    connect,
    disconnect,
  };
}

export default useConversation;
