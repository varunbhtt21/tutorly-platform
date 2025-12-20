/**
 * Classroom Page
 *
 * Video classroom for tutoring sessions with 100ms video and Tutorly chat.
 *
 * Architecture:
 * - Uses 100ms React SDK for video (no iframe)
 * - Integrates Tutorly's existing chat system on right sidebar
 * - Auto-joins with user name from AuthContext (no name prompt)
 * - Supports both Daily.co (iframe) and 100ms (SDK) providers
 *
 * Flow:
 * 1. User navigates to /classroom/:sessionId
 * 2. Page calls joinClassroom API to get room credentials
 * 3. If provider is "hundredms", uses 100ms SDK with native components
 * 4. If provider is "daily", falls back to iframe approach
 * 5. Chat sidebar shows Tutorly messaging with the other participant
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import { HMSProvider, useHMS } from '../context/HMSContext';
import { useConversation } from '../hooks/useConversation';
import { classroomAPI, messagingAPI } from '../services';
import { VideoGrid, VideoControls } from '../components/video';
import { ChatWindow } from '../components/messaging/ChatWindow';
import { Button, Card } from '../components/UIComponents';
import {
  Video,
  MessageCircle,
  Loader2,
  AlertCircle,
  ArrowLeft,
  Maximize2,
  Minimize2,
  Clock,
  X,
} from 'lucide-react';
import type { JoinClassroomResponse } from '../services/classroomAPI';
import type { Conversation, Message } from '../types/api';

// ============================================================================
// Types
// ============================================================================

interface ClassroomState {
  status: 'loading' | 'joining' | 'active' | 'ended' | 'error';
  error?: string;
  roomData?: JoinClassroomResponse;
}

// ============================================================================
// Session Timer Component
// ============================================================================

interface SessionTimerProps {
  startTime: Date;
}

const SessionTimer: React.FC<SessionTimerProps> = ({ startTime }) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const diff = Math.floor((now.getTime() - startTime.getTime()) / 1000);
      setElapsed(Math.max(0, diff));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const hours = Math.floor(elapsed / 3600);
  const minutes = Math.floor((elapsed % 3600) / 60);
  const seconds = elapsed % 60;

  const formatTime = (val: number) => val.toString().padStart(2, '0');

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800/80 rounded-lg">
      <Clock size={14} className="text-gray-400" />
      <span className="font-mono text-sm text-white tabular-nums">
        {hours > 0 && `${formatTime(hours)}:`}
        {formatTime(minutes)}:{formatTime(seconds)}
      </span>
    </div>
  );
};

// ============================================================================
// 100ms Video Classroom Component
// ============================================================================

interface HMSClassroomContentProps {
  roomData: JoinClassroomResponse;
  sessionId: number;
  isInstructor: boolean;
  sessionStartTime: Date;
  onEndSession: () => void;
  onLeave: () => void;
  isEnding: boolean;
  conversation: Conversation | null;
  messages: Message[];
  isLoadingMessages: boolean;
  onSendMessage: (content: string, replyToId?: number) => void;
  isChatConnected: boolean;
  isParticipantOnline: boolean;
}

const HMSClassroomContent: React.FC<HMSClassroomContentProps> = ({
  roomData,
  sessionId,
  isInstructor,
  sessionStartTime,
  onEndSession,
  onLeave,
  isEnding,
  conversation,
  messages,
  isLoadingMessages,
  onSendMessage,
  isChatConnected,
  isParticipantOnline,
}) => {
  const { joinRoom, leaveRoom, isConnected, isConnecting, error } = useHMS();
  const [showChat, setShowChat] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const hasJoined = useRef(false);

  // Auto-join room on mount using auth token from backend
  useEffect(() => {
    if (!hasJoined.current && roomData.token && roomData.participant_name) {
      hasJoined.current = true;
      joinRoom(roomData.token, roomData.participant_name).catch((err) => {
        console.error('Failed to join room:', err);
        toast.error('Failed to join video room. Please try again.');
      });
    }
  }, [roomData.token, roomData.participant_name, joinRoom]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isConnected) {
        leaveRoom();
      }
    };
  }, [isConnected, leaveRoom]);

  // Handle fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;

    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().then(() => {
        setIsFullscreen(true);
      }).catch((err) => {
        console.error('Fullscreen error:', err);
      });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      });
    }
  }, []);

  // Handle fullscreen change events
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Handle session end/leave
  const handleEndOrLeave = useCallback(async () => {
    if (isInstructor) {
      if (window.confirm('Are you sure you want to end this session? This action cannot be undone.')) {
        await leaveRoom();
        onEndSession();
      }
    } else {
      if (window.confirm('Are you sure you want to leave the classroom?')) {
        await leaveRoom();
        onLeave();
      }
    }
  }, [isInstructor, leaveRoom, onEndSession, onLeave]);

  // Show connection error
  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900 p-4">
        <Card className="max-w-md w-full p-8 text-center bg-gray-800 border-gray-700">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-500/20 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Connection Error</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <Button
            variant="primary"
            onClick={() => {
              hasJoined.current = false;
              joinRoom(roomData.token, roomData.participant_name);
            }}
          >
            Try Again
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="fixed inset-0 bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-800/80 backdrop-blur-sm border-b border-gray-700/50 z-10">
        <div className="flex items-center gap-4">
          <Link
            to={isInstructor ? '/instructor/home' : '/dashboard'}
            className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-400" />
          </Link>
          <div>
            <h1 className="text-lg font-semibold text-white">Tutoring Session</h1>
            <p className="text-sm text-gray-400">
              Room: {roomData.room_name}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <SessionTimer startTime={sessionStartTime} />

          {/* Live indicator */}
          {isConnected && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-red-600/20 rounded-lg">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-red-400">LIVE</span>
            </div>
          )}

          {/* Connecting indicator */}
          {isConnecting && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-600/20 rounded-lg">
              <Loader2 size={14} className="text-yellow-400 animate-spin" />
              <span className="text-sm font-medium text-yellow-400">Connecting...</span>
            </div>
          )}

          {/* Chat toggle button */}
          <button
            onClick={() => setShowChat(!showChat)}
            className={`p-2 rounded-lg transition-colors ${
              showChat ? 'bg-primary-600 text-white' : 'hover:bg-gray-700/50 text-gray-400'
            }`}
            title={showChat ? 'Hide chat' : 'Show chat'}
          >
            <MessageCircle size={20} />
          </button>

          {/* Fullscreen toggle */}
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? (
              <Minimize2 size={20} className="text-gray-400" />
            ) : (
              <Maximize2 size={20} className="text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Video area */}
        <div className={`flex-1 flex flex-col ${showChat ? 'mr-0' : ''}`}>
          {/* Video grid */}
          <div className="flex-1 p-4">
            <VideoGrid roomName={roomData.room_name} />
          </div>

          {/* Video controls */}
          <div className="px-4 pb-4">
            <VideoControls
              isInstructor={isInstructor}
              onEndSession={handleEndOrLeave}
              onLeave={handleEndOrLeave}
              isEnding={isEnding}
            />
          </div>
        </div>

        {/* Chat sidebar */}
        {showChat && (
          <div className="w-80 lg:w-96 border-l border-gray-700/50 flex flex-col bg-gray-800/50">
            {/* Chat header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700/50">
              <div className="flex items-center gap-2">
                <MessageCircle size={18} className="text-primary-400" />
                <h2 className="font-semibold text-white">Session Chat</h2>
                {/* Online status indicator */}
                {isChatConnected && (
                  <div className="flex items-center gap-1.5 ml-2">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isParticipantOnline ? 'bg-green-500' : 'bg-gray-500'
                      }`}
                    />
                    <span className="text-xs text-gray-400">
                      {isParticipantOnline ? 'Online' : 'Offline'}
                    </span>
                  </div>
                )}
              </div>
              <button
                onClick={() => setShowChat(false)}
                className="p-1.5 rounded-lg hover:bg-gray-700/50 transition-colors lg:hidden"
              >
                <X size={18} className="text-gray-400" />
              </button>
            </div>

            {/* Chat window */}
            <div className="flex-1 overflow-hidden">
              {conversation ? (
                <ChatWindow
                  conversation={conversation}
                  messages={messages}
                  isLoading={isLoadingMessages}
                  onSendMessage={onSendMessage}
                />
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                  <MessageCircle size={48} className="text-gray-600 mb-4" />
                  <p className="text-gray-400 text-sm">
                    Chat will be available once connected
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Daily.co Iframe Fallback Component
// ============================================================================

interface DailyClassroomContentProps {
  roomData: JoinClassroomResponse;
  isInstructor: boolean;
  sessionStartTime: Date;
  onEndSession: () => void;
  onLeave: () => void;
  isEnding: boolean;
}

const DailyClassroomContent: React.FC<DailyClassroomContentProps> = ({
  roomData,
  isInstructor,
  sessionStartTime,
  onEndSession,
  onLeave,
  isEnding,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const handleLoad = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handleError = useCallback(() => {
    setIsLoading(false);
    toast.error('Failed to load video. Please try refreshing.');
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;

    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().then(() => {
        setIsFullscreen(true);
      }).catch((err) => {
        console.error('Fullscreen error:', err);
      });
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false);
      });
    }
  }, []);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  return (
    <div ref={containerRef} className="fixed inset-0 bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-800/80 backdrop-blur-sm border-b border-gray-700/50">
        <div className="flex items-center gap-4">
          <Link
            to={isInstructor ? '/instructor/home' : '/dashboard'}
            className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors"
          >
            <ArrowLeft size={20} className="text-gray-400" />
          </Link>
          <div>
            <h1 className="text-lg font-semibold text-white">Tutoring Session</h1>
            <p className="text-sm text-gray-400">Room: {roomData.room_name}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <SessionTimer startTime={sessionStartTime} />

          <div className="flex items-center gap-2 px-3 py-1.5 bg-red-600/20 rounded-lg">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-red-400">LIVE</span>
          </div>

          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-lg hover:bg-gray-700/50 transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? (
              <Minimize2 size={20} className="text-gray-400" />
            ) : (
              <Maximize2 size={20} className="text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Video container */}
      <div className="flex-1 relative p-4">
        <div className="relative w-full h-full bg-gray-900 rounded-2xl overflow-hidden">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
              <div className="text-center">
                <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Connecting to classroom...</p>
              </div>
            </div>
          )}

          <iframe
            ref={iframeRef}
            src={roomData.room_url}
            title="Video Classroom"
            allow="camera; microphone; fullscreen; display-capture; autoplay"
            className="w-full h-full border-0"
            onLoad={handleLoad}
            onError={handleError}
          />
        </div>

        {/* Control bar overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
          <div className="flex items-center justify-end max-w-4xl mx-auto">
            {isInstructor ? (
              <Button
                variant="primary"
                size="md"
                onClick={() => {
                  if (window.confirm('Are you sure you want to end this session?')) {
                    onEndSession();
                  }
                }}
                disabled={isEnding}
                className="!bg-red-600 hover:!bg-red-500 !shadow-red-500/25"
              >
                {isEnding ? (
                  <>
                    <Loader2 size={16} className="animate-spin mr-2" />
                    Ending...
                  </>
                ) : (
                  'End Session'
                )}
              </Button>
            ) : (
              <Button
                variant="secondary"
                size="md"
                onClick={() => {
                  if (window.confirm('Are you sure you want to leave?')) {
                    onLeave();
                  }
                }}
                className="!bg-gray-800 !text-white !border-gray-700 hover:!bg-gray-700"
              >
                <ArrowLeft size={16} className="mr-2" />
                Leave
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Error State Component
// ============================================================================

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  onBack: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry, onBack }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
    <Card className="max-w-md w-full p-8 text-center">
      <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
        <AlertCircle className="w-8 h-8 text-red-600" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Join Classroom</h2>
      <p className="text-gray-600 mb-6">{message}</p>
      <div className="flex gap-3 justify-center">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft size={16} className="mr-2" />
          Go Back
        </Button>
        {onRetry && (
          <Button variant="primary" onClick={onRetry}>
            Try Again
          </Button>
        )}
      </div>
    </Card>
  </div>
);

// ============================================================================
// Session Ended State Component
// ============================================================================

interface SessionEndedStateProps {
  onBack: () => void;
}

const SessionEndedState: React.FC<SessionEndedStateProps> = ({ onBack }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
    <Card className="max-w-md w-full p-8 text-center">
      <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-green-100 flex items-center justify-center">
        <Video className="w-8 h-8 text-green-600" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Session Ended</h2>
      <p className="text-gray-600 mb-6">
        Thank you for your session! We hope it was productive.
      </p>
      <Button variant="primary" onClick={onBack} className="w-full">
        <ArrowLeft size={16} className="mr-2" />
        Return to Dashboard
      </Button>
    </Card>
  </div>
);

// ============================================================================
// Loading State Component
// ============================================================================

const LoadingState: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-900">
    <div className="text-center">
      <Loader2 className="w-16 h-16 text-primary-500 animate-spin mx-auto mb-6" />
      <h2 className="text-xl font-semibold text-white mb-2">Joining Classroom</h2>
      <p className="text-gray-400">Setting up your video session...</p>
    </div>
  </div>
);

// ============================================================================
// Main Classroom Component
// ============================================================================

const Classroom: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [classroomState, setClassroomState] = useState<ClassroomState>({
    status: 'loading',
  });
  const [sessionStartTime] = useState(() => new Date());
  const [conversationId, setConversationId] = useState<number | null>(null);

  // Use the reusable conversation hook for real-time messaging
  const {
    messages,
    isLoadingMessages,
    conversation,
    setConversation,
    sendMessage,
    isConnected: isChatConnected,
    isParticipantOnline,
  } = useConversation(conversationId, {
    onNewMessage: (message) => {
      // Play notification sound or show indicator for new messages
      // This callback is optional but useful for notifications
    },
  });

  // Validate session ID
  const numericSessionId = sessionId ? parseInt(sessionId, 10) : null;

  // Join classroom mutation
  const joinMutation = useMutation({
    mutationFn: () => {
      if (!numericSessionId) {
        throw new Error('Invalid session ID');
      }
      return classroomAPI.joinClassroom(numericSessionId);
    },
    onSuccess: async (data) => {
      setClassroomState({
        status: 'active',
        roomData: data,
      });

      // Load conversation for the session chat
      try {
        // Get conversations and find one related to this session
        const conversations = await messagingAPI.getConversations();

        if (conversations.length > 0) {
          // Use the most recent conversation
          // TODO: Backend should link sessions to conversations directly
          const recentConversation = conversations[0];
          setConversation(recentConversation);
          setConversationId(recentConversation.id);
        }
      } catch (error) {
        console.error('Failed to load conversation:', error);
      }
    },
    onError: (error: Error) => {
      setClassroomState({
        status: 'error',
        error: error.message || 'Failed to join classroom',
      });
    },
  });

  // End classroom mutation (instructor only)
  const endMutation = useMutation({
    mutationFn: () => {
      if (!numericSessionId) {
        throw new Error('Invalid session ID');
      }
      return classroomAPI.endClassroom(numericSessionId);
    },
    onSuccess: () => {
      toast.success('Session ended successfully');
      setClassroomState({ status: 'ended' });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to end session');
    },
  });

  // Join classroom on mount
  useEffect(() => {
    if (numericSessionId && classroomState.status === 'loading') {
      setClassroomState({ status: 'joining' });
      joinMutation.mutate();
    }
  }, [numericSessionId]);

  // Handle navigation
  const handleBack = useCallback(() => {
    const isInstructor = user?.role === 'instructor';
    navigate(isInstructor ? '/instructor/home' : '/dashboard');
  }, [navigate, user]);

  const handleRetry = useCallback(() => {
    setClassroomState({ status: 'loading' });
    joinMutation.mutate();
  }, [joinMutation]);

  const handleEndSession = useCallback(() => {
    endMutation.mutate();
  }, [endMutation]);

  const handleLeave = useCallback(() => {
    handleBack();
  }, [handleBack]);

  // Handle sending messages - delegates to the useConversation hook
  // The hook handles optimistic updates, WebSocket, and REST fallback
  const handleSendMessage = useCallback((content: string, replyToId?: number) => {
    sendMessage(content, replyToId);
  }, [sendMessage]);

  // Invalid session ID
  if (!numericSessionId) {
    return (
      <ErrorState
        message="Invalid session ID provided."
        onBack={handleBack}
      />
    );
  }

  // Render based on state
  if (classroomState.status === 'loading' || classroomState.status === 'joining') {
    return <LoadingState />;
  }

  if (classroomState.status === 'error') {
    return (
      <ErrorState
        message={classroomState.error || 'An unexpected error occurred.'}
        onRetry={handleRetry}
        onBack={handleBack}
      />
    );
  }

  if (classroomState.status === 'ended') {
    return <SessionEndedState onBack={handleBack} />;
  }

  // Active classroom
  const { roomData } = classroomState;
  if (!roomData) {
    return (
      <ErrorState
        message="Failed to load classroom data."
        onRetry={handleRetry}
        onBack={handleBack}
      />
    );
  }

  const isInstructor = roomData.participant_role === 'instructor';

  // Use 100ms for hundredms provider, iframe for daily
  if (roomData.provider === 'hundredms') {
    return (
      <HMSProvider>
        <HMSClassroomContent
          roomData={roomData}
          sessionId={numericSessionId}
          isInstructor={isInstructor}
          sessionStartTime={sessionStartTime}
          onEndSession={handleEndSession}
          onLeave={handleLeave}
          isEnding={endMutation.isPending}
          conversation={conversation}
          messages={messages}
          isLoadingMessages={isLoadingMessages}
          onSendMessage={handleSendMessage}
          isChatConnected={isChatConnected}
          isParticipantOnline={isParticipantOnline}
        />
      </HMSProvider>
    );
  }

  // Fallback to Daily.co iframe approach
  return (
    <DailyClassroomContent
      roomData={roomData}
      isInstructor={isInstructor}
      sessionStartTime={sessionStartTime}
      onEndSession={handleEndSession}
      onLeave={handleLeave}
      isEnding={endMutation.isPending}
    />
  );
};

export default Classroom;
