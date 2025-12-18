/**
 * Messages Page
 * Full messaging interface with conversation list and chat window
 * Responsive design with mobile-first approach
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { MessageSquare } from 'lucide-react';
import { Card } from '../components/UIComponents';
import { ConversationList, ChatWindow } from '../components/messaging';
import { useWebSocket } from '../context/WebSocketContext';
import { useAuth } from '../context/AuthContext';
import { useUnreadCount } from '../context/UnreadCountContext';
import { messagingAPI } from '../services';
import type { Conversation, Message } from '../types/api';

// Map to track tempId -> optimistic message id for proper replacement
const pendingMessages = new Map<string, number>();

const Messages: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { refreshCount } = useUnreadCount();
  const {
    connect,
    disconnect,
    onNewMessage,
    onMessageSent,
    sendMessage: wsSendMessage,
    isConnected,
    connectionState,
  } = useWebSocket();

  // Track if we initiated the connection (for cleanup)
  const connectionInitiatedRef = useRef(false);

  // Connect to WebSocket on mount, disconnect on unmount
  useEffect(() => {
    // Only connect once per mount
    if (!connectionInitiatedRef.current) {
      connectionInitiatedRef.current = true;
      connect();
    }

    return () => {
      // Disconnect when leaving the messages page
      if (connectionInitiatedRef.current) {
        disconnect();
        connectionInitiatedRef.current = false;
      }
    };
  }, []); // Empty deps - only run on mount/unmount

  // Get selected conversation from URL
  const selectedConversationId = searchParams.get('conversation')
    ? parseInt(searchParams.get('conversation')!, 10)
    : null;

  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [isMobileViewingChat, setIsMobileViewingChat] = useState(false);

  // Fetch conversations
  const {
    data: conversations = [],
    isLoading: isLoadingConversations,
  } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => messagingAPI.getConversations(),
    refetchInterval: 30000, // Refresh every 30 seconds as backup
  });

  // Fetch messages for selected conversation
  const {
    data: messages = [],
    isLoading: isLoadingMessages,
  } = useQuery({
    queryKey: ['messages', selectedConversationId],
    queryFn: () => messagingAPI.getMessages(selectedConversationId!, 0, 50),
    enabled: !!selectedConversationId,
  });

  // Update selected conversation when URL changes or conversations load
  useEffect(() => {
    if (selectedConversationId && conversations.length > 0) {
      const conv = conversations.find((c) => c.id === selectedConversationId);
      if (conv) {
        setSelectedConversation(conv);
      }
    }
  }, [selectedConversationId, conversations]);

  // Send message mutation (REST API fallback)
  const sendMessageMutation = useMutation({
    mutationFn: ({ conversationId, content }: { conversationId: number; content: string }) =>
      messagingAPI.sendMessage(conversationId, { content, message_type: 'text' }),
    onSuccess: (newMessage) => {
      // Add message to cache
      queryClient.setQueryData<Message[]>(
        ['messages', selectedConversationId],
        (old = []) => [...old, newMessage]
      );
    },
    onError: () => {
      toast.error('Failed to send message. Please try again.');
    },
  });

  // Handle selecting a conversation
  const handleSelectConversation = useCallback((conversation: Conversation) => {
    setSelectedConversation(conversation);
    setSearchParams({ conversation: conversation.id.toString() });
    setIsMobileViewingChat(true);
    // Refresh unread count after a short delay to allow mark-as-read to complete
    setTimeout(() => refreshCount(), 1000);
  }, [setSearchParams, refreshCount]);

  // Handle going back (mobile)
  const handleBack = useCallback(() => {
    setIsMobileViewingChat(false);
    setSearchParams({});
    setSelectedConversation(null);
  }, [setSearchParams]);

  // Handle sending a message
  const handleSendMessage = useCallback((content: string, replyToId?: number) => {
    if (!selectedConversationId || !user) return;

    // Create unique IDs for tracking
    const tempId = `temp-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
    const optimisticId = -Date.now(); // Negative ID to distinguish from real messages

    // Track this pending message for later replacement
    pendingMessages.set(tempId, optimisticId);

    const optimisticMessage: Message = {
      id: optimisticId,
      conversation_id: selectedConversationId,
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

    // Add to cache immediately (optimistic update)
    queryClient.setQueryData<Message[]>(
      ['messages', selectedConversationId],
      (old = []) => [...old, optimisticMessage]
    );

    // Try WebSocket first, fall back to REST
    if (isConnected) {
      wsSendMessage(selectedConversationId, content, tempId);
    } else {
      // For REST fallback, clean up pending message tracking after mutation completes
      pendingMessages.delete(tempId);
      sendMessageMutation.mutate({ conversationId: selectedConversationId, content });
    }
  }, [selectedConversationId, user, isConnected, wsSendMessage, queryClient, sendMessageMutation]);

  // Subscribe to WebSocket events
  useEffect(() => {
    // Handle new messages from other users
    const unsubNew = onNewMessage((message, conversationId) => {
      // Add to messages if viewing this conversation
      if (conversationId === selectedConversationId) {
        queryClient.setQueryData<Message[]>(
          ['messages', conversationId],
          (old = []) => [...old, message]
        );
      }

      // Update conversation list unread count
      queryClient.invalidateQueries({ queryKey: ['conversations'] });

      // Show notification if not viewing this conversation
      if (conversationId !== selectedConversationId) {
        toast.info(`New message from ${message.sender?.first_name}`, {
          description: message.content.slice(0, 50) + (message.content.length > 50 ? '...' : ''),
        });
      }
    });

    // Handle message sent confirmation (replace optimistic with real)
    const unsubSent = onMessageSent((message, tempId) => {
      queryClient.setQueryData<Message[]>(
        ['messages', message.conversation_id],
        (old = []) => {
          // Find and remove the optimistic message using the tempId mapping
          const optimisticId = tempId ? pendingMessages.get(tempId) : undefined;

          let filtered: Message[];
          if (optimisticId !== undefined) {
            // Remove the specific optimistic message
            filtered = old.filter((m) => m.id !== optimisticId);
            pendingMessages.delete(tempId!);
          } else {
            // Fallback: remove any negative ID messages (optimistic messages use negative IDs)
            filtered = old.filter((m) => m.id > 0);
          }

          // Only add if not already present (prevent duplicates)
          if (!filtered.some((m) => m.id === message.id)) {
            return [...filtered, message];
          }
          return filtered;
        }
      );
    });

    return () => {
      unsubNew();
      unsubSent();
    };
  }, [selectedConversationId, onNewMessage, onMessageSent, queryClient]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 h-[calc(100vh-180px)] min-h-[500px]">
      {/* Page header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 rounded-xl bg-gradient-to-br from-primary-500 to-blue-500 text-white shadow-lg shadow-primary-500/30">
          <MessageSquare size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
          <p className="text-sm text-gray-500">
            {connectionState === 'connected' && (
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Connected
              </span>
            )}
            {connectionState === 'connecting' && (
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                Connecting...
              </span>
            )}
            {connectionState === 'reconnecting' && (
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
                Reconnecting...
              </span>
            )}
            {connectionState === 'disconnected' && (
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 bg-gray-400 rounded-full" />
                Disconnected
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Main content */}
      <Card className="h-full overflow-hidden flex">
        {/* Conversation list - hidden on mobile when viewing chat */}
        <div
          className={`
            w-full lg:w-80 xl:w-96 flex-shrink-0
            border-r border-white/30
            ${isMobileViewingChat ? 'hidden lg:block' : 'block'}
          `}
        >
          <ConversationList
            conversations={conversations}
            selectedId={selectedConversationId}
            onSelect={handleSelectConversation}
            isLoading={isLoadingConversations}
          />
        </div>

        {/* Chat window */}
        <div
          className={`
            flex-1 flex flex-col min-w-0
            ${isMobileViewingChat ? 'block' : 'hidden lg:block'}
          `}
        >
          <ChatWindow
            conversation={selectedConversation}
            messages={messages}
            isLoading={isLoadingMessages}
            onBack={handleBack}
            onSendMessage={handleSendMessage}
          />
        </div>
      </Card>
    </div>
  );
};

export default Messages;
