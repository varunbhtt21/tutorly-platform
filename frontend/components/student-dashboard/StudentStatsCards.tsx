/**
 * Student Stats Cards Component
 *
 * Displays key statistics for the student dashboard:
 * - Total sessions completed
 * - Hours of learning
 * - Current streak
 * - Total spent
 */

import { BookOpen, Clock, Flame, Wallet } from 'lucide-react';
import { StudentStats } from '../../services/studentAPI';

interface StudentStatsCardsProps {
  stats: StudentStats;
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subValue?: string;
  gradient: string;
  iconBg: string;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  subValue,
  gradient,
  iconBg,
}) => (
  <div className={`relative overflow-hidden rounded-2xl p-5 ${gradient} border border-white/50 shadow-lg hover:shadow-xl transition-all hover:scale-[1.02]`}>
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {subValue && (
          <p className="text-xs text-gray-500 mt-1">{subValue}</p>
        )}
      </div>
      <div className={`p-2.5 rounded-xl ${iconBg}`}>
        {icon}
      </div>
    </div>
    {/* Decorative element */}
    <div className="absolute -bottom-4 -right-4 w-20 h-20 rounded-full bg-white/20 blur-xl" />
  </div>
);

export const StudentStatsCards: React.FC<StudentStatsCardsProps> = ({ stats }) => {
  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        icon={<BookOpen size={20} className="text-primary-600" />}
        label="Sessions Completed"
        value={stats.total_sessions_completed}
        subValue={`${stats.total_instructors} instructor${stats.total_instructors !== 1 ? 's' : ''}`}
        gradient="bg-gradient-to-br from-primary-50 to-blue-50"
        iconBg="bg-primary-100"
      />
      <StatCard
        icon={<Clock size={20} className="text-blue-600" />}
        label="Hours Learning"
        value={stats.total_hours_learning.toFixed(1)}
        subValue="Total learning time"
        gradient="bg-gradient-to-br from-blue-50 to-cyan-50"
        iconBg="bg-blue-100"
      />
      <StatCard
        icon={<Flame size={20} className="text-orange-600" />}
        label="Current Streak"
        value={`${stats.current_streak_weeks} week${stats.current_streak_weeks !== 1 ? 's' : ''}`}
        subValue={stats.current_streak_weeks > 0 ? "Keep it up!" : "Start learning!"}
        gradient="bg-gradient-to-br from-orange-50 to-amber-50"
        iconBg="bg-orange-100"
      />
      <StatCard
        icon={<Wallet size={20} className="text-green-600" />}
        label="Total Invested"
        value={formatCurrency(stats.total_spent, stats.currency)}
        subValue={`${stats.trial_sessions_used} trial${stats.trial_sessions_used !== 1 ? 's' : ''} used`}
        gradient="bg-gradient-to-br from-green-50 to-emerald-50"
        iconBg="bg-green-100"
      />
    </div>
  );
};

export default StudentStatsCards;
