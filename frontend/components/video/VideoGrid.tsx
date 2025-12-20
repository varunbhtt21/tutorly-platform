/**
 * VideoGrid Component
 *
 * Displays video tiles in a responsive grid layout.
 * Optimized for 1-on-1 tutoring sessions (2 participants).
 *
 * Uses HMS context internally to get peer information.
 *
 * Layout:
 * - 1 participant: Full screen with waiting message
 * - 2 participants: Side by side on desktop, stacked on mobile
 */

import React from 'react';
import { useHMS } from '../../context/HMSContext';
import { VideoTile } from './VideoTile';
import { DraggablePiP } from './DraggablePiP';
import { Loader2 } from 'lucide-react';

interface VideoGridProps {
  roomName?: string;  // Optional, for display purposes
}

export const VideoGrid: React.FC<VideoGridProps> = ({ roomName }) => {
  const { localPeer, remotePeers, isConnecting, isConnected } = useHMS();

  const totalParticipants = (localPeer ? 1 : 0) + remotePeers.length;

  // Still connecting
  if (isConnecting) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 rounded-2xl">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Connecting to room...</p>
        </div>
      </div>
    );
  }

  // Not connected yet
  if (!isConnected) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 rounded-2xl">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
            <div className="w-8 h-8 rounded-full bg-gray-700" />
          </div>
          <p className="text-gray-400">Ready to connect...</p>
        </div>
      </div>
    );
  }

  // No participants (shouldn't happen if connected)
  if (totalParticipants === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 rounded-2xl">
        <p className="text-gray-400">Waiting for participants...</p>
      </div>
    );
  }

  // 1-on-1 layout (most common for tutoring)
  if (totalParticipants === 2 && localPeer && remotePeers.length === 1) {
    return (
      <div className="h-full relative">
        {/* Remote peer (main view - fullscreen) */}
        <div className="absolute inset-0">
          <VideoTile
            peer={remotePeers[0]}
            isLocal={false}
            className="w-full h-full"
          />
        </div>

        {/* Local peer (draggable picture-in-picture) */}
        <DraggablePiP initialPosition="bottom-right">
          <VideoTile
            peer={localPeer}
            isLocal={true}
            className="w-full h-full"
          />
        </DraggablePiP>
      </div>
    );
  }

  // Single participant (local only, waiting for remote)
  // Show waiting message with small draggable self-preview in corner (PiP style)
  if (totalParticipants === 1 && localPeer) {
    return (
      <div className="h-full relative">
        {/* Main area - Waiting message */}
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 rounded-2xl">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-500/20 flex items-center justify-center">
              <div className="w-8 h-8 rounded-full bg-primary-500/40 animate-ping" />
            </div>
            <p className="text-lg font-medium text-white mb-2">
              Waiting for other participant...
            </p>
            <p className="text-sm text-gray-400">
              They will appear here when they join
            </p>
          </div>
        </div>

        {/* Local preview - draggable PiP */}
        <DraggablePiP initialPosition="bottom-right">
          <VideoTile
            peer={localPeer}
            isLocal={true}
            className="w-full h-full"
          />
        </DraggablePiP>
      </div>
    );
  }

  // Generic grid for more participants (rare in tutoring)
  const allPeers = [...(localPeer ? [localPeer] : []), ...remotePeers];

  return (
    <div
      className={`
        h-full grid gap-4
        ${totalParticipants === 1 ? 'grid-cols-1' : ''}
        ${totalParticipants === 2 ? 'grid-cols-1 lg:grid-cols-2' : ''}
        ${totalParticipants >= 3 ? 'grid-cols-2 lg:grid-cols-2' : ''}
      `}
    >
      {allPeers.map((peer) => (
        <VideoTile
          key={peer.id}
          peer={peer}
          isLocal={peer.isLocal}
          className="w-full aspect-video"
        />
      ))}
    </div>
  );
};

export default VideoGrid;
