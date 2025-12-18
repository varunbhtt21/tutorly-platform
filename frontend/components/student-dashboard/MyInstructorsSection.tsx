/**
 * My Instructors Section Component for Student Dashboard
 *
 * Displays instructors the student has worked with:
 * - Instructor card with photo, name, headline
 * - Total sessions with each instructor
 * - Last session date
 * - Book again button
 * - Link to instructor profile
 */

import React from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Star,
  Calendar,
  BookOpen,
  ChevronRight,
  MessageCircle,
  ExternalLink,
} from 'lucide-react';
import { Card, Button, Badge } from '../UIComponents';
import { MyInstructor } from '../../services/studentAPI';

interface MyInstructorsSectionProps {
  instructors: MyInstructor[];
  onBookAgain?: (instructorId: number) => void;
  onMessage?: (instructorId: number) => void;
}

interface InstructorItemProps {
  instructor: MyInstructor;
  index: number;
  onBookAgain?: (instructorId: number) => void;
  onMessage?: (instructorId: number) => void;
}

const InstructorItem: React.FC<InstructorItemProps> = ({
  instructor,
  index,
  onBookAgain,
  onMessage,
}) => {
  const formatLastSession = (dateString: string | null) => {
    if (!dateString) return 'No sessions yet';

    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatPrice = (price: number | null, currency: string) => {
    if (price === null) return 'N/A';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div
      className="group relative bg-white/60 backdrop-blur-sm rounded-xl border border-white/50 p-4 transition-all duration-300 hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50 hover:scale-[1.01]"
      style={{
        animation: `fadeIn 0.4s ease-out forwards`,
        animationDelay: `${index * 0.1}s`,
        opacity: 0,
      }}
    >
      <div className="flex items-start gap-4">
        {/* Instructor Photo */}
        <Link
          to={`/instructor/${instructor.instructor_id}`}
          className="relative flex-shrink-0"
        >
          {instructor.photo_url ? (
            <img
              src={instructor.photo_url}
              alt={instructor.name}
              className="w-14 h-14 rounded-xl object-cover border-2 border-white shadow-sm group-hover:scale-105 transition-transform"
            />
          ) : (
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-100 to-blue-100 flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
              <User size={24} className="text-primary-600" />
            </div>
          )}
          {/* Rating badge */}
          {instructor.average_rating && (
            <div className="absolute -bottom-1 -right-1 bg-white rounded-lg px-1.5 py-0.5 shadow-sm border border-gray-100 flex items-center gap-0.5">
              <Star size={10} className="text-amber-400 fill-amber-400" />
              <span className="text-[10px] font-bold text-gray-700">
                {instructor.average_rating.toFixed(1)}
              </span>
            </div>
          )}
        </Link>

        {/* Instructor Info */}
        <div className="flex-grow min-w-0">
          <Link
            to={`/instructor/${instructor.instructor_id}`}
            className="hover:text-primary-600 transition-colors"
          >
            <h4 className="font-semibold text-gray-900 truncate">
              {instructor.name}
            </h4>
          </Link>
          {instructor.headline && (
            <p className="text-sm text-gray-500 truncate mt-0.5">
              {instructor.headline}
            </p>
          )}

          {/* Stats */}
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <BookOpen size={12} className="text-primary-500" />
              <span className="font-medium text-gray-700">{instructor.total_sessions_with}</span>
              {' '}sessions
            </span>
            <span className="flex items-center gap-1">
              <Calendar size={12} className="text-gray-400" />
              {formatLastSession(instructor.last_session_date)}
            </span>
          </div>

          {/* Price */}
          {instructor.regular_session_price && (
            <div className="mt-2">
              <span className="text-xs text-gray-500">
                From{' '}
                <span className="font-semibold text-gray-900">
                  {formatPrice(instructor.regular_session_price, instructor.currency)}
                </span>
                /hr
              </span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 flex-shrink-0">
          <Button
            variant="primary"
            size="sm"
            onClick={() => onBookAgain?.(instructor.instructor_id)}
            className="gap-1"
          >
            <Calendar size={14} />
            Book
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onMessage?.(instructor.instructor_id)}
            className="gap-1 text-gray-500 hover:text-primary-600"
          >
            <MessageCircle size={14} />
            Message
          </Button>
        </div>
      </div>

      {/* Hover gradient overlay */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
    </div>
  );
};

export const MyInstructorsSection: React.FC<MyInstructorsSectionProps> = ({
  instructors,
  onBookAgain,
  onMessage,
}) => {
  if (instructors.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <User size={18} className="text-blue-600" />
          </div>
          My Instructors
        </h3>
        <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 text-center border-2 border-dashed border-gray-200/80">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <User size={28} className="text-gray-400" />
          </div>
          <h4 className="font-semibold text-gray-700 mb-1">No instructors yet</h4>
          <p className="text-gray-400 text-sm max-w-xs mx-auto mb-4">
            Your instructors will appear here after you complete your first session
          </p>
          <Link
            to="/instructors"
            className="inline-flex items-center gap-2 text-primary-600 font-medium text-sm hover:text-primary-700 transition-colors"
          >
            Browse Instructors
            <ExternalLink size={14} />
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <User size={18} className="text-blue-600" />
          </div>
          My Instructors
          <span className="ml-2 text-sm font-medium text-gray-400">
            ({instructors.length})
          </span>
        </h3>
        <Link
          to="/instructors"
          className="flex items-center gap-1 text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors group"
        >
          Find More
          <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      <div className="space-y-3">
        {instructors.slice(0, 4).map((instructor, index) => (
          <InstructorItem
            key={instructor.instructor_id}
            instructor={instructor}
            index={index}
            onBookAgain={onBookAgain}
            onMessage={onMessage}
          />
        ))}
      </div>

      {instructors.length > 4 && (
        <div className="mt-4 pt-4 border-t border-gray-100 text-center">
          <Link
            to="/my-instructors"
            className="text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            View all {instructors.length} instructors
          </Link>
        </div>
      )}

      {/* CSS animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </Card>
  );
};

export default MyInstructorsSection;
