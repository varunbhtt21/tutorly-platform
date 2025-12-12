import React from 'react';
import { Link } from 'react-router-dom';
import { Video, Upload } from 'lucide-react';
import { Card, Button } from '../UIComponents';
import { getMediaUrl } from '../../lib/axios';

interface IntroVideoPlayerProps {
  videoUrl?: string;
}

const IntroVideoPlayer: React.FC<IntroVideoPlayerProps> = ({ videoUrl }) => {
  if (!videoUrl) {
    return (
      <Card className="p-6 h-full flex flex-col">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Introduction Video</h3>
        <div className="flex-grow flex flex-col items-center justify-center bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 p-6">
          <div className="bg-gray-100 p-4 rounded-full mb-4">
            <Video size={32} className="text-gray-400" />
          </div>
          <p className="text-gray-500 text-sm text-center mb-4">
            No introduction video yet
          </p>
          <Link to="/dashboard/instructor/onboarding">
            <Button variant="outline" size="sm" className="gap-2">
              <Upload size={14} />
              Add Video
            </Button>
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Introduction Video</h3>
      <div className="rounded-xl overflow-hidden bg-black aspect-video">
        <video
          src={getMediaUrl(videoUrl)}
          controls
          className="w-full h-full object-contain"
        >
          Your browser does not support the video tag.
        </video>
      </div>
    </Card>
  );
};

export default IntroVideoPlayer;
