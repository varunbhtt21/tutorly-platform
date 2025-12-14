/**
 * Quick Actions Component
 * Modern action buttons with hover effects and micro-animations
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MessageSquare, Settings, BarChart3, ChevronRight, Zap } from 'lucide-react';
import { Card } from '../UIComponents';

interface QuickAction {
  icon: React.ReactNode;
  label: string;
  description: string;
  href: string;
  badge?: string;
  gradient: string;
  iconColor: string;
}

interface ActionItemProps {
  action: QuickAction;
  index: number;
}

const ActionItem: React.FC<ActionItemProps> = ({ action, index }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Link
      to={action.href}
      className={`
        relative flex items-center gap-3 p-3 rounded-xl
        transition-all duration-300 ease-out group
        ${isHovered ? 'bg-white shadow-lg shadow-gray-200/50' : 'bg-transparent hover:bg-white/50'}
      `}
      style={{
        animation: `fadeInUp 0.4s ease-out forwards`,
        animationDelay: `${index * 0.1}s`,
        opacity: 0,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Icon container with gradient background */}
      <div
        className={`
          relative p-2.5 rounded-xl transition-all duration-300
          ${isHovered ? action.gradient : 'bg-gray-100'}
        `}
      >
        <div
          className={`
            transition-all duration-300
            ${isHovered ? action.iconColor : 'text-gray-500'}
          `}
        >
          {action.icon}
        </div>
        {/* Floating particle effect on hover */}
        {isHovered && (
          <div className="absolute inset-0 overflow-hidden rounded-xl">
            <div className="absolute w-1 h-1 bg-white/60 rounded-full animate-float-1" />
            <div className="absolute w-1 h-1 bg-white/40 rounded-full animate-float-2" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-grow min-w-0">
        <span
          className={`
            text-sm font-semibold block truncate
            transition-colors duration-300
            ${isHovered ? 'text-gray-900' : 'text-gray-700'}
          `}
        >
          {action.label}
        </span>
        <span className="text-xs text-gray-400 block truncate">
          {action.description}
        </span>
      </div>

      {/* Badge or Arrow */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {action.badge && (
          <span className="bg-gradient-to-r from-primary-500 to-blue-500 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-sm animate-pulse">
            {action.badge}
          </span>
        )}
        <ChevronRight
          size={16}
          className={`
            text-gray-300 transition-all duration-300
            ${isHovered ? 'text-gray-400 translate-x-1' : ''}
          `}
        />
      </div>

      {/* Hover gradient overlay */}
      <div
        className={`
          absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100
          transition-opacity duration-300 pointer-events-none
          bg-gradient-to-r from-transparent via-white/20 to-transparent
        `}
      />
    </Link>
  );
};

const QuickActions: React.FC = () => {
  const actions: QuickAction[] = [
    {
      icon: <Calendar size={18} strokeWidth={2.5} />,
      label: 'Manage Availability',
      description: 'Set your teaching hours',
      href: '/availability',
      gradient: 'bg-gradient-to-br from-primary-100 to-blue-100',
      iconColor: 'text-primary-600',
    },
    {
      icon: <MessageSquare size={18} strokeWidth={2.5} />,
      label: 'Messages',
      description: 'Chat with students',
      href: '/messages',
      badge: undefined, // TODO: Add unread count when messaging is implemented
      gradient: 'bg-gradient-to-br from-emerald-100 to-green-100',
      iconColor: 'text-emerald-600',
    },
    {
      icon: <Settings size={18} strokeWidth={2.5} />,
      label: 'Account Settings',
      description: 'Manage your profile',
      href: '/settings',
      gradient: 'bg-gradient-to-br from-gray-100 to-slate-100',
      iconColor: 'text-gray-600',
    },
    {
      icon: <BarChart3 size={18} strokeWidth={2.5} />,
      label: 'View Analytics',
      description: 'Track your performance',
      href: '/analytics',
      gradient: 'bg-gradient-to-br from-amber-100 to-orange-100',
      iconColor: 'text-amber-600',
    },
  ];

  return (
    <Card className="p-5 overflow-hidden">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <div className="w-8 h-8 bg-gradient-to-br from-primary-100 to-blue-100 rounded-lg flex items-center justify-center">
          <Zap size={16} className="text-primary-600" />
        </div>
        Quick Actions
      </h3>

      <div className="space-y-1">
        {actions.map((action, index) => (
          <ActionItem key={action.href} action={action} index={index} />
        ))}
      </div>

      {/* CSS animations */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes float-1 {
          0%, 100% {
            transform: translate(4px, 4px);
            opacity: 0;
          }
          50% {
            transform: translate(20px, -10px);
            opacity: 1;
          }
        }
        @keyframes float-2 {
          0%, 100% {
            transform: translate(20px, 20px);
            opacity: 0;
          }
          50% {
            transform: translate(5px, 5px);
            opacity: 1;
          }
        }
        .animate-float-1 {
          animation: float-1 1.5s ease-in-out infinite;
        }
        .animate-float-2 {
          animation: float-2 1.8s ease-in-out infinite;
          animation-delay: 0.3s;
        }
      `}</style>
    </Card>
  );
};

export default QuickActions;
