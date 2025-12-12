import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Star, Edit3 } from 'lucide-react';
import { Card, Badge, Button } from '../UIComponents';
import type { InstructorProfile, UserBasicInfo, LanguageResponse } from '../../types/api';
import { getMediaUrl } from '../../lib/axios';

interface InstructorProfileCardProps {
  profile: InstructorProfile;
  user: UserBasicInfo;
}

const InstructorProfileCard: React.FC<InstructorProfileCardProps> = ({ profile, user }) => {
  const fullName = `${user.first_name} ${user.last_name}`;

  const formatPrice = (price?: number | string) => {
    if (!price) return 'Not set';
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return `$${numPrice.toFixed(0)}/hr`;
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
    <Card className="p-6">
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Profile Photo */}
        <div className="flex-shrink-0">
          {profile.profile_photo_url ? (
            <img
              src={getMediaUrl(profile.profile_photo_url)}
              alt={fullName}
              className="w-24 h-24 sm:w-32 sm:h-32 rounded-2xl object-cover border-2 border-white shadow-lg"
            />
          ) : (
            <div className="w-24 h-24 sm:w-32 sm:h-32 rounded-2xl bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center border-2 border-white shadow-lg">
              <span className="text-3xl font-bold text-primary-600">
                {user.first_name.charAt(0)}{user.last_name.charAt(0)}
              </span>
            </div>
          )}
        </div>

        {/* Profile Info */}
        <div className="flex-grow">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{fullName}</h2>
              {profile.headline && (
                <p className="text-gray-600 text-sm mt-0.5">{profile.headline}</p>
              )}
            </div>
            <Badge variant={getStatusBadgeVariant(profile.status)}>
              {formatStatus(profile.status)}
            </Badge>
          </div>

          {/* Location & Rating */}
          <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-600">
            {profile.country_of_birth && (
              <span className="flex items-center gap-1">
                <MapPin size={14} className="text-gray-400" />
                {profile.country_of_birth}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Star size={14} className="text-yellow-400 fill-yellow-400" />
              <span className="font-medium">New</span>
            </span>
          </div>

          {/* Languages */}
          {profile.languages && profile.languages.length > 0 && (
            <div className="mt-3">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Languages:</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {profile.languages.map((lang: LanguageResponse, idx: number) => (
                  <span
                    key={idx}
                    className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full"
                  >
                    {lang.language} ({lang.proficiency})
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Pricing */}
          <div className="flex items-center gap-4 mt-4">
            <div>
              <span className="text-lg font-bold text-gray-900">{formatPrice(profile.hourly_rate)}</span>
              {profile.trial_lesson_price && (
                <span className="text-sm text-gray-500 ml-2">
                  (Trial: ${typeof profile.trial_lesson_price === 'string' ? parseFloat(profile.trial_lesson_price).toFixed(0) : profile.trial_lesson_price.toFixed(0)})
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Button */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <Link to="/dashboard/instructor/onboarding">
          <Button variant="outline" size="sm" className="gap-2">
            <Edit3 size={14} />
            Edit Profile
          </Button>
        </Link>
      </div>
    </Card>
  );
};

export default InstructorProfileCard;
