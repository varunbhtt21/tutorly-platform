/**
 * Unread Count Context
 *
 * Provides real-time unread message count for notification badges.
 * Integrates with WebSocket for live updates and REST API for initial fetch.
 *
 * Features:
 * - Initial fetch on authentication
 * - Real-time updates via WebSocket events
 * - Automatic increment on new messages
 * - Reset when user views messages
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import { useAuth } from './AuthContext';
import { wsManager, WSManagerEvent } from '../lib/WebSocketManager';
import { messagingAPI } from '../services';

// ============================================================================
// Types
// ============================================================================

interface UnreadCountContextType {
  /** Total unread messages across all conversations */
  unreadCount: number;
  /** Whether the count is being loaded */
  isLoading: boolean;
  /** Refresh the count from the server */
  refreshCount: () => Promise<void>;
  /** Decrement count (when user reads messages) */
  decrementCount: (amount: number) => void;
}

const UnreadCountContext = createContext<UnreadCountContextType | null>(null);

// ============================================================================
// Provider Component
// ============================================================================

interface UnreadCountProviderProps {
  children: ReactNode;
}

export const UnreadCountProvider: React.FC<UnreadCountProviderProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch unread count from server
  const refreshCount = useCallback(async () => {
    if (!isAuthenticated) {
      setUnreadCount(0);
      return;
    }

    setIsLoading(true);
    try {
      const count = await messagingAPI.getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('[UnreadCount] Failed to fetch count:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Decrement count when user reads messages
  const decrementCount = useCallback((amount: number) => {
    setUnreadCount((prev) => Math.max(0, prev - amount));
  }, []);

  // Fetch count on authentication change
  useEffect(() => {
    if (isAuthenticated) {
      refreshCount();
    } else {
      setUnreadCount(0);
    }
  }, [isAuthenticated, refreshCount]);

  // Subscribe to WebSocket events for real-time updates
  useEffect(() => {
    if (!isAuthenticated) return;

    const unsubscribe = wsManager.on((event: WSManagerEvent) => {
      switch (event.type) {
        case 'newMessage':
          // Increment count when we receive a new message from someone else
          setUnreadCount((prev) => prev + 1);
          break;

        case 'authenticated':
          // Refresh count when WebSocket connects/reconnects
          refreshCount();
          break;
      }
    });

    return unsubscribe;
  }, [isAuthenticated, refreshCount]);

  // Periodically refresh count as backup (every 60 seconds)
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      refreshCount();
    }, 60000);

    return () => clearInterval(interval);
  }, [isAuthenticated, refreshCount]);

  // ========================================================================
  // Context Value
  // ========================================================================

  const value: UnreadCountContextType = {
    unreadCount,
    isLoading,
    refreshCount,
    decrementCount,
  };

  return (
    <UnreadCountContext.Provider value={value}>
      {children}
    </UnreadCountContext.Provider>
  );
};

// ============================================================================
// Hook
// ============================================================================

export const useUnreadCount = (): UnreadCountContextType => {
  const context = useContext(UnreadCountContext);
  if (!context) {
    throw new Error('useUnreadCount must be used within an UnreadCountProvider');
  }
  return context;
};

export default UnreadCountContext;
