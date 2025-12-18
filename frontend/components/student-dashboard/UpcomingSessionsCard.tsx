/**
 * Upcoming Sessions Card Component for Student Dashboard
 *
 * Displays the next 7 days of upcoming sessions with:
 * - Instructor info, subject, date/time
 * - Join meeting button (enabled 15 mins before)
 * - Cancel/Reschedule options
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Calendar,
  Clock,
  Video,
  X,
  RefreshCw,
  ChevronRight,
  Sparkles,
  User,
  ExternalLink,
} from 'lucide-react';
import { Card, Button, Badge } from '../UIComponents';
import { UpcomingSession } from '../../services/studentAPI';

interface UpcomingSessionsCardProps {
  sessions: UpcomingSession[];
  onCancel?: (sessionId: number) => void;
  onReschedule?: (sessionId: number) => void;
}

interface SessionItemProps {
  session: UpcomingSession;
  index: number;
  onCancel?: (sessionId: number) => void;
  onReschedule?: (sessionId: number) => void;
}

const SessionItem: React.FC<SessionItemProps> = ({
  session,
  index,
  onCancel,
  onReschedule,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    let dayText = '';
    let isToday = false;
    let isTomorrow = false;

    if (date.toDateString() === today.toDateString()) {
      dayText = 'Today';
      isToday = true;
    } else if (date.toDateString() === tomorrow.toDateString()) {
      dayText = 'Tomorrow';
      isTomorrow = true;
    } else {
      dayText = date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      });
    }

    const timeText = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });

    return { dayText, timeText, isToday, isTomorrow };
  };

  const { dayText, timeText, isToday, isTomorrow } = formatDateTime(session.start_at);

  const handleJoinMeeting = () => {
    if (session.meeting_link) {
      window.open(session.meeting_link, '_blank');
    }
  };

  return (
    <div
      className={`
        relative flex items-center gap-4 p-4
        bg-white/60 backdrop-blur-sm rounded-xl
        border border-white/50
        transition-all duration-300 ease-out
        hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50
        ${isHovered ? 'scale-[1.01] border-primary-200/50' : 'scale-100'}
      `}
      style={{
        animation: `slideInRight 0.4s ease-out forwards`,
        animationDelay: `${index * 0.1}s`,
        opacity: 0,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowActions(false);
      }}
    >
      {/* Today indicator */}
      {isToday && session.can_join && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-lg animate-pulse">
          LIVE
        </div>
      )}

      {/* Instructor Avatar */}
      <div className="relative flex-shrink-0">
        {session.instructor_photo_url ? (
          <img
            src={session.instructor_photo_url}
            alt={session.instructor_name}
            className="w-12 h-12 rounded-full object-cover border-2 border-white shadow-sm"
          />
        ) : (
          <div
            className={`
              w-12 h-12 rounded-full flex items-center justify-center
              transition-all duration-300
              ${isToday
                ? 'bg-gradient-to-br from-primary-100 to-blue-100'
                : isTomorrow
                  ? 'bg-gradient-to-br from-amber-100 to-orange-100'
                  : 'bg-gray-100'
              }
            `}
          >
            <User
              size={20}
              className={`
                ${isToday ? 'text-primary-600' : isTomorrow ? 'text-amber-600' : 'text-gray-500'}
              `}
            />
          </div>
        )}
        {/* Online ring for joinable sessions */}
        {session.can_join && (
          <span className="absolute -bottom-0.5 -right-0.5 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-green-500 border-2 border-white"></span>
          </span>
        )}
      </div>

      {/* Session Info */}
      <div className="flex-grow min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="font-semibold text-gray-900 truncate">
            {session.instructor_name}
          </h4>
          {session.session_type === 'trial' && (
            <Badge variant="secondary">
              <Sparkles size={10} className="mr-1" />
              Trial
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span
            className={`
              flex items-center gap-1.5 font-medium
              ${isToday ? 'text-primary-600' : isTomorrow ? 'text-amber-600' : 'text-gray-500'}
            `}
          >
            <Calendar size={13} />
            {dayText}
          </span>
          <span className="flex items-center gap-1.5 text-gray-500">
            <Clock size={13} />
            {timeText}
          </span>
          <span className="text-gray-400 text-xs">
            {session.duration_minutes}min
          </span>
        </div>
        {session.subject && (
          <span className="inline-block mt-1 text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
            {session.subject}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex-shrink-0 flex items-center gap-2">
        {/* Action dropdown toggle */}
        {(session.can_cancel || session.can_reschedule) && (
          <div className="relative">
            <button
              onClick={() => setShowActions(!showActions)}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </button>

            {/* Dropdown */}
            {showActions && (
              <div className="absolute right-0 top-full mt-1 w-40 bg-white rounded-xl shadow-xl border border-gray-100 py-1 z-10">
                {session.can_reschedule && (
                  <button
                    onClick={() => {
                      onReschedule?.(session.session_id);
                      setShowActions(false);
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <RefreshCw size={14} />
                    Reschedule
                  </button>
                )}
                {session.can_cancel && (
                  <button
                    onClick={() => {
                      onCancel?.(session.session_id);
                      setShowActions(false);
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <X size={14} />
                    Cancel
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Join Button */}
        <Button
          variant={session.can_join ? 'primary' : 'secondary'}
          size="sm"
          onClick={handleJoinMeeting}
          disabled={!session.can_join}
          className={`
            gap-1.5 transition-all duration-300
            ${isHovered && session.can_join ? 'shadow-lg' : 'shadow-none'}
          `}
        >
          {session.can_join ? (
            <>
              <Video size={14} />
              Join
            </>
          ) : (
            <>
              <Clock size={14} />
              Waiting
            </>
          )}
        </Button>
      </div>

      {/* Left accent line */}
      <div
        className={`
          absolute left-0 top-1/2 -translate-y-1/2 w-1 rounded-r-full
          transition-all duration-300
          ${isToday
            ? 'h-full bg-gradient-to-b from-primary-500 to-blue-500'
            : isTomorrow
              ? 'h-3/4 bg-gradient-to-b from-amber-400 to-orange-400'
              : 'h-1/2 bg-gray-200'
          }
          ${isHovered ? 'h-full' : ''}
        `}
      />
    </div>
  );
};

export const UpcomingSessionsCard: React.FC<UpcomingSessionsCardProps> = ({
  sessions,
  onCancel,
  onReschedule,
}) => {
  if (sessions.length === 0) {
    return (
      <Card className="p-6 h-full">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <Calendar size={18} className="text-primary-600" />
          </div>
          Upcoming Sessions
        </h3>
        <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 text-center border-2 border-dashed border-gray-200/80">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <Calendar size={28} className="text-gray-400" />
          </div>
          <h4 className="font-semibold text-gray-700 mb-1">No upcoming sessions</h4>
          <p className="text-gray-400 text-sm max-w-xs mx-auto mb-4">
            Book a session with your favorite instructor to start learning
          </p>
          <Link
            to="/instructors"
            className="inline-flex items-center gap-2 text-primary-600 font-medium text-sm hover:text-primary-700 transition-colors"
          >
            Find Instructors
            <ExternalLink size={14} />
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 h-full">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <Calendar size={18} className="text-primary-600" />
          </div>
          Upcoming Sessions
          <span className="ml-2 text-sm font-medium text-gray-400">
            ({sessions.length})
          </span>
        </h3>
        <Link
          to="/my-sessions"
          className="flex items-center gap-1 text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors group"
        >
          View All
          <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      <div className="space-y-3">
        {sessions.slice(0, 5).map((session, index) => (
          <SessionItem
            key={session.session_id}
            session={session}
            index={index}
            onCancel={onCancel}
            onReschedule={onReschedule}
          />
        ))}
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </Card>
  );
};

export default UpcomingSessionsCard;
