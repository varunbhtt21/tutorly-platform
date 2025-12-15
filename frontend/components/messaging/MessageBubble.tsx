/**
 * MessageBubble Component
 * Displays individual messages with status indicators,
 * animations, and glassmorphism design
 */

import React, { useState } from 'react';
import { format } from 'date-fns';
import { Check, CheckCheck, Clock, Reply, MoreHorizontal } from 'lucide-react';
import type { Message, MessageStatus } from '../../types/api';

interface MessageBubbleProps {
  message: Message;
  isOwnMessage: boolean;
  showAvatar?: boolean;
  onReply?: (message: Message) => void;
}

const StatusIcon: React.FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case 'read':
      return <CheckCheck size={14} className="text-blue-500" />;
    case 'delivered':
      return <CheckCheck size={14} className="text-gray-400" />;
    case 'sent':
      return <Check size={14} className="text-gray-400" />;
    default:
      return <Clock size={14} className="text-gray-300 animate-pulse" />;
  }
};

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isOwnMessage,
  showAvatar = true,
  onReply,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const sender = message.sender;
  const initials = sender
    ? `${sender.first_name[0]}${sender.last_name?.[0] || ''}`
    : '?';

  const formattedTime = format(new Date(message.created_at), 'h:mm a');

  return (
    <div
      className={`
        group flex items-end gap-2 max-w-[80%] mb-2
        ${isOwnMessage ? 'ml-auto flex-row-reverse' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowActions(false);
      }}
    >
      {/* Avatar */}
      {showAvatar && !isOwnMessage && (
        <div
          className={`
            flex-shrink-0 h-8 w-8 rounded-lg overflow-hidden
            bg-gradient-to-br from-primary-500 to-blue-500
            flex items-center justify-center
            shadow-sm transition-all duration-300
            ${isHovered ? 'scale-105' : ''}
          `}
        >
          {sender?.profile_photo_url ? (
            <img
              src={sender.profile_photo_url}
              alt={sender.first_name}
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="text-white font-semibold text-xs">{initials}</span>
          )}
        </div>
      )}

      {/* Message content */}
      <div className="relative flex flex-col">
        {/* Message bubble */}
        <div
          className={`
            relative px-4 py-2.5 rounded-2xl
            transition-all duration-300
            ${isOwnMessage
              ? 'bg-gradient-to-br from-primary-500 to-blue-500 text-white rounded-br-md shadow-lg shadow-primary-500/20'
              : 'bg-white/80 backdrop-blur-sm text-gray-900 rounded-bl-md shadow-md border border-white/50'
            }
            ${isHovered ? 'shadow-lg' : ''}
          `}
        >
          {/* Reply reference */}
          {message.reply_to_id && (
            <div
              className={`
                mb-2 pb-2 border-b text-xs flex items-center gap-1
                ${isOwnMessage
                  ? 'border-white/30 text-white/80'
                  : 'border-gray-200 text-gray-500'
                }
              `}
            >
              <Reply size={12} />
              <span>Replying to a message</span>
            </div>
          )}

          {/* Message text */}
          <p className={`text-sm leading-relaxed whitespace-pre-wrap break-words`}>
            {message.content}
          </p>

          {/* Timestamp and status */}
          <div
            className={`
              flex items-center gap-1.5 mt-1
              ${isOwnMessage ? 'justify-end' : 'justify-start'}
            `}
          >
            <span
              className={`
                text-[10px]
                ${isOwnMessage ? 'text-white/70' : 'text-gray-400'}
              `}
            >
              {formattedTime}
            </span>
            {isOwnMessage && <StatusIcon status={message.status} />}
          </div>

          {/* Decorative tail */}
          <div
            className={`
              absolute bottom-0 w-3 h-3
              ${isOwnMessage
                ? 'right-0 translate-x-0.5 bg-gradient-to-br from-blue-500 to-blue-500'
                : 'left-0 -translate-x-0.5 bg-white/80'
              }
            `}
            style={{
              clipPath: isOwnMessage
                ? 'polygon(0 0, 100% 0, 100% 100%)'
                : 'polygon(0 0, 100% 0, 0 100%)',
            }}
          />
        </div>

        {/* Actions menu */}
        {isHovered && (
          <div
            className={`
              absolute top-1/2 -translate-y-1/2 flex items-center gap-1
              transition-all duration-200 animate-fadeIn
              ${isOwnMessage ? 'right-full mr-2' : 'left-full ml-2'}
            `}
          >
            {onReply && (
              <button
                onClick={() => onReply(message)}
                className="
                  p-1.5 rounded-lg bg-white/80 backdrop-blur-sm
                  text-gray-500 hover:text-primary-600 hover:bg-white
                  shadow-sm hover:shadow-md transition-all duration-200
                  border border-white/50
                "
                title="Reply"
              >
                <Reply size={14} />
              </button>
            )}
            <button
              onClick={() => setShowActions(!showActions)}
              className="
                p-1.5 rounded-lg bg-white/80 backdrop-blur-sm
                text-gray-500 hover:text-primary-600 hover:bg-white
                shadow-sm hover:shadow-md transition-all duration-200
                border border-white/50
              "
              title="More options"
            >
              <MoreHorizontal size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Spacer for own messages avatar area */}
      {showAvatar && isOwnMessage && <div className="w-8" />}

      {/* CSS for fade animation */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-50%) scale(0.9); }
          to { opacity: 1; transform: translateY(-50%) scale(1); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default MessageBubble;
