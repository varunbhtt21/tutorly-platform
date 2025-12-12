import React from 'react';
import { Calendar, Users, CheckCircle2, DollarSign } from 'lucide-react';
import { Card } from '../UIComponents';
import type { DashboardStats } from '../../types/api';

interface StatsRowProps {
  stats: DashboardStats;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  borderColor: string;
  bgColor: string;
  iconColor: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  borderColor,
  bgColor,
  iconColor,
}) => (
  <Card className={`p-5 border-l-[5px] ${borderColor} hover:translate-y-[-2px] transition-transform`}>
    <div className="flex justify-between items-start">
      <div>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wide">{title}</p>
        <h3 className="text-3xl font-extrabold text-gray-900 mt-1">{value}</h3>
      </div>
      <div className={`${bgColor} p-2.5 rounded-xl ${iconColor} shadow-inner`}>
        {icon}
      </div>
    </div>
  </Card>
);

const StatsRow: React.FC<StatsRowProps> = ({ stats }) => {
  const formatEarnings = (amount: number) => {
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Upcoming Sessions"
        value={stats.upcoming_sessions_count}
        icon={<Calendar size={22} />}
        borderColor="border-l-primary-500"
        bgColor="bg-primary-100"
        iconColor="text-primary-600"
      />
      <StatCard
        title="Total Students"
        value={stats.total_students}
        icon={<Users size={22} />}
        borderColor="border-l-sky-500"
        bgColor="bg-sky-100"
        iconColor="text-sky-600"
      />
      <StatCard
        title="Completed Sessions"
        value={stats.completed_sessions}
        icon={<CheckCircle2 size={22} />}
        borderColor="border-l-emerald-500"
        bgColor="bg-emerald-100"
        iconColor="text-emerald-600"
      />
      <StatCard
        title="Total Earnings"
        value={formatEarnings(stats.total_earnings)}
        icon={<DollarSign size={22} />}
        borderColor="border-l-amber-500"
        bgColor="bg-amber-100"
        iconColor="text-amber-600"
      />
    </div>
  );
};

export default StatsRow;
