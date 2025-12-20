/**
 * Upcoming Sessions List Component
 * Modern design with staggered animations and interactive session cards
 * Supports "In Progress" sessions with live badge and classroom link
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Clock, User, ChevronRight, Video, Sparkles, Radio } from 'lucide-react';
import { Card, Button, Badge } from '../UIComponents';
import type { UpcomingSession } from '../../types/api';

interface UpcomingSessionsListProps {
  sessions: UpcomingSession[];
}

// Session card with hover effects
interface SessionCardProps {
  session: UpcomingSession;
  index: number;
}

const SessionCard: React.FC<SessionCardProps> = ({ session, index }) => {
  const [isHovered, setIsHovered] = useState(false);

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
      dayText = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    }

    const timeText = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });

    return { dayText, timeText, isToday, isTomorrow };
  };

  const { dayText, timeText, isToday, isTomorrow } = formatDateTime(session.start_at);
  const isInProgress = session.is_in_progress;

  return (
    <div
      className={`
        relative flex items-center gap-4 p-4
        bg-white/60 backdrop-blur-sm rounded-xl
        border transition-all duration-300 ease-out
        hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50
        ${isInProgress
          ? 'border-green-300 bg-green-50/60'
          : 'border-white/50'
        }
        ${isHovered ? 'scale-[1.01] border-primary-200/50' : 'scale-100'}
      `}
      style={{
        animation: `slideInRight 0.4s ease-out forwards`,
        animationDelay: `${index * 0.1}s`,
        opacity: 0,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* In Progress / Live indicator */}
      {isInProgress && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full shadow-lg flex items-center gap-1">
          <Radio size={10} className="animate-pulse" />
          LIVE
        </div>
      )}

      {/* Today indicator (only if not in progress) */}
      {isToday && !isInProgress && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-primary-500 to-blue-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-lg animate-pulse">
          NOW
        </div>
      )}

      {/* Student Avatar with ring animation */}
      <div className="relative flex-shrink-0">
        <div
          className={`
            w-12 h-12 rounded-full flex items-center justify-center
            transition-all duration-300
            ${isInProgress
              ? 'bg-gradient-to-br from-green-100 to-emerald-100'
              : isToday
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
              ${isInProgress
                ? 'text-green-600'
                : isToday
                  ? 'text-primary-600'
                  : isTomorrow
                    ? 'text-amber-600'
                    : 'text-gray-500'
              }
            `}
          />
        </div>
        {/* Online ring - show for in-progress sessions */}
        {(isInProgress || isToday) && (
          <span className="absolute -bottom-0.5 -right-0.5 flex h-4 w-4">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isInProgress ? 'bg-green-400' : 'bg-green-400'}`}></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-green-500 border-2 border-white"></span>
          </span>
        )}
      </div>

      {/* Session Info */}
      <div className="flex-grow min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="font-semibold text-gray-900 truncate">
            {session.student_name}
          </h4>
          {isInProgress && (
            <Badge variant="secondary" className="!bg-green-100 !text-green-700">
              <Radio size={10} className="mr-1" />
              In Progress
            </Badge>
          )}
          {session.is_trial && !isInProgress && (
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
              ${isInProgress
                ? 'text-green-600'
                : isToday
                  ? 'text-primary-600'
                  : isTomorrow
                    ? 'text-amber-600'
                    : 'text-gray-500'
              }
            `}
          >
            <Calendar size={13} />
            {isInProgress ? 'In Progress' : dayText}
          </span>
          <span className="flex items-center gap-1.5 text-gray-500">
            <Clock size={13} />
            {timeText}
          </span>
          <span className="text-gray-400 text-xs">
            {session.duration_minutes}min
          </span>
        </div>
      </div>

      {/* Session type tag */}
      <div className="hidden sm:block">
        <span
          className={`
            text-xs font-medium px-3 py-1.5 rounded-lg capitalize
            transition-all duration-300
            ${isInProgress
              ? 'bg-green-100 text-green-700'
              : isHovered
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-600'
            }
          `}
        >
          {session.session_type}
        </span>
      </div>

      {/* Join Button - Links to classroom */}
      <div className="flex-shrink-0">
        <Link to={`/classroom/${session.id}`}>
          <Button
            variant={isInProgress ? 'primary' : isToday ? 'primary' : 'secondary'}
            size="sm"
            className={`
              gap-1.5 transition-all duration-300
              ${isInProgress
                ? '!bg-green-600 hover:!bg-green-500 !shadow-green-500/25'
                : ''
              }
              ${isHovered ? 'shadow-lg' : 'shadow-none'}
            `}
          >
            <Video size={14} />
            {isInProgress ? 'Enter' : 'Join'}
          </Button>
        </Link>
      </div>

      {/* Left accent line */}
      <div
        className={`
          absolute left-0 top-1/2 -translate-y-1/2 w-1 rounded-r-full
          transition-all duration-300
          ${isInProgress
            ? 'h-full bg-gradient-to-b from-green-500 to-emerald-500'
            : isToday
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

const UpcomingSessionsList: React.FC<UpcomingSessionsListProps> = ({ sessions }) => {
  // Count in-progress sessions
  const inProgressCount = sessions.filter(s => s.is_in_progress).length;

  if (sessions.length === 0) {
    return (
      <Card className="p-6 h-full">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar size={20} className="text-primary-500" />
          Upcoming Sessions
        </h3>
        <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 text-center border-2 border-dashed border-gray-200/80">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <Calendar size={28} className="text-gray-400" />
          </div>
          <h4 className="font-semibold text-gray-700 mb-1">No upcoming sessions</h4>
          <p className="text-gray-400 text-sm max-w-xs mx-auto">
            Sessions will appear here once students book lessons with you
          </p>
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
          {sessions.length > 0 && (
            <span className="ml-2 text-sm font-medium text-gray-400">
              ({sessions.length})
            </span>
          )}
          {inProgressCount > 0 && (
            <span className="ml-2 flex items-center gap-1 text-xs font-semibold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">
              <Radio size={10} className="animate-pulse" />
              {inProgressCount} Live
            </span>
          )}
        </h3>
        <Link
          to="/sessions"
          className="flex items-center gap-1 text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors group"
        >
          View All
          <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      <div className="space-y-3">
        {sessions.slice(0, 4).map((session, index) => (
          <SessionCard key={session.id} session={session} index={index} />
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

export default UpcomingSessionsList;
