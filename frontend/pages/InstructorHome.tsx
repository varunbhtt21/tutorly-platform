/**
 * Instructor Home Page
 * Modern dashboard home with next session, upcoming sessions, and micro-animations
 */

import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { instructorAPI } from '../services';
import { Card, Button } from '../components/UIComponents';
import {
  Video,
  Clock,
  Calendar,
  ChevronRight,
  MessageCircle,
  MoreHorizontal,
  Sparkles,
  User,
  Timer,
} from 'lucide-react';
import type { UpcomingSession } from '../types/api';

// Animated background blob
const AnimatedBlob: React.FC<{ className?: string; delay?: number }> = ({ className = '', delay = 0 }) => (
  <div
    className={`absolute rounded-full mix-blend-multiply filter blur-xl opacity-60 animate-blob ${className}`}
    style={{ animationDelay: `${delay}s` }}
  />
);

// Welcome greeting based on time
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
};

// Format time remaining until session
const getTimeRemaining = (dateString: string): { text: string; isNow: boolean; isSoon: boolean } => {
  const sessionDate = new Date(dateString);
  const now = new Date();
  const diffMs = sessionDate.getTime() - now.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins <= 0) {
    return { text: 'Now', isNow: true, isSoon: false };
  } else if (diffMins < 60) {
    return { text: `In ${diffMins} minute${diffMins !== 1 ? 's' : ''}`, isNow: false, isSoon: diffMins <= 30 };
  } else if (diffHours < 24) {
    return { text: `In ${diffHours} hour${diffHours !== 1 ? 's' : ''}`, isNow: false, isSoon: diffHours <= 1 };
  } else {
    return { text: `In ${diffDays} day${diffDays !== 1 ? 's' : ''}`, isNow: false, isSoon: false };
  }
};

// Format session time
const formatSessionTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

// Format session end time
const formatEndTime = (dateString: string, durationMinutes: number) => {
  const date = new Date(dateString);
  date.setMinutes(date.getMinutes() + durationMinutes);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

// Next Session Card - Large featured card
interface NextSessionCardProps {
  session: UpcomingSession;
}

const NextSessionCard: React.FC<NextSessionCardProps> = ({ session }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [, setTick] = useState(0);

  // Update time every minute to refresh countdown
  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 60000);
    return () => clearInterval(interval);
  }, []);

  const timeRemaining = getTimeRemaining(session.start_at);

  return (
    <Card
      className={`
        relative overflow-hidden p-0
        transition-all duration-500
        ${isHovered ? 'shadow-2xl shadow-primary-500/20 scale-[1.01]' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50/80 via-white to-blue-50/80" />

      {/* Animated decorative elements */}
      <div
        className={`
          absolute -top-20 -right-20 w-64 h-64 rounded-full
          bg-gradient-to-br from-primary-200/40 to-blue-200/40
          blur-3xl transition-all duration-700
          ${isHovered ? 'scale-125 opacity-100' : 'scale-100 opacity-60'}
        `}
      />
      <div
        className={`
          absolute -bottom-10 -left-10 w-40 h-40 rounded-full
          bg-gradient-to-br from-purple-200/30 to-pink-200/30
          blur-2xl transition-all duration-700
          ${isHovered ? 'scale-110 opacity-80' : 'scale-100 opacity-40'}
        `}
      />

      <div className="relative p-6 lg:p-8">
        {/* Header with avatar and actions */}
        <div className="flex items-start justify-between mb-6">
          {/* Student info */}
          <div className="flex items-center gap-4">
            <div
              className={`
                relative w-14 h-14 rounded-2xl overflow-hidden
                bg-gradient-to-br from-primary-500 to-blue-500
                flex items-center justify-center
                shadow-lg shadow-primary-500/30
                transition-all duration-300
                ${isHovered ? 'scale-110 rotate-3' : ''}
              `}
            >
              <span className="text-white font-bold text-xl">
                {session.student_name.charAt(0)}
              </span>
              {/* Online indicator */}
              <span className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-green-500 border-2 border-white rounded-full" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {session.student_name}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm font-medium text-gray-500 capitalize">
                  {session.session_type} lesson
                </span>
                {session.is_trial && (
                  <span className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-semibold rounded-full">
                    Trial Lesson
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Actions menu */}
          <button className="p-2 hover:bg-white/50 rounded-xl transition-colors">
            <MoreHorizontal size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Time display */}
        <div className="flex flex-col lg:flex-row lg:items-center gap-6 mb-8">
          {/* Time card */}
          <div className="flex-grow">
            <div className="flex items-baseline gap-2">
              <span className="text-5xl lg:text-6xl font-extrabold text-gray-900 tabular-nums">
                {formatSessionTime(session.start_at).split(' ')[0]}
              </span>
              <span className="text-2xl font-medium text-gray-400">
                {formatSessionTime(session.start_at).split(' ')[1]}
              </span>
              <span className="text-2xl text-gray-300 mx-2">–</span>
              <span className="text-2xl font-medium text-gray-500">
                {formatEndTime(session.start_at, session.duration_minutes)}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-3">
              <Timer size={16} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-500">
                {session.duration_minutes} minutes
              </span>
            </div>
          </div>

          {/* Countdown badge */}
          <div
            className={`
              px-5 py-3 rounded-2xl
              flex items-center gap-3
              transition-all duration-300
              ${timeRemaining.isNow
                ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg shadow-green-500/30'
                : timeRemaining.isSoon
                  ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/30'
                  : 'bg-white/80 border border-gray-200/50 text-gray-700'
              }
            `}
          >
            {timeRemaining.isNow ? (
              <span className="flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-white opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
              </span>
            ) : (
              <Clock size={18} />
            )}
            <span className="font-bold text-lg">{timeRemaining.text}</span>
          </div>
        </div>

        {/* Decorative illustration */}
        <div
          className={`
            absolute right-8 bottom-8 w-32 h-32 lg:w-40 lg:h-40
            transition-all duration-500
            ${isHovered ? 'scale-110 rotate-6' : 'scale-100 rotate-0'}
          `}
        >
          {/* Simple illustration - clock/calendar visual */}
          <div className="relative w-full h-full">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-100 to-blue-100 rounded-3xl rotate-6" />
            <div className="absolute inset-2 bg-white rounded-2xl shadow-inner flex items-center justify-center">
              <div className="text-center">
                <Calendar size={36} className="text-primary-400 mx-auto mb-1" />
                <div className="text-xs font-bold text-gray-400">
                  {new Date(session.start_at).toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3 mt-4 relative z-10">
          <Button
            size="lg"
            className={`
              gap-2 px-8 shadow-lg shadow-primary-500/25
              transition-all duration-300
              ${isHovered ? 'shadow-xl shadow-primary-500/30 scale-[1.02]' : ''}
            `}
          >
            <Video size={20} />
            Enter Classroom
          </Button>
          <Button variant="outline" size="lg" className="gap-2">
            <MessageCircle size={18} />
            Message
          </Button>
        </div>
      </div>
    </Card>
  );
};

// Up Next Session Item
interface UpNextItemProps {
  session: UpcomingSession;
  index: number;
}

const UpNextItem: React.FC<UpNextItemProps> = ({ session, index }) => {
  const [isHovered, setIsHovered] = useState(false);

  const formatRelativeDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'tomorrow';
    } else {
      return `in ${Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))} days`;
    }
  };

  return (
    <div
      className={`
        relative flex items-center gap-4 p-4 rounded-2xl
        bg-white/60 backdrop-blur-sm border border-white/50
        transition-all duration-300 ease-out
        hover:bg-white/80 hover:shadow-lg hover:shadow-gray-200/50
        ${isHovered ? 'scale-[1.01]' : 'scale-100'}
      `}
      style={{
        animation: `slideInUp 0.4s ease-out forwards`,
        animationDelay: `${index * 0.1}s`,
        opacity: 0,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Avatar */}
      <div
        className={`
          w-12 h-12 rounded-xl overflow-hidden
          bg-gradient-to-br from-gray-200 to-gray-300
          flex items-center justify-center
          transition-all duration-300
          ${isHovered ? 'scale-105' : ''}
        `}
      >
        <span className="text-gray-600 font-bold">
          {session.student_name.charAt(0)}
        </span>
      </div>

      {/* Info */}
      <div className="flex-grow min-w-0">
        <h4 className="font-semibold text-gray-900 truncate">
          {session.student_name}
        </h4>
        <p className="text-sm text-gray-500">
          {formatRelativeDate(session.start_at)}, {formatSessionTime(session.start_at)} – {formatEndTime(session.start_at, session.duration_minutes)}
        </p>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <button
          className={`
            p-2 rounded-lg transition-all duration-300
            ${isHovered ? 'bg-primary-100 text-primary-600' : 'text-gray-400 hover:text-gray-600'}
          `}
        >
          <Video size={18} />
        </button>
        <button
          className={`
            p-2 rounded-lg transition-all duration-300
            ${isHovered ? 'bg-gray-100 text-gray-600' : 'text-gray-400 hover:text-gray-600'}
          `}
        >
          <MessageCircle size={18} />
        </button>
      </div>

      {/* Left accent */}
      <div
        className={`
          absolute left-0 top-1/2 -translate-y-1/2 w-1 rounded-r-full
          bg-gradient-to-b from-primary-400 to-blue-400
          transition-all duration-300
          ${isHovered ? 'h-3/4' : 'h-1/3'}
        `}
      />
    </div>
  );
};

// Empty state when no sessions
const EmptySessionState: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card
      className={`
        p-8 lg:p-12 text-center relative overflow-hidden
        transition-all duration-300
        ${isHovered ? 'shadow-xl shadow-gray-200/50' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 to-white" />
      <div
        className={`
          absolute -top-20 -right-20 w-48 h-48 rounded-full
          bg-gradient-to-br from-primary-100/50 to-blue-100/50
          blur-2xl transition-all duration-500
          ${isHovered ? 'scale-125 opacity-100' : 'scale-100 opacity-60'}
        `}
      />

      <div className="relative">
        <div
          className={`
            w-20 h-20 mx-auto mb-6 rounded-3xl
            bg-gradient-to-br from-gray-100 to-gray-50
            flex items-center justify-center
            shadow-inner transition-all duration-300
            ${isHovered ? 'scale-110 rotate-3' : ''}
          `}
        >
          <Calendar size={36} className="text-gray-400" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          No upcoming sessions
        </h3>
        <p className="text-gray-500 mb-6 max-w-md mx-auto">
          Your schedule is clear for now. Sessions will appear here once students book lessons with you.
        </p>
        <Link to="/calendar">
          <Button variant="outline" className="gap-2">
            <Calendar size={18} />
            Manage Availability
          </Button>
        </Link>
      </div>
    </Card>
  );
};

// Quick stats row
interface QuickStatsProps {
  todaySessions: number;
  weekSessions: number;
  totalStudents: number;
}

const QuickStats: React.FC<QuickStatsProps> = ({ todaySessions, weekSessions, totalStudents }) => {
  return (
    <div className="grid grid-cols-3 gap-4">
      {[
        { label: 'Today', value: todaySessions, icon: <Clock size={16} />, color: 'primary' },
        { label: 'This Week', value: weekSessions, icon: <Calendar size={16} />, color: 'blue' },
        { label: 'Students', value: totalStudents, icon: <User size={16} />, color: 'purple' },
      ].map((stat, idx) => (
        <div
          key={stat.label}
          className="bg-white/60 backdrop-blur-sm border border-white/50 rounded-2xl p-4 text-center hover:shadow-lg hover:bg-white/80 transition-all duration-300"
          style={{
            animation: `fadeInUp 0.4s ease-out forwards`,
            animationDelay: `${idx * 0.1}s`,
            opacity: 0,
          }}
        >
          <div className={`text-2xl font-bold text-gray-900`}>{stat.value}</div>
          <div className="text-xs font-medium text-gray-500 flex items-center justify-center gap-1.5 mt-1">
            {stat.icon}
            {stat.label}
          </div>
        </div>
      ))}
    </div>
  );
};

// Main component
const InstructorHome: React.FC = () => {
  const { user, loading: authLoading } = useAuth();

  // Fetch dashboard data
  const {
    data: dashboard,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['instructorDashboard'],
    queryFn: () => instructorAPI.getDashboard(),
    enabled: !!user && user.role === 'instructor',
    staleTime: 1000 * 60 * 2, // Cache for 2 minutes
    refetchInterval: 1000 * 60, // Refetch every minute
  });

  // Redirect if not instructor
  if (!authLoading && (!user || user.role !== 'instructor')) {
    return <Navigate to="/dashboard" replace />;
  }

  // Loading state
  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <AnimatedBlob className="w-72 h-72 bg-primary-200/30 -top-20 -right-20" delay={0} />
          <AnimatedBlob className="w-96 h-96 bg-blue-200/20 top-1/3 -left-48" delay={2} />
        </div>
        <div className="container mx-auto px-4 py-8 relative">
          <div className="max-w-4xl mx-auto">
            {/* Skeleton */}
            <div className="h-8 bg-gray-200/80 rounded-xl w-64 mb-2 animate-pulse" />
            <div className="h-5 bg-gray-200/60 rounded-lg w-48 mb-8 animate-pulse" />
            <div className="h-72 bg-white/60 rounded-3xl border border-white/50 animate-pulse mb-6" />
            <div className="h-10 bg-gray-200/60 rounded-xl w-32 mb-4 animate-pulse" />
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-white/60 rounded-2xl border border-white/50 animate-pulse" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50/30 flex items-center justify-center">
        <Card className="p-8 text-center max-w-md">
          <h2 className="text-xl font-bold text-gray-900 mb-2">Unable to load</h2>
          <p className="text-gray-500 mb-4">Please try refreshing the page.</p>
          <Button onClick={() => window.location.reload()}>Refresh</Button>
        </Card>
      </div>
    );
  }

  const upcomingSessions = dashboard?.upcoming_sessions || [];
  const nextSession = upcomingSessions[0];
  const upNextSessions = upcomingSessions.slice(1, 5);
  const stats = dashboard?.stats;

  // Count today's sessions
  const today = new Date().toDateString();
  const todaySessions = upcomingSessions.filter(
    (s) => new Date(s.start_at).toDateString() === today
  ).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <AnimatedBlob className="w-72 h-72 bg-primary-200/30 -top-20 -right-20" delay={0} />
        <AnimatedBlob className="w-96 h-96 bg-blue-200/20 top-1/3 -left-48" delay={2} />
        <AnimatedBlob className="w-64 h-64 bg-purple-200/20 bottom-20 right-1/4" delay={4} />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8 animate-fadeInUp">
            <div className="flex items-center gap-2 text-primary-600 font-medium mb-1">
              <Sparkles size={16} className="animate-pulse" />
              <span className="text-sm">{getGreeting()}</span>
            </div>
            <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">
              {getGreeting()},{' '}
              <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                {dashboard?.user?.first_name || user?.first_name}
              </span>
            </h1>
            <p className="text-gray-500 mt-1">
              {upcomingSessions.length > 0
                ? `You have ${todaySessions} session${todaySessions !== 1 ? 's' : ''} today`
                : 'Ready to inspire your next student?'}
            </p>
          </div>

          {/* Quick Stats */}
          {stats && (
            <div className="mb-8">
              <QuickStats
                todaySessions={todaySessions}
                weekSessions={stats.upcoming_sessions_count}
                totalStudents={stats.total_students}
              />
            </div>
          )}

          {/* Next Session */}
          <div className="mb-8">
            {nextSession ? (
              <NextSessionCard session={nextSession} />
            ) : (
              <EmptySessionState />
            )}
          </div>

          {/* Up Next Section */}
          {upNextSessions.length > 0 && (
            <div className="animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <Clock size={20} className="text-primary-500" />
                  Up next
                </h2>
                <Link
                  to="/calendar"
                  className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1 transition-colors group"
                >
                  See all
                  <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
              <div className="space-y-3">
                {upNextSessions.map((session, index) => (
                  <UpNextItem key={session.id} session={session} index={index} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -30px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(30px, 10px) scale(1.05); }
        }
        .animate-blob { animation: blob 8s ease-in-out infinite; }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeInUp { animation: fadeInUp 0.6s ease-out forwards; }
        @keyframes slideInUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default InstructorHome;
