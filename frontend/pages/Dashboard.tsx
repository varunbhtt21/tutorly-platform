/**
 * Dashboard Page
 * Modern design with micro-animations, glassmorphism, and Figma-style elements
 */

import { Link, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { instructorAPI } from '../services';
import { Badge } from '../components/UIComponents';
import {
  InstructorProfileCard,
  IntroVideoPlayer,
  StatsRow,
  UpcomingSessionsList,
  AboutSection,
  QuickActions,
} from '../components/dashboard';
import { Sparkles, BookOpen, ArrowRight, TrendingUp } from 'lucide-react';

// Animated background blob component
const AnimatedBlob: React.FC<{ className?: string; delay?: number }> = ({ className = '', delay = 0 }) => (
  <div
    className={`absolute rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob ${className}`}
    style={{ animationDelay: `${delay}s` }}
  />
);

// Welcome greeting based on time of day
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
};

// Skeleton loader for dashboard
const DashboardSkeleton = () => (
  <div className="container mx-auto px-4 py-10">
    {/* Animated gradient overlay */}
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200/30 rounded-full blur-3xl animate-pulse" />
      <div className="absolute top-1/3 -left-40 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl animate-pulse delay-1000" />
    </div>

    <div className="relative">
      {/* Header skeleton */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <div className="h-9 bg-gradient-to-r from-gray-200 to-gray-100 rounded-xl w-72 mb-3 animate-shimmer" />
          <div className="h-5 bg-gray-200/80 rounded-lg w-56 animate-shimmer delay-100" />
        </div>
        <div className="h-10 bg-gray-200/80 rounded-xl w-40 animate-shimmer delay-200" />
      </div>

      {/* Stats skeleton */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="h-28 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg animate-shimmer"
            style={{ animationDelay: `${i * 0.1}s` }}
          />
        ))}
      </div>

      {/* Content skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 h-64 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg animate-shimmer" />
        <div className="h-64 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg animate-shimmer delay-200" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-72 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg animate-shimmer" />
        <div className="space-y-6">
          <div className="h-48 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg animate-shimmer delay-100" />
          <div className="h-56 bg-white/60 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg animate-shimmer delay-200" />
        </div>
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" />;

  // Admin users should use the Admin Dashboard - redirect them there
  if (user.role === 'admin') {
    return <Navigate to="/admin" replace />;
  }

  const isInstructor = user.role === 'instructor';

  // Fetch instructor dashboard data
  const {
    data: dashboard,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['instructorDashboard'],
    queryFn: () => instructorAPI.getDashboard(),
    enabled: isInstructor,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });

  // Redirect instructors to onboarding if profile is not complete
  if (isInstructor && dashboard && !dashboard.profile.is_onboarding_complete) {
    return <Navigate to="/dashboard/instructor/onboarding" replace />;
  }

  // Student dashboard - modern design
  if (!isInstructor) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <AnimatedBlob className="w-72 h-72 bg-primary-200/40 -top-20 -right-20" delay={0} />
          <AnimatedBlob className="w-96 h-96 bg-blue-200/30 top-1/2 -left-48" delay={2} />
          <AnimatedBlob className="w-64 h-64 bg-purple-200/30 bottom-20 right-1/4" delay={4} />
        </div>

        <div className="container mx-auto px-4 py-10 relative">
          {/* Welcome header with animation */}
          <div className="mb-10 animate-fadeInUp">
            <div className="flex items-center gap-2 text-primary-600 font-medium mb-2">
              <Sparkles size={18} className="animate-pulse" />
              <span>{getGreeting()}</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Welcome back, <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">{user.first_name}!</span>
            </h1>
            <p className="text-gray-500 text-lg">
              Here's what's happening with your learning today.
            </p>
          </div>

          {/* Student CTA card */}
          <div
            className="bg-white/70 backdrop-blur-xl border border-white/50 shadow-2xl shadow-primary-500/10 rounded-3xl p-10 text-center max-w-2xl mx-auto animate-fadeInUp"
            style={{ animationDelay: '0.2s' }}
          >
            <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <BookOpen size={36} className="text-primary-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Student Dashboard Coming Soon
            </h2>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">
              We're building an amazing learning experience for you. In the meantime, find your perfect tutor!
            </p>
            <Link
              to="/instructors"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-primary-600 to-blue-600 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-blue-500 transition-all shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:scale-[1.02] active:scale-[0.98] group"
            >
              Find a Tutor
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </Link>
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
          @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
          .animate-shimmer {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s ease-in-out infinite;
          }
        `}</style>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
        <DashboardSkeleton />
        <style>{`
          @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
          }
          .animate-shimmer {
            background: linear-gradient(90deg, rgba(255,255,255,0.4) 25%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0.4) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s ease-in-out infinite;
          }
        `}</style>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50/30 relative overflow-hidden">
        <div className="container mx-auto px-4 py-10">
          <div className="bg-white/70 backdrop-blur-xl border border-red-200/50 shadow-xl rounded-3xl p-10 text-center max-w-lg mx-auto animate-fadeInUp">
            <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Unable to load dashboard
            </h2>
            <p className="text-gray-500 mb-6">
              Please try refreshing the page or contact support.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-red-500 text-white font-semibold rounded-xl hover:bg-red-600 transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
        <style>{`
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fadeInUp { animation: fadeInUp 0.6s ease-out forwards; }
        `}</style>
      </div>
    );
  }

  // No dashboard data (profile not created yet)
  if (!dashboard) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <AnimatedBlob className="w-72 h-72 bg-primary-200/40 -top-20 -right-20" delay={0} />
          <AnimatedBlob className="w-96 h-96 bg-blue-200/30 top-1/2 -left-48" delay={2} />
        </div>

        <div className="container mx-auto px-4 py-10 relative">
          <div className="mb-10 animate-fadeInUp">
            <div className="flex items-center gap-2 text-primary-600 font-medium mb-2">
              <Sparkles size={18} className="animate-pulse" />
              <span>Let's get started</span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Welcome, <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">{user.first_name}!</span>
            </h1>
            <p className="text-gray-500 text-lg">
              Complete your profile to start teaching.
            </p>
          </div>

          <div
            className="bg-white/70 backdrop-blur-xl border border-white/50 shadow-2xl shadow-primary-500/10 rounded-3xl p-10 text-center max-w-2xl mx-auto animate-fadeInUp"
            style={{ animationDelay: '0.2s' }}
          >
            <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <TrendingUp size={36} className="text-primary-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Complete Your Profile
            </h2>
            <p className="text-gray-500 mb-8 max-w-md mx-auto">
              Your instructor profile hasn't been created yet. Set up your profile to start accepting students.
            </p>
            <Link
              to="/dashboard/instructor/onboarding"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-primary-600 to-blue-600 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-blue-500 transition-all shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:scale-[1.02] active:scale-[0.98] group"
            >
              Complete Profile Setup
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>

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
        `}</style>
      </div>
    );
  }

  const { profile, user: dashboardUser, stats, upcoming_sessions } = dashboard;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50/30 relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <AnimatedBlob className="w-72 h-72 bg-primary-200/30 -top-20 -right-20" delay={0} />
        <AnimatedBlob className="w-96 h-96 bg-blue-200/20 top-1/3 -left-48" delay={2} />
        <AnimatedBlob className="w-64 h-64 bg-purple-200/20 bottom-20 right-1/4" delay={4} />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 animate-fadeInUp">
          <div>
            <div className="flex items-center gap-2 text-primary-600 font-medium mb-1">
              <Sparkles size={16} className="animate-pulse" />
              <span className="text-sm">{getGreeting()}</span>
            </div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Welcome back, <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">{dashboardUser.first_name}!</span>
              </h1>
              <Badge
                variant={profile.status === 'verified' ? 'primary' : 'secondary'}
              >
                {profile.status === 'verified' ? 'Verified' : 'Pending'}
              </Badge>
            </div>
            <p className="text-gray-500 mt-1 text-sm sm:text-base">
              Here's an overview of your instructor profile and activity.
            </p>
          </div>

          {/* Profile Completion */}
          {stats.profile_completion_percent < 100 && (
            <div
              className="flex items-center gap-3 bg-amber-50/80 backdrop-blur-sm border border-amber-200/50 rounded-xl px-4 py-3 shadow-sm hover:shadow-md transition-all animate-fadeInUp"
              style={{ animationDelay: '0.1s' }}
            >
              <div className="text-sm">
                <span className="font-bold text-amber-700">
                  {stats.profile_completion_percent}%
                </span>
                <span className="text-amber-600"> complete</span>
              </div>
              <div className="w-24 h-2.5 bg-amber-200/50 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-amber-400 to-amber-500 rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${stats.profile_completion_percent}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Stats Row */}
        <div className="mb-8 animate-fadeInUp" style={{ animationDelay: '0.15s' }}>
          <StatsRow stats={stats} />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Profile Card */}
          <div className="lg:col-span-2 animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <InstructorProfileCard profile={profile} user={dashboardUser} />
          </div>

          {/* Intro Video */}
          <div className="lg:col-span-1 animate-fadeInUp" style={{ animationDelay: '0.25s' }}>
            <IntroVideoPlayer videoUrl={profile.intro_video_url} />
          </div>
        </div>

        {/* Secondary Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upcoming Sessions - Takes 2 columns */}
          <div className="lg:col-span-2 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <UpcomingSessionsList sessions={upcoming_sessions} />
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* About Section */}
            <div className="animate-fadeInUp" style={{ animationDelay: '0.35s' }}>
              <AboutSection
                bio={profile.bio}
                teachingExperience={profile.teaching_experience}
              />
            </div>

            {/* Quick Actions */}
            <div className="animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
              <QuickActions />
            </div>
          </div>
        </div>
      </div>

      {/* Global CSS animations */}
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
      `}</style>
    </div>
  );
};

export default Dashboard;
