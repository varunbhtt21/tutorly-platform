/**
 * VideoTile Component
 *
 * Displays a single participant's video feed.
 * Shows avatar when video is disabled.
 * Displays name badge and audio indicator.
 */

import React from 'react';
import {
  useHMSStore,
  selectVideoTrackByPeerID,
  selectAudioTrackByPeerID,
  useVideo,
} from '@100mslive/react-sdk';
import type { HMSPeer } from '@100mslive/react-sdk';
import { Mic, MicOff, User } from 'lucide-react';

interface VideoTileProps {
  peer: HMSPeer;
  isLocal?: boolean;
  className?: string;
}

export const VideoTile: React.FC<VideoTileProps> = ({
  peer,
  isLocal = false,
  className = '',
}) => {
  // Get tracks for this peer
  const videoTrack = useHMSStore(selectVideoTrackByPeerID(peer.id));
  const audioTrack = useHMSStore(selectAudioTrackByPeerID(peer.id));

  // Attach video element
  const { videoRef } = useVideo({
    trackId: videoTrack?.id,
  });

  const isVideoEnabled = videoTrack?.enabled;
  const isAudioEnabled = audioTrack?.enabled;

  // Get initials for avatar
  const initials = peer.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  // Role badge
  const isInstructor = peer.roleName === 'host';

  return (
    <div
      className={`
        relative bg-gray-900 rounded-2xl overflow-hidden
        ${className}
      `}
    >
      {/* Video element */}
      {isVideoEnabled ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted={isLocal}
          className={`
            w-full h-full object-cover
            ${isLocal ? 'transform -scale-x-100' : ''}
          `}
        />
      ) : (
        // Avatar when video is off
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center shadow-xl">
            {initials ? (
              <span className="text-3xl font-bold text-white">{initials}</span>
            ) : (
              <User size={40} className="text-white" />
            )}
          </div>
        </div>
      )}

      {/* Overlay gradient for readability */}
      <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/70 to-transparent pointer-events-none" />

      {/* Name badge */}
      <div className="absolute bottom-3 left-3 flex items-center gap-2">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-black/50 backdrop-blur-sm rounded-lg">
          {/* Audio indicator */}
          <div
            className={`
              p-1 rounded-full
              ${isAudioEnabled ? 'bg-green-500/20' : 'bg-red-500/20'}
            `}
          >
            {isAudioEnabled ? (
              <Mic size={14} className="text-green-400" />
            ) : (
              <MicOff size={14} className="text-red-400" />
            )}
          </div>

          {/* Name */}
          <span className="text-sm font-medium text-white">
            {peer.name}
            {isLocal && ' (You)'}
          </span>

          {/* Role badge */}
          {isInstructor && (
            <span className="px-1.5 py-0.5 text-xs font-semibold bg-primary-500/80 text-white rounded">
              Instructor
            </span>
          )}
        </div>
      </div>

      {/* Local indicator */}
      {isLocal && (
        <div className="absolute top-3 right-3 px-2 py-1 bg-primary-500/80 backdrop-blur-sm rounded-md">
          <span className="text-xs font-medium text-white">You</span>
        </div>
      )}
    </div>
  );
};

export default VideoTile;
