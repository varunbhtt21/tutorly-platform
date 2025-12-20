/**
 * HMS (100ms) Video Context
 *
 * Provides 100ms video state management following React Context pattern.
 * Integrates with existing AuthContext for user information.
 *
 * Features:
 * - Auto-joins room with user name from Tutorly auth (no name prompt)
 * - Manages connection state, peers, and media tracks
 * - Provides controls for audio/video/screenshare
 * - Clean separation from chat (uses Tutorly messaging)
 *
 * Architecture:
 * - This context wraps 100ms SDK state
 * - Components consume this context for video UI
 * - Chat remains independent using WebSocketContext
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  ReactNode,
} from 'react';
import {
  HMSRoomProvider,
  useHMSStore,
  useHMSActions,
  selectIsConnectedToRoom,
  selectLocalPeer,
  selectPeers,
  selectIsLocalAudioEnabled,
  selectIsLocalVideoEnabled,
  selectIsLocalScreenShared,
  selectRoomState,
  selectConnectionQuality,
  HMSRoomState,
} from '@100mslive/react-sdk';
import type { HMSPeer } from '@100mslive/react-sdk';

// ============================================================================
// Types
// ============================================================================

export interface HMSContextType {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionState: HMSRoomState;
  error: string | null;

  // Participants
  localPeer: HMSPeer | null;
  peers: HMSPeer[];
  remotePeers: HMSPeer[];

  // Media state
  isAudioEnabled: boolean;
  isVideoEnabled: boolean;
  isScreenSharing: boolean;

  // Actions
  joinRoom: (authToken: string, userName: string) => Promise<void>;
  leaveRoom: () => Promise<void>;
  toggleAudio: () => Promise<void>;
  toggleVideo: () => Promise<void>;
  toggleScreenShare: () => Promise<void>;
}

const HMSContext = createContext<HMSContextType | undefined>(undefined);

// ============================================================================
// Inner Provider (uses HMS hooks)
// ============================================================================

interface HMSProviderInnerProps {
  children: ReactNode;
}

const HMSProviderInner: React.FC<HMSProviderInnerProps> = ({ children }) => {
  const hmsActions = useHMSActions();

  // Selectors
  const isConnected = useHMSStore(selectIsConnectedToRoom);
  const localPeer = useHMSStore(selectLocalPeer);
  const peers = useHMSStore(selectPeers);
  const isAudioEnabled = useHMSStore(selectIsLocalAudioEnabled);
  const isVideoEnabled = useHMSStore(selectIsLocalVideoEnabled);
  const isScreenSharing = useHMSStore(selectIsLocalScreenShared);
  const roomState = useHMSStore(selectRoomState);

  // Local state
  const [error, setError] = useState<string | null>(null);

  // Derived state
  const isConnecting = roomState === HMSRoomState.Connecting;
  const remotePeers = peers.filter((peer) => !peer.isLocal);

  // Join room with auth token
  const joinRoom = useCallback(
    async (authToken: string, userName: string) => {
      try {
        setError(null);

        await hmsActions.join({
          authToken,
          userName,
          settings: {
            isAudioMuted: false,
            isVideoMuted: false,
          },
          // Skip preview - join directly (no name prompt)
          rememberDeviceSelection: true,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to join room';
        setError(message);
        throw err;
      }
    },
    [hmsActions]
  );

  // Leave room
  const leaveRoom = useCallback(async () => {
    try {
      await hmsActions.leave();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to leave room';
      setError(message);
    }
  }, [hmsActions]);

  // Toggle audio
  const toggleAudio = useCallback(async () => {
    try {
      await hmsActions.setLocalAudioEnabled(!isAudioEnabled);
    } catch (err) {
      console.error('Failed to toggle audio:', err);
    }
  }, [hmsActions, isAudioEnabled]);

  // Toggle video
  const toggleVideo = useCallback(async () => {
    try {
      await hmsActions.setLocalVideoEnabled(!isVideoEnabled);
    } catch (err) {
      console.error('Failed to toggle video:', err);
    }
  }, [hmsActions, isVideoEnabled]);

  // Toggle screen share
  const toggleScreenShare = useCallback(async () => {
    try {
      await hmsActions.setScreenShareEnabled(!isScreenSharing);
    } catch (err) {
      console.error('Failed to toggle screen share:', err);
    }
  }, [hmsActions, isScreenSharing]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isConnected) {
        hmsActions.leave();
      }
    };
  }, []);

  const contextValue: HMSContextType = {
    isConnected,
    isConnecting,
    connectionState: roomState,
    error,
    localPeer: localPeer || null,
    peers,
    remotePeers,
    isAudioEnabled,
    isVideoEnabled,
    isScreenSharing,
    joinRoom,
    leaveRoom,
    toggleAudio,
    toggleVideo,
    toggleScreenShare,
  };

  return <HMSContext.Provider value={contextValue}>{children}</HMSContext.Provider>;
};

// ============================================================================
// Main Provider (wraps HMSRoomProvider)
// ============================================================================

interface HMSProviderProps {
  children: ReactNode;
}

export const HMSProvider: React.FC<HMSProviderProps> = ({ children }) => {
  return (
    <HMSRoomProvider>
      <HMSProviderInner>{children}</HMSProviderInner>
    </HMSRoomProvider>
  );
};

// ============================================================================
// Hook
// ============================================================================

export const useHMS = (): HMSContextType => {
  const context = useContext(HMSContext);

  if (context === undefined) {
    throw new Error('useHMS must be used within an HMSProvider');
  }

  return context;
};

export default HMSContext;
