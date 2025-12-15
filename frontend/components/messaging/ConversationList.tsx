/**
 * ConversationList Component
 * Displays list of conversations with glassmorphism design,
 * online indicators, and smooth animations
 */

import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { Search, MessageCircle, Circle, Loader2 } from 'lucide-react';
import type { Conversation } from '../../types/api';
import { useWebSocket } from '../../context/WebSocketContext';

interface ConversationListProps {
  conversations: Conversation[];
  selectedId: number | null;
  onSelect: (conversation: Conversation) => void;
  isLoading?: boolean;
}

interface ConversationItemProps {
  conversation: Conversation;
  isSelected: boolean;
  isOnline: boolean;
  onClick: () => void;
}

const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isSelected,
  isOnline,
  onClick,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const participant = conversation.other_participant;

  const initials = participant
    ? `${participant.first_name[0]}${participant.last_name?.[0] || ''}`
    : '?';

  const displayName = participant
    ? `${participant.first_name} ${participant.last_name || ''}`
    : 'Unknown User';

  const lastMessageTime = conversation.last_message_at
    ? formatDistanceToNow(new Date(conversation.last_message_at), { addSuffix: true })
    : 'No messages yet';

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        w-full p-3 rounded-xl flex items-center gap-3
        transition-all duration-300 text-left group
        ${isSelected
          ? 'bg-gradient-to-r from-primary-500/10 to-blue-500/10 border border-primary-200/50'
          : isHovered
          ? 'bg-white/60 shadow-md'
          : 'bg-white/30 hover:bg-white/50'
        }
      `}
    >
      {/* Avatar with online indicator */}
      <div className="relative flex-shrink-0">
        <div
          className={`
            h-12 w-12 rounded-xl overflow-hidden
            bg-gradient-to-br from-primary-500 to-blue-500
            flex items-center justify-center
            shadow-md transition-all duration-300
            ${isHovered ? 'scale-105 shadow-lg shadow-primary-500/20' : ''}
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
        {/* Online indicator */}
        <span
          className={`
            absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full
            border-2 border-white transition-all duration-300
            ${isOnline ? 'bg-green-500' : 'bg-gray-300'}
            ${isOnline && isHovered ? 'scale-110 animate-pulse' : ''}
          `}
        />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-0.5">
          <h4
            className={`
              font-semibold text-sm truncate transition-colors duration-300
              ${isSelected ? 'text-primary-700' : 'text-gray-900'}
            `}
          >
            {displayName}
          </h4>
          {conversation.unread_count > 0 && (
            <span
              className={`
                flex-shrink-0 min-w-[20px] h-5 px-1.5
                bg-gradient-to-r from-primary-500 to-blue-500
                text-white text-xs font-bold rounded-full
                flex items-center justify-center
                shadow-sm shadow-primary-500/30
                transition-all duration-300
                ${isHovered ? 'scale-110' : ''}
              `}
            >
              {conversation.unread_count > 99 ? '99+' : conversation.unread_count}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <p className="text-xs text-gray-500 truncate">{lastMessageTime}</p>
          {participant?.role && (
            <span
              className={`
                text-[10px] px-1.5 py-0.5 rounded-md capitalize
                ${participant.role === 'instructor'
                  ? 'bg-primary-100/80 text-primary-700'
                  : 'bg-sky-100/80 text-sky-700'
                }
              `}
            >
              {participant.role}
            </span>
          )}
        </div>
      </div>

      {/* Hover indicator */}
      <div
        className={`
          w-1 h-8 rounded-full bg-gradient-to-b from-primary-500 to-blue-500
          transition-all duration-300
          ${isSelected ? 'opacity-100' : isHovered ? 'opacity-50' : 'opacity-0'}
        `}
      />
    </button>
  );
};

const EmptyState: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-100 to-blue-100 flex items-center justify-center mb-4">
      <MessageCircle size={32} className="text-primary-500" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">No conversations yet</h3>
    <p className="text-sm text-gray-500 max-w-[200px]">
      Start a conversation with a tutor or student to begin messaging
    </p>
  </div>
);

const LoadingState: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-12">
    <Loader2 size={32} className="text-primary-500 animate-spin mb-4" />
    <p className="text-sm text-gray-500">Loading conversations...</p>
  </div>
);

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  selectedId,
  onSelect,
  isLoading = false,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const { isUserOnline } = useWebSocket();

  const filteredConversations = conversations.filter((conv) => {
    if (!searchQuery.trim()) return true;
    const participant = conv.other_participant;
    if (!participant) return false;
    const fullName = `${participant.first_name} ${participant.last_name || ''}`.toLowerCase();
    return fullName.includes(searchQuery.toLowerCase());
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header with search */}
      <div className="p-4 border-b border-white/30">
        <h2 className="text-lg font-bold text-gray-900 mb-3">Messages</h2>
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="
              w-full pl-9 pr-4 py-2.5 text-sm
              rounded-xl border border-white/40
              bg-white/50 backdrop-blur-sm
              text-gray-900 placeholder-gray-400
              focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50
              focus:bg-white/80 transition-all
            "
          />
        </div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {isLoading ? (
          <LoadingState />
        ) : filteredConversations.length === 0 ? (
          searchQuery ? (
            <div className="text-center py-8 text-gray-500 text-sm">
              No conversations match "{searchQuery}"
            </div>
          ) : (
            <EmptyState />
          )
        ) : (
          filteredConversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isSelected={selectedId === conversation.id}
              isOnline={conversation.other_participant
                ? isUserOnline(conversation.other_participant.id)
                : false
              }
              onClick={() => onSelect(conversation)}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationList;
