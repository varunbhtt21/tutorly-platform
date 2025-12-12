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

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" />;

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

  // Student dashboard - simple view
  if (!isInstructor) {
    return (
      <div className="container mx-auto px-4 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user.first_name}!
          </h1>
          <p className="text-gray-500 mt-1">
            Here's what's happening with your learning today.
          </p>
        </div>

        <div className="bg-white/70 backdrop-blur-xl border border-white/50 shadow-xl rounded-2xl p-8 text-center">
          <p className="text-gray-500 mb-4">Student dashboard coming soon!</p>
          <Link
            to="/instructors"
            className="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-br from-primary-600 to-blue-600 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-blue-500 transition-all"
          >
            Find a Tutor
          </Link>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-10">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded-lg w-64 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-48 mb-8"></div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded-2xl"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded-2xl"></div>
            <div className="h-64 bg-gray-200 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-10">
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
          <h2 className="text-lg font-semibold text-red-800 mb-2">
            Unable to load dashboard
          </h2>
          <p className="text-red-600 text-sm">
            Please try refreshing the page or contact support.
          </p>
        </div>
      </div>
    );
  }

  // No dashboard data (profile not created yet)
  if (!dashboard) {
    return (
      <div className="container mx-auto px-4 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome, {user.first_name}!
          </h1>
          <p className="text-gray-500 mt-1">
            Complete your profile to start teaching.
          </p>
        </div>

        <div className="bg-white/70 backdrop-blur-xl border border-white/50 shadow-xl rounded-2xl p-8 text-center">
          <p className="text-gray-500 mb-4">
            Your instructor profile hasn't been created yet.
          </p>
          <Link
            to="/dashboard/instructor/onboarding"
            className="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-br from-primary-600 to-blue-600 text-white font-semibold rounded-xl hover:from-primary-500 hover:to-blue-500 transition-all"
          >
            Complete Profile Setup
          </Link>
        </div>
      </div>
    );
  }

  const { profile, user: dashboardUser, stats, upcoming_sessions } = dashboard;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              Welcome back, {dashboardUser.first_name}!
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
          <div className="flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-2">
            <div className="text-sm">
              <span className="font-semibold text-amber-700">
                {stats.profile_completion_percent}%
              </span>
              <span className="text-amber-600"> complete</span>
            </div>
            <div className="w-24 h-2 bg-amber-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full transition-all"
                style={{ width: `${stats.profile_completion_percent}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Stats Row */}
      <div className="mb-8">
        <StatsRow stats={stats} />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Profile Card */}
        <div className="lg:col-span-2 flex">
          <div className="w-full">
            <InstructorProfileCard profile={profile} user={dashboardUser} />
          </div>
        </div>

        {/* Intro Video */}
        <div className="lg:col-span-1">
          <IntroVideoPlayer videoUrl={profile.intro_video_url} />
        </div>
      </div>

      {/* Secondary Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upcoming Sessions - Takes 2 columns */}
        <div className="lg:col-span-2">
          <UpcomingSessionsList sessions={upcoming_sessions} />
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* About Section */}
          <AboutSection
            bio={profile.bio}
            teachingExperience={profile.teaching_experience}
          />

          {/* Quick Actions */}
          <QuickActions />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
