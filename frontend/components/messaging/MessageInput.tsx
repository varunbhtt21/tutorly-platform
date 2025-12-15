/**
 * MessageInput Component
 * Input area with feature gating for images/files,
 * typing indicators, and reply support
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Send,
  Paperclip,
  Image as ImageIcon,
  Smile,
  X,
  Lock,
  Reply,
  Loader2,
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { messagingAPI } from '../../services';
import { useWebSocket } from '../../context/WebSocketContext';
import type { Message, FeatureAccess } from '../../types/api';

interface MessageInputProps {
  conversationId: number;
  otherUserId: number;
  onSend: (content: string) => void;
  replyTo?: Message | null;
  onCancelReply?: () => void;
  disabled?: boolean;
}

// Tooltip component for locked features
const LockedFeatureTooltip: React.FC<{ children: React.ReactNode; message: string }> = ({
  children,
  message,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {isVisible && (
        <div
          className="
            absolute bottom-full left-1/2 -translate-x-1/2 mb-2
            px-3 py-2 max-w-[200px] text-center
            bg-gray-900/95 backdrop-blur-sm text-white text-xs
            rounded-xl shadow-lg z-50
            animate-fadeIn
          "
        >
          <div className="flex items-center gap-1.5 justify-center mb-1">
            <Lock size={12} />
            <span className="font-semibold">Feature Locked</span>
          </div>
          <p className="text-gray-300">{message}</p>
          {/* Arrow */}
          <div
            className="
              absolute top-full left-1/2 -translate-x-1/2
              w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px]
              border-l-transparent border-r-transparent border-t-gray-900/95
            "
          />
        </div>
      )}
    </div>
  );
};

export const MessageInput: React.FC<MessageInputProps> = ({
  conversationId,
  otherUserId,
  onSend,
  replyTo,
  onCancelReply,
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { startTyping, stopTyping } = useWebSocket();
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch feature access
  const { data: featureAccess, isLoading: isLoadingAccess } = useQuery({
    queryKey: ['featureAccess', otherUserId],
    queryFn: () => messagingAPI.getFeatureAccess(otherUserId),
    enabled: otherUserId > 0,
    staleTime: 30000, // Cache for 30 seconds
  });

  const canSendText = featureAccess?.can_send_text ?? true;
  const canSendImage = featureAccess?.can_send_image ?? false;
  const canSendFile = featureAccess?.can_send_file ?? false;
  const hasBooking = featureAccess?.has_booking ?? false;

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [conversationId]);

  // Handle typing indicator
  const handleTyping = useCallback(() => {
    startTyping(conversationId);

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing
    typingTimeoutRef.current = setTimeout(() => {
      stopTyping(conversationId);
    }, 2000);
  }, [conversationId, startTyping, stopTyping]);

  // Cleanup typing timeout on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      stopTyping(conversationId);
    };
  }, [conversationId, stopTyping]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    handleTyping();
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();

    const trimmedMessage = message.trim();
    if (!trimmedMessage || isSending || disabled) return;

    setIsSending(true);
    stopTyping(conversationId);

    try {
      onSend(trimmedMessage);
      setMessage('');
      inputRef.current?.focus();
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const lockedMessage = 'Book a session to unlock this feature';

  return (
    <div className="border-t border-white/30 bg-white/40 backdrop-blur-md p-3">
      {/* Reply preview */}
      {replyTo && (
        <div
          className="
            mb-3 px-3 py-2 flex items-center gap-2
            bg-white/60 rounded-xl border border-white/50
          "
        >
          <Reply size={16} className="text-primary-500 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-gray-500">
              Replying to {replyTo.sender?.first_name}
            </p>
            <p className="text-sm text-gray-700 truncate">{replyTo.content}</p>
          </div>
          <button
            onClick={onCancelReply}
            className="
              p-1 rounded-lg text-gray-400 hover:text-gray-600
              hover:bg-white/50 transition-colors
            "
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* Input area */}
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        {/* Attachment buttons */}
        <div className="flex items-center gap-1 pb-2">
          {/* Image button */}
          <LockedFeatureTooltip message={lockedMessage}>
            <button
              type="button"
              disabled={!canSendImage}
              className={`
                p-2 rounded-xl transition-all duration-200
                ${canSendImage
                  ? 'text-gray-500 hover:text-primary-600 hover:bg-white/50'
                  : 'text-gray-300 cursor-not-allowed'
                }
              `}
              title={canSendImage ? 'Send image' : lockedMessage}
            >
              <ImageIcon size={20} />
            </button>
          </LockedFeatureTooltip>

          {/* File button */}
          <LockedFeatureTooltip message={lockedMessage}>
            <button
              type="button"
              disabled={!canSendFile}
              className={`
                p-2 rounded-xl transition-all duration-200
                ${canSendFile
                  ? 'text-gray-500 hover:text-primary-600 hover:bg-white/50'
                  : 'text-gray-300 cursor-not-allowed'
                }
              `}
              title={canSendFile ? 'Attach file' : lockedMessage}
            >
              <Paperclip size={20} />
            </button>
          </LockedFeatureTooltip>

          {/* Emoji button (always available) */}
          <button
            type="button"
            className="
              p-2 rounded-xl text-gray-500
              hover:text-primary-600 hover:bg-white/50
              transition-all duration-200
            "
            title="Add emoji"
          >
            <Smile size={20} />
          </button>
        </div>

        {/* Text input */}
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={disabled || !canSendText}
            rows={1}
            className="
              w-full px-4 py-3 pr-12
              bg-white/70 backdrop-blur-sm
              border border-white/50 rounded-2xl
              text-gray-900 placeholder-gray-400
              focus:bg-white/90 focus:border-primary-300
              focus:ring-2 focus:ring-primary-200/50
              transition-all duration-200
              resize-none overflow-hidden
              disabled:opacity-50 disabled:cursor-not-allowed
            "
            style={{ minHeight: '48px', maxHeight: '150px' }}
          />

          {/* Send button */}
          <button
            type="submit"
            disabled={!message.trim() || isSending || disabled}
            className={`
              absolute right-2 bottom-2
              p-2 rounded-xl
              transition-all duration-300
              ${message.trim()
                ? 'bg-gradient-to-br from-primary-500 to-blue-500 text-white shadow-lg shadow-primary-500/30 hover:shadow-xl hover:scale-105'
                : 'bg-gray-100 text-gray-400'
              }
              disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
            `}
          >
            {isSending ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
      </form>

      {/* Feature gating notice */}
      {!hasBooking && (
        <div
          className="
            mt-3 px-3 py-2 flex items-center gap-2
            bg-amber-50/80 backdrop-blur-sm
            border border-amber-200/50 rounded-xl
          "
        >
          <Lock size={14} className="text-amber-600 flex-shrink-0" />
          <p className="text-xs text-amber-700">
            <span className="font-medium">Some features are locked.</span>{' '}
            Book a session to send images and files.
          </p>
        </div>
      )}

      {/* Animation styles */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translate(-50%, 4px); }
          to { opacity: 1; transform: translate(-50%, 0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.15s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default MessageInput;
