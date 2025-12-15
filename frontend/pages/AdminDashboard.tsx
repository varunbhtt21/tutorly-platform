/**
 * Admin Dashboard - Clean & Performant
 * Focus: Data visibility, quick actions, zero bloat
 */

import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import { adminAPI, type PendingInstructor, type AdminUser } from '../services/adminAPI';
import { Card, Button } from '../components/UIComponents';
import {
  Shield,
  Users,
  UserCheck,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Ban,
  Play,
  Eye,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  GraduationCap,
  Search,
  Mail,
  Calendar,
  MapPin,
  ExternalLink,
} from 'lucide-react';

// Stat Card
const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}> = ({ title, value, icon, color }) => (
  <Card className="p-5">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">{value.toLocaleString()}</p>
      </div>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        {icon}
      </div>
    </div>
  </Card>
);

// Mini Stat
const MiniStat: React.FC<{
  label: string;
  value: number;
  color: string;
}> = ({ label, value, color }) => (
  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
    <span className="text-sm text-gray-600">{label}</span>
    <span className={`text-sm font-semibold ${color}`}>{value}</span>
  </div>
);

// Tab Button
const TabButton: React.FC<{
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  badge?: number;
}> = ({ active, onClick, children, badge }) => (
  <button
    onClick={onClick}
    className={`
      px-4 py-2.5 text-sm font-medium rounded-lg transition-colors
      ${active
        ? 'bg-primary-600 text-white'
        : 'text-gray-600 hover:bg-gray-100'
      }
    `}
  >
    <span className="flex items-center gap-2">
      {children}
      {badge !== undefined && badge > 0 && (
        <span className={`px-2 py-0.5 text-xs rounded-full ${active ? 'bg-white/20' : 'bg-red-500 text-white'}`}>
          {badge}
        </span>
      )}
    </span>
  </button>
);

// Instructor Review Card
const InstructorCard: React.FC<{
  instructor: PendingInstructor;
  onVerify: () => void;
  onReject: (reason: string) => void;
  isLoading: boolean;
}> = ({ instructor, onVerify, onReject, isLoading }) => {
  const [expanded, setExpanded] = useState(false);
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const handleReject = () => {
    if (rejectReason.trim().length < 10) {
      toast.error('Please provide a detailed reason (min 10 characters)');
      return;
    }
    onReject(rejectReason);
    setShowRejectForm(false);
    setRejectReason('');
  };

  const completionPercent = instructor.profile.is_onboarding_complete
    ? 100
    : ((instructor.profile.onboarding_step || 1) / 7) * 100;

  return (
    <Card className="p-5">
      <div className="flex items-start gap-4">
        {/* Avatar */}
        {instructor.profile.profile_photo_url ? (
          <img
            src={instructor.profile.profile_photo_url}
            alt={`${instructor.user.first_name} ${instructor.user.last_name}`}
            className="w-14 h-14 rounded-xl object-cover"
          />
        ) : (
          <div className="w-14 h-14 rounded-xl bg-amber-100 flex items-center justify-center">
            <span className="text-lg font-bold text-amber-700">
              {instructor.user.first_name[0]}{instructor.user.last_name[0]}
            </span>
          </div>
        )}

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-gray-900">
              {instructor.user.first_name} {instructor.user.last_name}
            </h3>
            <span className="px-2 py-0.5 text-xs font-medium bg-amber-100 text-amber-700 rounded-full">
              Pending
            </span>
          </div>

          <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Mail size={14} />
              {instructor.user.email}
            </span>
            {instructor.profile.country_of_birth && (
              <span className="flex items-center gap-1">
                <MapPin size={14} />
                {instructor.profile.country_of_birth}
              </span>
            )}
          </div>

          {instructor.profile.headline && (
            <p className="text-sm text-gray-600 mt-2 line-clamp-1">
              {instructor.profile.headline}
            </p>
          )}

          {/* Progress */}
          <div className="flex items-center gap-3 mt-3">
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full"
                style={{ width: `${completionPercent}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">{Math.round(completionPercent)}%</span>
          </div>
        </div>

        {/* Expand */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
          {instructor.profile.bio && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs font-medium text-gray-500 mb-1">Bio</p>
              <p className="text-sm text-gray-700">{instructor.profile.bio}</p>
            </div>
          )}

          {instructor.profile.intro_video_url && (
            <a
              href={instructor.profile.intro_video_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Play size={18} />
              <span className="text-sm font-medium">Watch Introduction Video</span>
              <ExternalLink size={14} className="ml-auto" />
            </a>
          )}

          <p className="text-xs text-gray-400 flex items-center gap-1">
            <Calendar size={12} />
            Submitted {instructor.profile.created_at
              ? new Date(instructor.profile.created_at).toLocaleDateString()
              : 'Unknown'}
          </p>
        </div>
      )}

      {/* Actions */}
      {showRejectForm ? (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
          <textarea
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Enter rejection reason (min 10 characters)..."
            className="w-full p-3 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={2}
          />
          <div className="flex gap-2">
            <Button
              onClick={handleReject}
              disabled={isLoading}
              className="!bg-red-600 hover:!bg-red-700"
            >
              Confirm Reject
            </Button>
            <Button
              variant="ghost"
              onClick={() => { setShowRejectForm(false); setRejectReason(''); }}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
          <Button onClick={onVerify} disabled={isLoading} size="sm">
            <CheckCircle size={16} /> Approve
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowRejectForm(true)}
            className="text-red-600 hover:bg-red-50"
          >
            <XCircle size={16} /> Reject
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setExpanded(!expanded)}>
            <Eye size={16} /> {expanded ? 'Less' : 'Details'}
          </Button>
        </div>
      )}
    </Card>
  );
};

// User Row
const UserRow: React.FC<{
  user: AdminUser;
  onSuspend: (reason: string) => void;
  onBan: (reason: string) => void;
  onActivate: () => void;
  isLoading: boolean;
}> = ({ user, onSuspend, onBan, onActivate, isLoading }) => {
  const [showActions, setShowActions] = useState(false);
  const [actionType, setActionType] = useState<'suspend' | 'ban' | null>(null);
  const [reason, setReason] = useState('');

  const handleAction = () => {
    if (reason.trim().length < 10) {
      toast.error('Please provide a detailed reason');
      return;
    }
    if (actionType === 'suspend') onSuspend(reason);
    else if (actionType === 'ban') onBan(reason);
    setActionType(null);
    setReason('');
    setShowActions(false);
  };

  const statusColors: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    suspended: 'bg-amber-100 text-amber-700',
    banned: 'bg-red-100 text-red-700',
    inactive: 'bg-gray-100 text-gray-600',
  };

  const roleColors: Record<string, string> = {
    admin: 'bg-purple-100 text-purple-700',
    instructor: 'bg-blue-100 text-blue-700',
    student: 'bg-gray-100 text-gray-600',
  };

  return (
    <div className="p-4 border-b border-gray-100 last:border-0 hover:bg-gray-50/50 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center font-medium text-gray-600">
            {user.first_name[0]}{user.last_name[0]}
          </div>
          <div>
            <p className="font-medium text-gray-900">{user.first_name} {user.last_name}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${roleColors[user.role] || roleColors.student}`}>
            {user.role}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[user.status] || statusColors.inactive}`}>
            {user.status}
          </span>
          {user.role !== 'admin' && (
            <button
              onClick={() => setShowActions(!showActions)}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {showActions ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          )}
        </div>
      </div>

      {showActions && user.role !== 'admin' && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          {actionType ? (
            <div className="space-y-2">
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder={`Enter ${actionType} reason...`}
                className="w-full p-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={2}
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleAction}
                  disabled={isLoading}
                  className={actionType === 'ban' ? '!bg-red-600' : ''}
                >
                  Confirm
                </Button>
                <Button size="sm" variant="ghost" onClick={() => { setActionType(null); setReason(''); }}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex gap-2">
              {user.status === 'active' && (
                <>
                  <Button size="sm" variant="ghost" onClick={() => setActionType('suspend')} className="text-amber-600">
                    <AlertTriangle size={14} /> Suspend
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setActionType('ban')} className="text-red-600">
                    <Ban size={14} /> Ban
                  </Button>
                </>
              )}
              {(user.status === 'suspended' || user.status === 'inactive') && (
                <Button size="sm" onClick={onActivate} disabled={isLoading}>
                  <CheckCircle size={14} /> Activate
                </Button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Main Component
const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'overview' | 'instructors' | 'users'>('overview');
  const [userRoleFilter, setUserRoleFilter] = useState('');
  const [userStatusFilter, setUserStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  if (!user || user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  // Queries
  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ['adminDashboardStats'],
    queryFn: () => adminAPI.getDashboardStats(),
  });

  const { data: pendingInstructors = [], isLoading: instructorsLoading, refetch: refetchInstructors } = useQuery({
    queryKey: ['adminPendingInstructors'],
    queryFn: () => adminAPI.getPendingInstructors(),
  });

  const { data: users = [], isLoading: usersLoading, refetch: refetchUsers } = useQuery({
    queryKey: ['adminUsers', userRoleFilter, userStatusFilter],
    queryFn: () => adminAPI.getAllUsers(userRoleFilter || undefined, userStatusFilter || undefined),
  });

  const filteredUsers = users.filter((u) =>
    searchQuery === '' ||
    u.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Mutations
  const verifyMutation = useMutation({
    mutationFn: (instructorId: number) => adminAPI.verifyInstructor(instructorId),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminPendingInstructors'] });
      queryClient.invalidateQueries({ queryKey: ['adminDashboardStats'] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to verify'),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ instructorId, reason }: { instructorId: number; reason: string }) =>
      adminAPI.rejectInstructor(instructorId, reason),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminPendingInstructors'] });
      queryClient.invalidateQueries({ queryKey: ['adminDashboardStats'] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to reject'),
  });

  const suspendMutation = useMutation({
    mutationFn: ({ userId, reason }: { userId: number; reason: string }) =>
      adminAPI.suspendUser(userId, reason),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      queryClient.invalidateQueries({ queryKey: ['adminDashboardStats'] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to suspend'),
  });

  const banMutation = useMutation({
    mutationFn: ({ userId, reason }: { userId: number; reason: string }) =>
      adminAPI.banUser(userId, reason),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      queryClient.invalidateQueries({ queryKey: ['adminDashboardStats'] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to ban'),
  });

  const activateMutation = useMutation({
    mutationFn: (userId: number) => adminAPI.activateUser(userId),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      queryClient.invalidateQueries({ queryKey: ['adminDashboardStats'] });
    },
    onError: (error: any) => toast.error(error.response?.data?.detail || 'Failed to activate'),
  });

  const handleRefresh = () => {
    refetchStats();
    refetchInstructors();
    refetchUsers();
    toast.success('Dashboard refreshed');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
              <Shield size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-500">Welcome, {user.first_name}</p>
            </div>
          </div>
          <Button variant="secondary" size="sm" onClick={handleRefresh}>
            <RefreshCw size={16} /> Refresh
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 p-1 bg-white rounded-xl border border-gray-200">
          <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>
            Overview
          </TabButton>
          <TabButton
            active={activeTab === 'instructors'}
            onClick={() => setActiveTab('instructors')}
            badge={stats?.pending_instructors}
          >
            <Clock size={16} /> Pending Reviews
          </TabButton>
          <TabButton active={activeTab === 'users'} onClick={() => setActiveTab('users')}>
            <Users size={16} /> Users
          </TabButton>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Main Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Users"
                value={stats?.total_users || 0}
                icon={<Users size={24} className="text-white" />}
                color="bg-blue-500"
              />
              <StatCard
                title="Students"
                value={stats?.total_students || 0}
                icon={<GraduationCap size={24} className="text-white" />}
                color="bg-emerald-500"
              />
              <StatCard
                title="Instructors"
                value={stats?.total_instructors || 0}
                icon={<UserCheck size={24} className="text-white" />}
                color="bg-purple-500"
              />
              <StatCard
                title="Admins"
                value={stats?.total_admins || 0}
                icon={<Shield size={24} className="text-white" />}
                color="bg-amber-500"
              />
            </div>

            {/* Secondary Stats */}
            <div className="grid lg:grid-cols-2 gap-4">
              <Card className="p-5">
                <h3 className="font-semibold text-gray-900 mb-4">Instructor Status</h3>
                <div className="space-y-2">
                  <MiniStat label="Pending Review" value={stats?.pending_instructors || 0} color="text-amber-600" />
                  <MiniStat label="Verified" value={stats?.verified_instructors || 0} color="text-green-600" />
                  <MiniStat label="Rejected" value={stats?.rejected_instructors || 0} color="text-red-600" />
                  <MiniStat label="Suspended" value={stats?.suspended_instructors || 0} color="text-gray-600" />
                </div>
              </Card>

              <Card className="p-5">
                <h3 className="font-semibold text-gray-900 mb-4">User Status</h3>
                <div className="space-y-2">
                  <MiniStat label="Active" value={stats?.active_users || 0} color="text-green-600" />
                  <MiniStat label="Suspended" value={stats?.suspended_users || 0} color="text-amber-600" />
                  <MiniStat label="Banned" value={stats?.banned_users || 0} color="text-red-600" />
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* Instructors Tab */}
        {activeTab === 'instructors' && (
          <div className="space-y-4">
            {instructorsLoading ? (
              <Card className="p-8 text-center text-gray-500">Loading...</Card>
            ) : pendingInstructors.length === 0 ? (
              <Card className="p-8 text-center">
                <CheckCircle size={40} className="mx-auto text-green-500 mb-3" />
                <p className="font-medium text-gray-900">All caught up!</p>
                <p className="text-sm text-gray-500">No pending instructor applications.</p>
              </Card>
            ) : (
              pendingInstructors.map((instructor) => (
                <InstructorCard
                  key={instructor.profile.id}
                  instructor={instructor}
                  onVerify={() => verifyMutation.mutate(instructor.profile.id)}
                  onReject={(reason) => rejectMutation.mutate({ instructorId: instructor.profile.id, reason })}
                  isLoading={verifyMutation.isPending || rejectMutation.isPending}
                />
              ))
            )}
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            {/* Filters */}
            <Card className="p-4">
              <div className="flex flex-wrap items-center gap-3">
                <div className="relative flex-1 min-w-[200px]">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search users..."
                    className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <select
                  value={userRoleFilter}
                  onChange={(e) => setUserRoleFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Roles</option>
                  <option value="student">Students</option>
                  <option value="instructor">Instructors</option>
                  <option value="admin">Admins</option>
                </select>
                <select
                  value={userStatusFilter}
                  onChange={(e) => setUserStatusFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                  <option value="banned">Banned</option>
                </select>
              </div>
            </Card>

            {/* User List */}
            <Card className="overflow-hidden">
              {usersLoading ? (
                <div className="p-8 text-center text-gray-500">Loading...</div>
              ) : filteredUsers.length === 0 ? (
                <div className="p-8 text-center">
                  <Users size={40} className="mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">No users found</p>
                </div>
              ) : (
                filteredUsers.map((u) => (
                  <UserRow
                    key={u.id}
                    user={u}
                    onSuspend={(reason) => suspendMutation.mutate({ userId: u.id, reason })}
                    onBan={(reason) => banMutation.mutate({ userId: u.id, reason })}
                    onActivate={() => activateMutation.mutate(u.id)}
                    isLoading={suspendMutation.isPending || banMutation.isPending || activateMutation.isPending}
                  />
                ))
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
