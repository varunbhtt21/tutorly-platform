/**
 * VideoControls Component
 *
 * Control bar for video call actions:
 * - Toggle audio/video
 * - Screen sharing
 * - End call
 *
 * Follows existing ControlBar pattern from Classroom.tsx
 */

import React from 'react';
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  MonitorUp,
  PhoneOff,
  ArrowLeft,
  Loader2,
} from 'lucide-react';
import { useHMS } from '../../context/HMSContext';
import { Button } from '../UIComponents';

interface VideoControlsProps {
  isInstructor: boolean;
  onEndSession: () => void;
  onLeave: () => void;
  isEnding?: boolean;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  isInstructor,
  onEndSession,
  onLeave,
  isEnding = false,
}) => {
  const {
    isAudioEnabled,
    isVideoEnabled,
    isScreenSharing,
    toggleAudio,
    toggleVideo,
    toggleScreenShare,
  } = useHMS();

  return (
    <div className="flex items-center justify-center gap-3 px-4 py-3">
      {/* Audio toggle */}
      <button
        onClick={toggleAudio}
        className={`
          p-4 rounded-2xl transition-all duration-200
          ${
            isAudioEnabled
              ? 'bg-gray-700 hover:bg-gray-600 text-white'
              : 'bg-red-500 hover:bg-red-400 text-white'
          }
        `}
        title={isAudioEnabled ? 'Mute microphone' : 'Unmute microphone'}
      >
        {isAudioEnabled ? <Mic size={22} /> : <MicOff size={22} />}
      </button>

      {/* Video toggle */}
      <button
        onClick={toggleVideo}
        className={`
          p-4 rounded-2xl transition-all duration-200
          ${
            isVideoEnabled
              ? 'bg-gray-700 hover:bg-gray-600 text-white'
              : 'bg-red-500 hover:bg-red-400 text-white'
          }
        `}
        title={isVideoEnabled ? 'Turn off camera' : 'Turn on camera'}
      >
        {isVideoEnabled ? <Video size={22} /> : <VideoOff size={22} />}
      </button>

      {/* Screen share toggle */}
      <button
        onClick={toggleScreenShare}
        className={`
          p-4 rounded-2xl transition-all duration-200
          ${
            isScreenSharing
              ? 'bg-primary-500 hover:bg-primary-400 text-white'
              : 'bg-gray-700 hover:bg-gray-600 text-white'
          }
        `}
        title={isScreenSharing ? 'Stop sharing' : 'Share screen'}
      >
        <MonitorUp size={22} />
      </button>

      {/* Separator */}
      <div className="w-px h-10 bg-gray-600 mx-2" />

      {/* End/Leave button */}
      {isInstructor ? (
        <Button
          variant="primary"
          size="md"
          onClick={onEndSession}
          disabled={isEnding}
          className="!bg-red-600 hover:!bg-red-500 !shadow-red-500/25 !rounded-2xl"
        >
          {isEnding ? (
            <>
              <Loader2 size={18} className="animate-spin mr-2" />
              Ending...
            </>
          ) : (
            <>
              <PhoneOff size={18} className="mr-2" />
              End Session
            </>
          )}
        </Button>
      ) : (
        <Button
          variant="secondary"
          size="md"
          onClick={onLeave}
          className="!bg-gray-700 !text-white !border-gray-600 hover:!bg-gray-600 !rounded-2xl"
        >
          <ArrowLeft size={18} className="mr-2" />
          Leave
        </Button>
      )}
    </div>
  );
};

export default VideoControls;
