/**
 * Classroom Page
 *
 * Video classroom for tutoring sessions.
 * Embeds Daily.co video call via iframe for reliability and simplicity.
 *
 * Flow:
 * 1. User navigates to /classroom/:sessionId
 * 2. Page calls joinClassroom API to get room URL with auth token
 * 3. Daily.co iframe is rendered with the authenticated URL
 * 4. Instructor can end the session via EndClassroom API
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import { classroomAPI } from '../services';
import { Button, Card } from '../components/UIComponents';
import {
  Video,
  VideoOff,
  Mic,
  MicOff,
  PhoneOff,
  Users,
  Clock,
  AlertCircle,
  Loader2,
  ArrowLeft,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import type { JoinClassroomResponse } from '../services/classroomAPI';

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
    <div className="flex items-center gap-2 px-4 py-2 bg-gray-900/50 rounded-xl">
      <Clock size={16} className="text-gray-400" />
      <span className="font-mono text-white tabular-nums">
        {hours > 0 && `${formatTime(hours)}:`}
        {formatTime(minutes)}:{formatTime(seconds)}
      </span>
    </div>
  );
};

// ============================================================================
// Video Container Component
// ============================================================================

interface VideoContainerProps {
  roomUrl: string;
  onLoad?: () => void;
  onError?: () => void;
}

const VideoContainer: React.FC<VideoContainerProps> = ({ roomUrl, onLoad, onError }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleLoad = useCallback(() => {
    setIsLoading(false);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback(() => {
    setIsLoading(false);
    onError?.();
  }, [onError]);

  return (
    <div className="relative w-full h-full bg-gray-900 rounded-2xl overflow-hidden">
      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Connecting to classroom...</p>
          </div>
        </div>
      )}

      {/* Daily.co iframe */}
      <iframe
        ref={iframeRef}
        src={roomUrl}
        title="Video Classroom"
        allow="camera; microphone; fullscreen; display-capture; autoplay"
        className="w-full h-full border-0"
        onLoad={handleLoad}
        onError={handleError}
      />
    </div>
  );
};

// ============================================================================
// Control Bar Component
// ============================================================================

interface ControlBarProps {
  isInstructor: boolean;
  sessionStartTime: Date;
  participantName: string;
  participantRole: string;
  onEndSession: () => void;
  onLeave: () => void;
  isEnding: boolean;
}

const ControlBar: React.FC<ControlBarProps> = ({
  isInstructor,
  sessionStartTime,
  participantName,
  participantRole,
  onEndSession,
  onLeave,
  isEnding,
}) => {
  return (
    <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        {/* Left side - Session info */}
        <div className="flex items-center gap-4">
          <SessionTimer startTime={sessionStartTime} />
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-900/50 rounded-lg">
            <Users size={14} className="text-gray-400" />
            <span className="text-sm text-gray-300">{participantName}</span>
            <span className="text-xs text-gray-500 capitalize">({participantRole})</span>
          </div>
        </div>

        {/* Right side - Actions */}
        <div className="flex items-center gap-3">
          {isInstructor ? (
            <Button
              variant="primary"
              size="md"
              onClick={onEndSession}
              disabled={isEnding}
              className="!bg-red-600 hover:!bg-red-500 !shadow-red-500/25"
            >
              {isEnding ? (
                <>
                  <Loader2 size={16} className="animate-spin mr-2" />
                  Ending...
                </>
              ) : (
                <>
                  <PhoneOff size={16} className="mr-2" />
                  End Session
                </>
              )}
            </Button>
          ) : (
            <Button
              variant="secondary"
              size="md"
              onClick={onLeave}
              className="!bg-gray-800 !text-white !border-gray-700 hover:!bg-gray-700"
            >
              <ArrowLeft size={16} className="mr-2" />
              Leave
            </Button>
          )}
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
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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
    onSuccess: (data) => {
      setClassroomState({
        status: 'active',
        roomData: data,
      });
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
    if (window.confirm('Are you sure you want to end this session? This action cannot be undone.')) {
      endMutation.mutate();
    }
  }, [endMutation]);

  const handleLeave = useCallback(() => {
    if (window.confirm('Are you sure you want to leave the classroom?')) {
      handleBack();
    }
  }, [handleBack]);

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

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 bg-gray-900 flex flex-col"
    >
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
            <p className="text-sm text-gray-400">
              Room: {roomData.room_name}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Live indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-red-600/20 rounded-lg">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-red-400">LIVE</span>
          </div>

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

      {/* Video container */}
      <div className="flex-1 relative p-4">
        <VideoContainer
          roomUrl={roomData.room_url}
          onLoad={() => console.log('Video loaded')}
          onError={() => {
            toast.error('Failed to load video. Please try refreshing.');
          }}
        />

        {/* Control bar overlay */}
        <ControlBar
          isInstructor={isInstructor}
          sessionStartTime={sessionStartTime}
          participantName={roomData.participant_name}
          participantRole={roomData.participant_role}
          onEndSession={handleEndSession}
          onLeave={handleLeave}
          isEnding={endMutation.isPending}
        />
      </div>
    </div>
  );
};

export default Classroom;
