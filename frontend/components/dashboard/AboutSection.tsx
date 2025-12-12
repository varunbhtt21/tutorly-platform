import React from 'react';
import { Card } from '../UIComponents';

interface AboutSectionProps {
  bio?: string;
  teachingExperience?: string;
}

const AboutSection: React.FC<AboutSectionProps> = ({ bio, teachingExperience }) => {
  const hasBio = bio && bio.trim().length > 0;
  const hasTeachingExp = teachingExperience && teachingExperience.trim().length > 0;

  if (!hasBio && !hasTeachingExp) {
    return null;
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">About Me</h3>

      {hasBio && (
        <div className="mb-4">
          <p className="text-gray-600 text-sm leading-relaxed">
            {bio.length > 300 ? `${bio.substring(0, 300)}...` : bio}
          </p>
        </div>
      )}

      {hasTeachingExp && (
        <div className="pt-4 border-t border-gray-100">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Teaching Style</h4>
          <p className="text-gray-600 text-sm leading-relaxed">
            {teachingExperience.length > 200
              ? `${teachingExperience.substring(0, 200)}...`
              : teachingExperience}
          </p>
        </div>
      )}
    </Card>
  );
};

export default AboutSection;
