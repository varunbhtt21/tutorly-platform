/**
 * WebSocket Context
 *
 * A thin React wrapper around the WebSocketManager singleton.
 * The actual WebSocket logic lives in WebSocketManager.ts,
 * which is outside React's render cycle for stability.
 *
 * This context:
 * - Provides React components access to WebSocket functionality
 * - Syncs manager state changes to React state for re-renders
 * - Handles cleanup on auth changes
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import { wsManager, ConnectionState, WSManagerEvent } from '../lib/WebSocketManager';
import { useAuth } from './AuthContext';
import type { Message } from '../types/api';

// ============================================================================
// Types
// ============================================================================

interface WebSocketContextType {
  // Connection state
  connectionState: ConnectionState;
  isConnected: boolean;
  isConnecting: boolean;

  // Connection control
  connect: () => void;
  disconnect: () => void;

  // Online users
  onlineUsers: Set<number>;
  isUserOnline: (userId: number) => boolean;

  // Typing indicators
  typingUsers: Map<number, Set<number>>;
  isUserTyping: (conversationId: number, userId: number) => boolean;

  // Actions
  sendMessage: (conversationId: number, content: string, tempId?: string) => void;
  markAsRead: (conversationId: number, messageId: number) => void;
  joinConversation: (conversationId: number) => void;
  leaveConversation: (conversationId: number) => void;
  startTyping: (conversationId: number) => void;
  stopTyping: (conversationId: number) => void;

  // Event subscriptions
  onNewMessage: (callback: (message: Message, conversationId: number) => void) => () => void;
  onMessageSent: (callback: (message: Message, tempId?: string) => void) => () => void;
  onMessageDelivered: (callback: (messageId: number) => void) => () => void;
  onMessageRead: (callback: (conversationId: number, messageId: number, readBy: number) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

// ============================================================================
// Provider Component
// ============================================================================

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();

  // React state that syncs with the manager
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    wsManager.getConnectionState()
  );
  const [onlineUsers, setOnlineUsers] = useState<Set<number>>(wsManager.onlineUsers);
  const [typingUsers, setTypingUsers] = useState<Map<number, Set<number>>>(new Map());

  // Subscribe to manager events
  useEffect(() => {
    const unsubscribe = wsManager.on((event: WSManagerEvent) => {
      switch (event.type) {
        case 'connectionStateChange':
          setConnectionState(event.state);
          break;

        case 'userOnline':
          setOnlineUsers(wsManager.onlineUsers);
          break;

        case 'userOffline':
          setOnlineUsers(wsManager.onlineUsers);
          break;

        case 'userTyping':
          setTypingUsers((prev) => {
            const next = new Map(prev);
            const convUsers = next.get(event.conversationId) || new Set();
            convUsers.add(event.userId);
            next.set(event.conversationId, convUsers);
            return next;
          });
          break;

        case 'userStoppedTyping':
          setTypingUsers((prev) => {
            const next = new Map(prev);
            const convUsers = next.get(event.conversationId);
            if (convUsers) {
              convUsers.delete(event.userId);
              if (convUsers.size === 0) {
                next.delete(event.conversationId);
              }
            }
            return next;
          });
          break;
      }
    });

    return unsubscribe;
  }, []);

  // Disconnect when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      wsManager.disconnect();
    }
  }, [isAuthenticated]);

  // ========================================================================
  // Stable wrapper functions (delegate to manager)
  // ========================================================================

  const connect = useCallback(() => {
    if (!isAuthenticated) {
      console.log('[WebSocket] Cannot connect: not authenticated');
      return;
    }
    wsManager.connect();
  }, [isAuthenticated]);

  const disconnect = useCallback(() => {
    wsManager.disconnect();
  }, []);

  const sendMessage = useCallback((conversationId: number, content: string, tempId?: string) => {
    wsManager.sendMessage(conversationId, content, tempId);
  }, []);

  const markAsRead = useCallback((conversationId: number, messageId: number) => {
    wsManager.markAsRead(conversationId, messageId);
  }, []);

  const joinConversation = useCallback((conversationId: number) => {
    wsManager.joinConversation(conversationId);
  }, []);

  const leaveConversation = useCallback((conversationId: number) => {
    wsManager.leaveConversation(conversationId);
  }, []);

  const startTyping = useCallback((conversationId: number) => {
    wsManager.startTyping(conversationId);
  }, []);

  const stopTyping = useCallback((conversationId: number) => {
    wsManager.stopTyping(conversationId);
  }, []);

  // ========================================================================
  // Event subscription wrappers
  // ========================================================================

  const onNewMessage = useCallback(
    (callback: (message: Message, conversationId: number) => void) => {
      return wsManager.on((event) => {
        if (event.type === 'newMessage') {
          callback(event.message, event.conversationId);
        }
      });
    },
    []
  );

  const onMessageSent = useCallback(
    (callback: (message: Message, tempId?: string) => void) => {
      return wsManager.on((event) => {
        if (event.type === 'messageSent') {
          callback(event.message, event.tempId);
        }
      });
    },
    []
  );

  const onMessageDelivered = useCallback(
    (callback: (messageId: number) => void) => {
      return wsManager.on((event) => {
        if (event.type === 'messageDelivered') {
          callback(event.messageId);
        }
      });
    },
    []
  );

  const onMessageRead = useCallback(
    (callback: (conversationId: number, messageId: number, readBy: number) => void) => {
      return wsManager.on((event) => {
        if (event.type === 'messageRead') {
          callback(event.conversationId, event.messageId, event.readBy);
        }
      });
    },
    []
  );

  // ========================================================================
  // Helper functions
  // ========================================================================

  const isUserOnline = useCallback(
    (userId: number) => onlineUsers.has(userId),
    [onlineUsers]
  );

  const isUserTyping = useCallback(
    (conversationId: number, userId: number) => {
      const convUsers = typingUsers.get(conversationId);
      return convUsers?.has(userId) ?? false;
    },
    [typingUsers]
  );

  // Derived state
  const isConnected = connectionState === 'connected';
  const isConnecting = connectionState === 'connecting' || connectionState === 'reconnecting';

  // ========================================================================
  // Context Value
  // ========================================================================

  const value: WebSocketContextType = {
    connectionState,
    isConnected,
    isConnecting,
    connect,
    disconnect,
    onlineUsers,
    isUserOnline,
    typingUsers,
    isUserTyping,
    sendMessage,
    markAsRead,
    joinConversation,
    leaveConversation,
    startTyping,
    stopTyping,
    onNewMessage,
    onMessageSent,
    onMessageDelivered,
    onMessageRead,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

// ============================================================================
// Hook
// ============================================================================

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;
