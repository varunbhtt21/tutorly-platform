/**
 * Stats Row Component
 * Modern stat cards with animated counters and hover effects
 */

import React, { useState, useEffect, useRef } from 'react';
import { Calendar, Users, CheckCircle2, DollarSign, TrendingUp } from 'lucide-react';
import { Card } from '../UIComponents';
import type { DashboardStats } from '../../types/api';

interface StatsRowProps {
  stats: DashboardStats;
}

interface StatCardProps {
  title: string;
  value: number;
  prefix?: string;
  suffix?: string;
  icon: React.ReactNode;
  gradient: string;
  iconBg: string;
  iconColor: string;
  trend?: number;
  delay?: number;
}

// Animated counter hook
const useCountUp = (end: number, duration: number = 1500, delay: number = 0) => {
  const [count, setCount] = useState(0);
  const countRef = useRef(0);
  const frameRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    const startTime = Date.now() + delay;
    const endValue = end;

    const animate = () => {
      const now = Date.now();
      if (now < startTime) {
        frameRef.current = requestAnimationFrame(animate);
        return;
      }

      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function (easeOutExpo)
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const currentCount = Math.floor(easeProgress * endValue);

      if (currentCount !== countRef.current) {
        countRef.current = currentCount;
        setCount(currentCount);
      }

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      }
    };

    frameRef.current = requestAnimationFrame(animate);

    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [end, duration, delay]);

  return count;
};

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  prefix = '',
  suffix = '',
  icon,
  gradient,
  iconBg,
  iconColor,
  trend,
  delay = 0,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const animatedValue = useCountUp(value, 1500, delay);

  return (
    <Card
      className={`
        p-5 relative overflow-hidden group cursor-default
        transition-all duration-300 ease-out
        hover:shadow-2xl hover:shadow-gray-200/50
        ${isHovered ? 'scale-[1.02]' : 'scale-100'}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background gradient on hover */}
      <div
        className={`
          absolute inset-0 opacity-0 group-hover:opacity-100
          transition-opacity duration-500
          ${gradient}
        `}
      />

      {/* Decorative circles */}
      <div
        className={`
          absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-10
          transition-all duration-500
          ${iconBg}
          ${isHovered ? 'scale-150 opacity-20' : 'scale-100'}
        `}
      />

      <div className="relative flex justify-between items-start">
        <div className="flex-grow">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">
            {title}
          </p>
          <div className="flex items-baseline gap-1">
            <h3 className="text-3xl font-extrabold text-gray-900 tabular-nums">
              {prefix}{animatedValue.toLocaleString()}{suffix}
            </h3>
          </div>

          {/* Optional trend indicator */}
          {trend !== undefined && trend > 0 && (
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp size={12} className="text-emerald-500" />
              <span className="text-xs font-semibold text-emerald-600">
                +{trend}% this week
              </span>
            </div>
          )}
        </div>

        <div
          className={`
            ${iconBg} p-3 rounded-xl ${iconColor}
            shadow-lg transition-all duration-300
            ${isHovered ? 'scale-110 rotate-3' : 'scale-100 rotate-0'}
          `}
        >
          {icon}
        </div>
      </div>

      {/* Bottom accent line */}
      <div
        className={`
          absolute bottom-0 left-0 h-1 rounded-full
          transition-all duration-500 ease-out
          ${iconBg}
          ${isHovered ? 'w-full' : 'w-0'}
        `}
      />
    </Card>
  );
};

const StatsRow: React.FC<StatsRowProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Upcoming Sessions"
        value={stats.upcoming_sessions_count}
        icon={<Calendar size={22} strokeWidth={2.5} />}
        gradient="bg-gradient-to-br from-primary-50/50 to-blue-50/50"
        iconBg="bg-primary-100"
        iconColor="text-primary-600"
        delay={0}
      />
      <StatCard
        title="Total Students"
        value={stats.total_students}
        icon={<Users size={22} strokeWidth={2.5} />}
        gradient="bg-gradient-to-br from-sky-50/50 to-cyan-50/50"
        iconBg="bg-sky-100"
        iconColor="text-sky-600"
        delay={100}
      />
      <StatCard
        title="Completed Sessions"
        value={stats.completed_sessions}
        icon={<CheckCircle2 size={22} strokeWidth={2.5} />}
        gradient="bg-gradient-to-br from-emerald-50/50 to-green-50/50"
        iconBg="bg-emerald-100"
        iconColor="text-emerald-600"
        delay={200}
      />
      <StatCard
        title="Total Earnings"
        value={stats.total_earnings}
        prefix="$"
        icon={<DollarSign size={22} strokeWidth={2.5} />}
        gradient="bg-gradient-to-br from-amber-50/50 to-yellow-50/50"
        iconBg="bg-amber-100"
        iconColor="text-amber-600"
        delay={300}
      />
    </div>
  );
};

export default StatsRow;
