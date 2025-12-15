/**
 * ChatWindow Component
 * Main chat area with messages, typing indicators,
 * and real-time updates
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { format, isToday, isYesterday, isSameDay } from 'date-fns';
import {
  ArrowLeft,
  Phone,
  Video,
  MoreVertical,
  Loader2,
  MessageCircle,
  Circle,
} from 'lucide-react';
import type { Conversation, Message } from '../../types/api';
import { useWebSocket } from '../../context/WebSocketContext';
import { useAuth } from '../../context/AuthContext';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';

interface ChatWindowProps {
  conversation: Conversation | null;
  messages: Message[];
  isLoading?: boolean;
  onBack?: () => void;
  onSendMessage: (content: string, replyToId?: number) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

// Date divider component
const DateDivider: React.FC<{ date: Date }> = ({ date }) => {
  let label: string;

  if (isToday(date)) {
    label = 'Today';
  } else if (isYesterday(date)) {
    label = 'Yesterday';
  } else {
    label = format(date, 'MMMM d, yyyy');
  }

  return (
    <div className="flex items-center justify-center my-4">
      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
      <span className="px-4 py-1 text-xs font-medium text-gray-500 bg-white/60 backdrop-blur-sm rounded-full border border-white/50 shadow-sm">
        {label}
      </span>
      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent" />
    </div>
  );
};

// Typing indicator component
const TypingIndicator: React.FC<{ userName: string }> = ({ userName }) => (
  <div className="flex items-center gap-2 px-4 py-2 ml-10">
    <div className="flex items-center gap-2 px-3 py-2 bg-white/60 backdrop-blur-sm rounded-2xl rounded-bl-md border border-white/50 shadow-sm">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-xs text-gray-500">{userName} is typing...</span>
    </div>
  </div>
);

// Empty state when no conversation selected
const EmptyState: React.FC = () => (
  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
    <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-primary-100 to-blue-100 flex items-center justify-center mb-6 shadow-lg">
      <MessageCircle size={48} className="text-primary-500" />
    </div>
    <h3 className="text-xl font-bold text-gray-900 mb-2">Select a conversation</h3>
    <p className="text-sm text-gray-500 max-w-[280px]">
      Choose a conversation from the list to start messaging
    </p>
  </div>
);

// Chat header component
const ChatHeader: React.FC<{
  conversation: Conversation;
  isOnline: boolean;
  isTyping: boolean;
  onBack?: () => void;
}> = ({ conversation, isOnline, isTyping, onBack }) => {
  const participant = conversation.other_participant;
  const [isHovered, setIsHovered] = useState(false);

  const initials = participant
    ? `${participant.first_name[0]}${participant.last_name?.[0] || ''}`
    : '?';

  const displayName = participant
    ? `${participant.first_name} ${participant.last_name || ''}`
    : 'Unknown User';

  return (
    <div
      className="
        px-4 py-3 border-b border-white/30
        bg-white/40 backdrop-blur-md
        flex items-center justify-between
      "
    >
      <div className="flex items-center gap-3">
        {/* Back button (mobile) */}
        {onBack && (
          <button
            onClick={onBack}
            className="
              lg:hidden p-2 -ml-2 rounded-xl
              text-gray-500 hover:text-primary-600
              hover:bg-white/50 transition-all
            "
          >
            <ArrowLeft size={20} />
          </button>
        )}

        {/* Avatar */}
        <div
          className="relative"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div
            className={`
              h-10 w-10 rounded-xl overflow-hidden
              bg-gradient-to-br from-primary-500 to-blue-500
              flex items-center justify-center
              shadow-md transition-all duration-300
              ${isHovered ? 'scale-105 shadow-lg' : ''}
            `}
          >
            {participant?.profile_photo_url ? (
              <img
                src={participant.profile_photo_url}
                alt={displayName}
                className="h-full w-full object-cover"
              />
            ) : (
              <span className="text-white font-bold text-sm">{initials}</span>
            )}
          </div>
          <span
            className={`
              absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full
              border-2 border-white transition-colors duration-300
              ${isOnline ? 'bg-green-500' : 'bg-gray-300'}
            `}
          />
        </div>

        {/* User info */}
        <div>
          <h3 className="font-semibold text-gray-900 text-sm">{displayName}</h3>
          <p className="text-xs text-gray-500">
            {isTyping ? (
              <span className="text-primary-600 animate-pulse">typing...</span>
            ) : isOnline ? (
              <span className="text-green-600">Online</span>
            ) : (
              'Offline'
            )}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1">
        <button
          className="
            p-2.5 rounded-xl text-gray-500
            hover:text-primary-600 hover:bg-white/50
            transition-all duration-200
          "
          title="Voice call"
        >
          <Phone size={18} />
        </button>
        <button
          className="
            p-2.5 rounded-xl text-gray-500
            hover:text-primary-600 hover:bg-white/50
            transition-all duration-200
          "
          title="Video call"
        >
          <Video size={18} />
        </button>
        <button
          className="
            p-2.5 rounded-xl text-gray-500
            hover:text-primary-600 hover:bg-white/50
            transition-all duration-200
          "
          title="More options"
        >
          <MoreVertical size={18} />
        </button>
      </div>
    </div>
  );
};

export const ChatWindow: React.FC<ChatWindowProps> = ({
  conversation,
  messages,
  isLoading = false,
  onBack,
  onSendMessage,
  onLoadMore,
  hasMore = false,
}) => {
  const { user } = useAuth();
  const { isUserOnline, isUserTyping, joinConversation, leaveConversation, markAsRead } = useWebSocket();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [replyTo, setReplyTo] = useState<Message | null>(null);

  // Join/leave conversation for real-time updates
  useEffect(() => {
    if (conversation) {
      joinConversation(conversation.id);
      return () => leaveConversation(conversation.id);
    }
  }, [conversation?.id, joinConversation, leaveConversation]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Mark messages as read when viewing
  useEffect(() => {
    if (conversation && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.sender?.id !== user?.id) {
        markAsRead(conversation.id, lastMessage.id);
      }
    }
  }, [conversation, messages, user, markAsRead]);

  const handleSend = useCallback((content: string) => {
    onSendMessage(content, replyTo?.id);
    setReplyTo(null);
  }, [onSendMessage, replyTo]);

  const handleReply = useCallback((message: Message) => {
    setReplyTo(message);
  }, []);

  if (!conversation) {
    return <EmptyState />;
  }

  const participant = conversation.other_participant;
  const isOnline = participant ? isUserOnline(participant.id) : false;
  const isTyping = participant ? isUserTyping(conversation.id, participant.id) : false;

  // Group messages by date
  const groupedMessages: { date: Date; messages: Message[] }[] = [];
  messages.forEach((message) => {
    const messageDate = new Date(message.created_at);
    const lastGroup = groupedMessages[groupedMessages.length - 1];

    if (lastGroup && isSameDay(lastGroup.date, messageDate)) {
      lastGroup.messages.push(message);
    } else {
      groupedMessages.push({ date: messageDate, messages: [message] });
    }
  });

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-white/20 to-white/40">
      {/* Header */}
      <ChatHeader
        conversation={conversation}
        isOnline={isOnline}
        isTyping={isTyping}
        onBack={onBack}
      />

      {/* Messages area */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-4 py-2"
      >
        {/* Load more button */}
        {hasMore && (
          <div className="flex justify-center py-4">
            <button
              onClick={onLoadMore}
              className="
                px-4 py-2 text-sm font-medium
                text-primary-600 hover:text-primary-700
                bg-white/60 hover:bg-white/80
                backdrop-blur-sm rounded-xl
                border border-white/50
                shadow-sm hover:shadow-md
                transition-all duration-200
              "
            >
              Load earlier messages
            </button>
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="flex justify-center py-8">
            <Loader2 size={24} className="text-primary-500 animate-spin" />
          </div>
        )}

        {/* Messages grouped by date */}
        {groupedMessages.map((group, groupIndex) => (
          <div key={group.date.toISOString()}>
            <DateDivider date={group.date} />
            {group.messages.map((message, messageIndex) => {
              const isOwnMessage = message.sender?.id === user?.id;
              const prevMessage = messageIndex > 0 ? group.messages[messageIndex - 1] : null;
              const showAvatar = !prevMessage || prevMessage.sender?.id !== message.sender?.id;

              return (
                <MessageBubble
                  key={message.id}
                  message={message}
                  isOwnMessage={isOwnMessage}
                  showAvatar={showAvatar}
                  onReply={handleReply}
                />
              );
            })}
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && participant && (
          <TypingIndicator userName={participant.first_name} />
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input */}
      <MessageInput
        conversationId={conversation.id}
        otherUserId={participant?.id || 0}
        onSend={handleSend}
        replyTo={replyTo}
        onCancelReply={() => setReplyTo(null)}
      />
    </div>
  );
};

export default ChatWindow;
