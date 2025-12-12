import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MessageSquare, Settings, BarChart3 } from 'lucide-react';
import { Card } from '../UIComponents';

interface QuickAction {
  icon: React.ReactNode;
  label: string;
  href: string;
  badge?: string;
}

const QuickActions: React.FC = () => {
  const actions: QuickAction[] = [
    {
      icon: <Calendar size={18} />,
      label: 'Manage Availability',
      href: '/availability',
    },
    {
      icon: <MessageSquare size={18} />,
      label: 'Messages',
      href: '/messages',
      badge: undefined, // TODO: Add unread count when messaging is implemented
    },
    {
      icon: <Settings size={18} />,
      label: 'Account Settings',
      href: '/settings',
    },
    {
      icon: <BarChart3 size={18} />,
      label: 'View Analytics',
      href: '/analytics',
    },
  ];

  return (
    <Card className="p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
      <ul className="space-y-1">
        {actions.map((action) => (
          <li key={action.href}>
            <Link
              to={action.href}
              className="flex items-center justify-between gap-3 p-3 hover:bg-white/80 rounded-xl transition-colors text-gray-700 font-medium group"
            >
              <div className="flex items-center gap-3">
                <div className="bg-gray-100 p-2 rounded-lg text-gray-500 group-hover:bg-primary-100 group-hover:text-primary-600 transition-colors">
                  {action.icon}
                </div>
                <span className="text-sm">{action.label}</span>
              </div>
              {action.badge && (
                <span className="bg-primary-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                  {action.badge}
                </span>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </Card>
  );
};

export default QuickActions;
