/**
 * Instructor Profile Card Component
 * Modern glassmorphism design with hover effects and micro-animations
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Star, Edit3, Award, Globe, ChevronRight } from 'lucide-react';
import { Card, Badge, Button } from '../UIComponents';
import type { InstructorProfile, UserBasicInfo, LanguageResponse } from '../../types/api';
import { getMediaUrl } from '../../lib/axios';

interface InstructorProfileCardProps {
  profile: InstructorProfile;
  user: UserBasicInfo;
}

const InstructorProfileCard: React.FC<InstructorProfileCardProps> = ({ profile, user }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const fullName = `${user.first_name} ${user.last_name}`;

  const formatPrice = (price?: number | string) => {
    if (!price) return 'Not set';
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return `₹${numPrice.toFixed(0)}`;
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'verified':
        return 'primary';
      case 'pending_review':
        return 'secondary';
      default:
        return 'neutral';
    }
  };

  const formatStatus = (status: string) => {
    return status.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <Card
      className={`
        p-6 h-full relative overflow-hidden
        transition-all duration-500 ease-out
        ${isHovered ? 'shadow-2xl shadow-primary-500/10' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background gradient decoration */}
      <div
        className={`
          absolute -top-20 -right-20 w-40 h-40 rounded-full
          bg-gradient-to-br from-primary-100/50 to-blue-100/50
          blur-2xl transition-all duration-700
          ${isHovered ? 'scale-150 opacity-80' : 'scale-100 opacity-40'}
        `}
      />
      <div
        className={`
          absolute -bottom-10 -left-10 w-32 h-32 rounded-full
          bg-gradient-to-br from-purple-100/30 to-pink-100/30
          blur-2xl transition-all duration-700
          ${isHovered ? 'scale-125 opacity-60' : 'scale-100 opacity-30'}
        `}
      />

      <div className="relative flex flex-col sm:flex-row gap-5">
        {/* Profile Photo with hover effects */}
        <div className="flex-shrink-0 relative group/photo">
          {/* Photo container */}
          <div
            className={`
              relative w-28 h-28 sm:w-36 sm:h-36 rounded-2xl overflow-hidden
              transition-all duration-500
              ${isHovered ? 'shadow-xl shadow-primary-500/20 scale-[1.02]' : 'shadow-lg'}
            `}
          >
            {/* Loading placeholder */}
            {!imageLoaded && (
              <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-100 animate-pulse" />
            )}

            {profile.profile_photo_url ? (
              <img
                src={getMediaUrl(profile.profile_photo_url)}
                alt={fullName}
                onLoad={() => setImageLoaded(true)}
                className={`
                  w-full h-full object-cover
                  transition-all duration-500
                  ${imageLoaded ? 'opacity-100' : 'opacity-0'}
                  ${isHovered ? 'scale-110' : 'scale-100'}
                `}
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-primary-100 to-blue-100 flex items-center justify-center">
                <span className="text-4xl font-bold text-primary-600">
                  {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                </span>
              </div>
            )}

            {/* Gradient overlay */}
            <div
              className={`
                absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent
                transition-opacity duration-300
                ${isHovered ? 'opacity-100' : 'opacity-0'}
              `}
            />
          </div>

          {/* Verified badge */}
          {profile.status === 'verified' && (
            <div
              className={`
                absolute -bottom-2 -right-2 w-10 h-10
                bg-gradient-to-br from-primary-500 to-blue-500
                rounded-xl flex items-center justify-center
                shadow-lg shadow-primary-500/30
                transition-all duration-300
                ${isHovered ? 'scale-110 rotate-3' : 'scale-100 rotate-0'}
              `}
            >
              <Award size={20} className="text-white fill-white/30" />
            </div>
          )}
        </div>

        {/* Profile Info */}
        <div className="flex-grow min-w-0">
          {/* Name and Status */}
          <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
            <div>
              <h2
                className={`
                  text-xl sm:text-2xl font-bold text-gray-900
                  transition-colors duration-300
                  ${isHovered ? 'text-primary-700' : ''}
                `}
              >
                {fullName}
              </h2>
              {profile.headline && (
                <p className="text-gray-600 text-sm mt-0.5 line-clamp-1">
                  {profile.headline}
                </p>
              )}
            </div>
            <Badge variant={getStatusBadgeVariant(profile.status)}>
              {formatStatus(profile.status)}
            </Badge>
          </div>

          {/* Location & Rating */}
          <div className="flex flex-wrap items-center gap-4 mb-4">
            {profile.country_of_birth && (
              <span className="flex items-center gap-1.5 text-sm text-gray-600">
                <div className="w-6 h-6 bg-gray-100 rounded-lg flex items-center justify-center">
                  <MapPin size={12} className="text-gray-500" />
                </div>
                {profile.country_of_birth}
              </span>
            )}
            <span className="flex items-center gap-1.5 text-sm">
              <div className="w-6 h-6 bg-yellow-50 rounded-lg flex items-center justify-center">
                <Star size={12} className="text-yellow-500 fill-yellow-500" />
              </div>
              <span className="font-semibold text-gray-700">New</span>
            </span>
          </div>

          {/* Languages */}
          {profile.languages && profile.languages.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Globe size={14} className="text-gray-400" />
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Languages
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.languages.map((lang: LanguageResponse, idx: number) => (
                  <span
                    key={idx}
                    className={`
                      text-xs font-medium px-3 py-1.5 rounded-lg
                      bg-gradient-to-r from-gray-50 to-gray-100
                      border border-gray-200/50
                      text-gray-700
                      transition-all duration-300
                      hover:from-primary-50 hover:to-blue-50
                      hover:border-primary-200/50 hover:text-primary-700
                    `}
                  >
                    {lang.language}
                    <span className="text-gray-400 ml-1">({lang.proficiency})</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Pricing */}
          <div className="flex items-center gap-6">
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-extrabold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                {formatPrice(profile.hourly_rate)}
              </span>
              <span className="text-sm text-gray-500 font-medium">/hour</span>
            </div>
            {profile.trial_lesson_price && (
              <div className="flex items-center gap-1.5 text-sm">
                <span className="text-gray-400">Trial:</span>
                <span className="font-semibold text-emerald-600">
                  ₹{typeof profile.trial_lesson_price === 'string'
                    ? parseFloat(profile.trial_lesson_price).toFixed(0)
                    : profile.trial_lesson_price.toFixed(0)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Edit Profile Button */}
      <div className="relative mt-5 pt-5 border-t border-gray-100/80">
        <Link to="/dashboard/instructor/onboarding" className="inline-block">
          <Button
            variant="outline"
            size="sm"
            className={`
              gap-2 group/btn
              transition-all duration-300
              ${isHovered ? 'border-primary-300 text-primary-700 bg-primary-50/50' : ''}
            `}
          >
            <Edit3
              size={14}
              className={`
                transition-transform duration-300
                ${isHovered ? 'rotate-12' : 'rotate-0'}
              `}
            />
            Edit Profile
            <ChevronRight
              size={14}
              className={`
                transition-all duration-300 opacity-0 -ml-2
                group-hover/btn:opacity-100 group-hover/btn:ml-0 group-hover/btn:translate-x-0.5
              `}
            />
          </Button>
        </Link>
      </div>

      {/* Bottom accent line */}
      <div
        className={`
          absolute bottom-0 left-0 h-1 rounded-full
          bg-gradient-to-r from-primary-500 to-blue-500
          transition-all duration-500 ease-out
          ${isHovered ? 'w-full' : 'w-0'}
        `}
      />
    </Card>
  );
};

export default InstructorProfileCard;
