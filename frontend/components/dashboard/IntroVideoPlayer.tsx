/**
 * Intro Video Player Component
 * Modern video player with glassmorphism and hover effects
 */

import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Video, Upload, Play, Pause, Volume2, VolumeX, Maximize2 } from 'lucide-react';
import { Card, Button } from '../UIComponents';
import { getMediaUrl } from '../../lib/axios';

interface IntroVideoPlayerProps {
  videoUrl?: string;
}

const IntroVideoPlayer: React.FC<IntroVideoPlayerProps> = ({ videoUrl }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [showControls, setShowControls] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMuteToggle = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
      }
    }
  };

  if (!videoUrl) {
    return (
      <Card
        className={`
          p-5 h-full flex flex-col relative overflow-hidden
          transition-all duration-300 ease-out
          ${isHovered ? 'shadow-xl shadow-gray-200/50' : ''}
        `}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Background decoration */}
        <div
          className={`
            absolute -top-10 -right-10 w-24 h-24 rounded-full
            bg-gradient-to-br from-purple-50 to-pink-50
            blur-2xl transition-all duration-500
            ${isHovered ? 'scale-125 opacity-100' : 'scale-100 opacity-50'}
          `}
        />

        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2 relative">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center">
            <Video size={16} className="text-purple-600" />
          </div>
          Introduction Video
        </h3>

        <div
          className={`
            flex-grow flex flex-col items-center justify-center
            bg-gradient-to-br from-gray-50 to-white rounded-xl
            border-2 border-dashed
            transition-all duration-300
            ${isHovered ? 'border-primary-300 bg-primary-50/20' : 'border-gray-200'}
            p-6 relative
          `}
        >
          <div
            className={`
              w-16 h-16 rounded-2xl flex items-center justify-center mb-4
              transition-all duration-300
              ${isHovered
                ? 'bg-gradient-to-br from-primary-100 to-blue-100 shadow-lg'
                : 'bg-gray-100'
              }
            `}
          >
            <Video
              size={28}
              className={`
                transition-colors duration-300
                ${isHovered ? 'text-primary-600' : 'text-gray-400'}
              `}
            />
          </div>
          <p
            className={`
              text-sm text-center mb-4 font-medium
              transition-colors duration-300
              ${isHovered ? 'text-gray-700' : 'text-gray-500'}
            `}
          >
            No introduction video yet
          </p>
          <p className="text-xs text-gray-400 text-center mb-4 max-w-xs">
            Add a video to introduce yourself to potential students
          </p>
          <Link to="/dashboard/instructor/onboarding">
            <Button
              variant={isHovered ? 'primary' : 'outline'}
              size="sm"
              className={`
                gap-2 transition-all duration-300
                ${isHovered ? 'shadow-lg shadow-primary-500/20' : ''}
              `}
            >
              <Upload size={14} />
              Add Video
            </Button>
          </Link>
        </div>

        {/* Bottom accent line */}
        <div
          className={`
            absolute bottom-0 left-0 h-0.5 rounded-full
            bg-gradient-to-r from-purple-400 to-pink-400
            transition-all duration-500 ease-out
            ${isHovered ? 'w-full' : 'w-0'}
          `}
        />
      </Card>
    );
  }

  return (
    <Card
      className={`
        p-5 h-full relative overflow-hidden
        transition-all duration-300 ease-out
        ${isHovered ? 'shadow-xl shadow-gray-200/50' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background decoration */}
      <div
        className={`
          absolute -top-10 -right-10 w-24 h-24 rounded-full
          bg-gradient-to-br from-purple-50 to-pink-50
          blur-2xl transition-all duration-500
          ${isHovered ? 'scale-125 opacity-100' : 'scale-100 opacity-50'}
        `}
      />

      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2 relative">
        <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center">
          <Video size={16} className="text-purple-600" />
        </div>
        Introduction Video
      </h3>

      <div
        className="relative rounded-xl overflow-hidden bg-gray-900 aspect-video group"
        onMouseEnter={() => setShowControls(true)}
        onMouseLeave={() => setShowControls(false)}
      >
        <video
          ref={videoRef}
          src={getMediaUrl(videoUrl)}
          className={`
            w-full h-full object-contain
            transition-all duration-500
            ${isHovered ? 'scale-[1.02]' : 'scale-100'}
          `}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        />

        {/* Custom overlay controls */}
        <div
          className={`
            absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent
            flex items-center justify-center
            transition-opacity duration-300
            ${showControls || !isPlaying ? 'opacity-100' : 'opacity-0'}
          `}
        >
          {/* Large play/pause button */}
          <button
            onClick={handlePlayPause}
            className={`
              w-16 h-16 rounded-full flex items-center justify-center
              bg-white/20 backdrop-blur-sm border border-white/30
              transition-all duration-300
              hover:bg-white/30 hover:scale-110
              ${isPlaying ? 'opacity-0 group-hover:opacity-100' : 'opacity-100'}
            `}
          >
            {isPlaying ? (
              <Pause size={28} className="text-white" />
            ) : (
              <Play size={28} className="text-white ml-1" />
            )}
          </button>
        </div>

        {/* Bottom controls bar */}
        <div
          className={`
            absolute bottom-0 left-0 right-0 px-4 py-3
            flex items-center justify-between
            bg-gradient-to-t from-black/80 to-transparent
            transition-all duration-300
            ${showControls ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}
          `}
        >
          <div className="flex items-center gap-2">
            <button
              onClick={handlePlayPause}
              className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
            >
              {isPlaying ? (
                <Pause size={18} className="text-white" />
              ) : (
                <Play size={18} className="text-white" />
              )}
            </button>
            <button
              onClick={handleMuteToggle}
              className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
            >
              {isMuted ? (
                <VolumeX size={18} className="text-white" />
              ) : (
                <Volume2 size={18} className="text-white" />
              )}
            </button>
          </div>
          <button
            onClick={handleFullscreen}
            className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
          >
            <Maximize2 size={18} className="text-white" />
          </button>
        </div>
      </div>

      {/* Bottom accent line */}
      <div
        className={`
          absolute bottom-0 left-0 h-0.5 rounded-full
          bg-gradient-to-r from-purple-400 to-pink-400
          transition-all duration-500 ease-out
          ${isHovered ? 'w-full' : 'w-0'}
        `}
      />
    </Card>
  );
};

export default IntroVideoPlayer;
