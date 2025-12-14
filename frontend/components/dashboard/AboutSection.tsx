/**
 * About Section Component
 * Modern glassmorphism card with subtle animations
 */

import React, { useState } from 'react';
import { User, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from '../UIComponents';

interface AboutSectionProps {
  bio?: string;
  teachingExperience?: string;
}

const AboutSection: React.FC<AboutSectionProps> = ({ bio, teachingExperience }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const hasBio = bio && bio.trim().length > 0;
  const hasTeachingExp = teachingExperience && teachingExperience.trim().length > 0;

  if (!hasBio && !hasTeachingExp) {
    return null;
  }

  const bioTruncateLength = 200;
  const teachingTruncateLength = 150;
  const shouldShowExpand = (hasBio && bio.length > bioTruncateLength) ||
    (hasTeachingExp && teachingExperience.length > teachingTruncateLength);

  return (
    <Card
      className={`
        p-5 relative overflow-hidden
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
          bg-gradient-to-br from-primary-50 to-blue-50
          blur-2xl transition-all duration-500
          ${isHovered ? 'scale-125 opacity-100' : 'scale-100 opacity-50'}
        `}
      />

      <div className="relative">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-100 to-blue-100 rounded-lg flex items-center justify-center">
            <User size={16} className="text-primary-600" />
          </div>
          About Me
        </h3>

        {hasBio && (
          <div className="mb-4">
            <p className="text-gray-600 text-sm leading-relaxed">
              {isExpanded || bio.length <= bioTruncateLength
                ? bio
                : `${bio.substring(0, bioTruncateLength)}...`}
            </p>
          </div>
        )}

        {hasTeachingExp && (
          <div
            className={`
              pt-4 border-t border-gray-100/80
              transition-all duration-300
              ${isExpanded ? 'opacity-100' : hasBio ? 'opacity-80' : 'opacity-100'}
            `}
          >
            <div className="flex items-center gap-2 mb-2">
              <BookOpen size={14} className="text-gray-400" />
              <h4 className="text-sm font-semibold text-gray-700">Teaching Style</h4>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed">
              {isExpanded || teachingExperience.length <= teachingTruncateLength
                ? teachingExperience
                : `${teachingExperience.substring(0, teachingTruncateLength)}...`}
            </p>
          </div>
        )}

        {/* Expand/Collapse button */}
        {shouldShowExpand && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={`
              mt-4 flex items-center gap-1.5 text-sm font-medium
              transition-colors duration-300
              ${isExpanded ? 'text-gray-500 hover:text-gray-700' : 'text-primary-600 hover:text-primary-700'}
            `}
          >
            {isExpanded ? (
              <>
                <ChevronUp size={16} />
                Show less
              </>
            ) : (
              <>
                <ChevronDown size={16} />
                Read more
              </>
            )}
          </button>
        )}
      </div>

      {/* Bottom accent line */}
      <div
        className={`
          absolute bottom-0 left-0 h-0.5 rounded-full
          bg-gradient-to-r from-primary-400 to-blue-400
          transition-all duration-500 ease-out
          ${isHovered ? 'w-full' : 'w-0'}
        `}
      />
    </Card>
  );
};

export default AboutSection;
