/**
 * Instructor Card Component
 * Modern design with micro-animations and polished interactions
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import type { InstructorProfile } from '../types/api';
import { Star, Globe, Play, Heart, MessageCircle, Award, Clock } from 'lucide-react';
import { Button, Badge, Card } from './UIComponents';
import { getMediaUrl } from '../lib/axios';

interface Props {
  instructor: InstructorProfile;
}

const InstructorCard: React.FC<Props> = ({ instructor }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  // Parse hourly rate (can be string or number from API)
  const hourlyRate = typeof instructor.hourly_rate === 'string'
    ? parseFloat(instructor.hourly_rate)
    : instructor.hourly_rate || 0;

  const trialPrice = typeof instructor.trial_lesson_price === 'string'
    ? parseFloat(instructor.trial_lesson_price)
    : instructor.trial_lesson_price || 0;

  // Get display name from languages (first language name, or use placeholder)
  const displayName = instructor.headline ||
    (instructor.languages?.[0]?.language ? `${instructor.languages[0].language} Tutor` : 'Language Tutor');

  // Generate avatar URL (use getMediaUrl to convert relative paths to full URLs)
  const avatarUrl = getMediaUrl(instructor.profile_photo_url) ||
    `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=random&size=256`;

  return (
    <Card
      className={`
        relative overflow-hidden group
        border-white/60 hover:border-primary-200
        transition-all duration-500 ease-out
        hover:shadow-2xl hover:shadow-primary-500/10
        ${isHovered ? 'scale-[1.01]' : 'scale-100'}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient overlay on hover */}
      <div
        className={`
          absolute inset-0 bg-gradient-to-r from-primary-500/5 to-blue-500/5
          transition-opacity duration-500
          ${isHovered ? 'opacity-100' : 'opacity-0'}
        `}
      />

      <div className="flex flex-col md:flex-row relative">
        {/* Left / Top - Image Section */}
        <div className="w-full md:w-72 shrink-0 relative overflow-hidden">
          {/* Image placeholder while loading */}
          {!imageLoaded && (
            <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-100 animate-pulse" />
          )}

          <img
            src={avatarUrl}
            alt={displayName}
            onLoad={() => setImageLoaded(true)}
            className={`
              w-full h-64 md:h-full object-cover
              transition-all duration-700 ease-out
              ${isHovered ? 'scale-110' : 'scale-100'}
              ${imageLoaded ? 'opacity-100' : 'opacity-0'}
            `}
          />

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent" />

          {/* Top badges */}
          <div className="absolute top-3 left-3 right-3 flex justify-between items-start">
            {/* Available badge */}
            {instructor.is_onboarding_complete && (
              <div
                className={`
                  bg-white/95 backdrop-blur-sm text-green-700 text-xs font-bold
                  px-3 py-1.5 rounded-full shadow-lg
                  flex items-center gap-1.5 border border-white/50
                  transition-all duration-300
                  ${isHovered ? 'translate-y-0 opacity-100' : 'translate-y-0 opacity-100'}
                `}
              >
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                Available Now
              </div>
            )}

            {/* Like button */}
            <button
              onClick={(e) => {
                e.preventDefault();
                setIsLiked(!isLiked);
              }}
              className={`
                p-2 rounded-full backdrop-blur-sm shadow-lg
                transition-all duration-300 transform
                ${isLiked
                  ? 'bg-red-500 text-white scale-110'
                  : 'bg-white/90 text-gray-600 hover:bg-white hover:text-red-500 hover:scale-110'
                }
              `}
            >
              <Heart
                size={18}
                className={isLiked ? 'fill-current' : ''}
              />
            </button>
          </div>

          {/* Video play button (if has intro video) */}
          {instructor.intro_video_url && (
            <div
              className={`
                absolute bottom-3 left-3
                transition-all duration-300
                ${isHovered ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'}
              `}
            >
              <button className="flex items-center gap-2 bg-white/95 backdrop-blur-sm px-3 py-2 rounded-full text-xs font-semibold text-gray-800 shadow-lg hover:bg-white transition-all hover:scale-105">
                <Play size={14} className="fill-primary-600 text-primary-600" />
                Watch Intro
              </button>
            </div>
          )}
        </div>

        {/* Right / Content Section */}
        <div className="p-6 flex flex-col flex-grow relative">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div className="flex-grow">
              <div className="flex items-center gap-2 mb-1">
                <h3
                  className={`
                    text-xl font-bold text-gray-900
                    transition-colors duration-300
                    ${isHovered ? 'text-primary-600' : ''}
                  `}
                >
                  {displayName}
                </h3>
                {instructor.status === 'verified' && (
                  <div className="text-primary-600" title="Verified Tutor">
                    <Award size={18} className="fill-primary-100" />
                  </div>
                )}
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-500">
                <span className="flex items-center gap-1.5 font-medium">
                  <Globe size={14} />
                  {instructor.country_of_birth || 'Global'}
                </span>
                {instructor.languages && instructor.languages.length > 0 && (
                  <span className="flex items-center gap-1">
                    <MessageCircle size={14} />
                    {instructor.languages.map(l => l.language).slice(0, 2).join(', ')}
                  </span>
                )}
              </div>
            </div>

            {/* Rating */}
            <div className="text-right">
              <div
                className={`
                  inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl
                  bg-gradient-to-r from-yellow-50 to-amber-50
                  border border-yellow-200/50
                  transition-all duration-300
                  ${isHovered ? 'shadow-md shadow-yellow-200/50 scale-105' : ''}
                `}
              >
                <Star size={16} className="text-yellow-500 fill-yellow-500" />
                <span className="font-bold text-gray-900">5.0</span>
              </div>
              <div className="text-xs text-gray-400 font-medium mt-1.5">
                New tutor
              </div>
            </div>
          </div>

          {/* Bio */}
          <p className="text-gray-600 text-sm line-clamp-2 mb-5 leading-relaxed flex-grow">
            {instructor.bio || 'Passionate about teaching and helping students achieve their learning goals.'}
          </p>

          {/* Tags/Badges */}
          <div className="flex flex-wrap gap-2 mb-5">
            {instructor.languages?.slice(0, 3).map((lang, i) => (
              <Badge
                key={i}
                variant="primary"
              >
                {lang.language}
              </Badge>
            ))}
            {instructor.education?.slice(0, 1).map((edu, i) => (
              <Badge key={`edu-${i}`} variant="secondary">
                {edu.degree}
              </Badge>
            ))}
          </div>

          {/* Footer - Price and CTA */}
          <div
            className={`
              pt-4 border-t border-gray-100/80
              flex items-center justify-between mt-auto
              transition-all duration-300
            `}
          >
            <div>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-extrabold text-gray-900">
                  ₹{hourlyRate || 25}
                </span>
                <span className="text-sm text-gray-500 font-medium">/hour</span>
              </div>
              {trialPrice > 0 && (
                <div className="flex items-center gap-1.5 mt-1">
                  <Clock size={12} className="text-green-600" />
                  <span className="text-xs text-green-600 font-semibold">
                    ₹{trialPrice} trial lesson
                  </span>
                </div>
              )}
            </div>

            <Link to={`/instructors/${instructor.id}`}>
              <Button
                className={`
                  shadow-lg shadow-primary-500/20
                  transition-all duration-300
                  ${isHovered ? 'shadow-xl shadow-primary-500/30 scale-105' : ''}
                `}
              >
                View Profile
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Bottom accent line on hover */}
      <div
        className={`
          absolute bottom-0 left-0 h-1 bg-gradient-to-r from-primary-500 to-blue-500
          transition-all duration-500 ease-out
          ${isHovered ? 'w-full' : 'w-0'}
        `}
      />
    </Card>
  );
};

export default InstructorCard;
