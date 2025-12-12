import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Clock, User, ChevronRight } from 'lucide-react';
import { Card, Button, Badge } from '../UIComponents';
import type { UpcomingSession } from '../../types/api';

interface UpcomingSessionsListProps {
  sessions: UpcomingSession[];
}

const UpcomingSessionsList: React.FC<UpcomingSessionsListProps> = ({ sessions }) => {
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    let dayText = '';
    if (date.toDateString() === today.toDateString()) {
      dayText = 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      dayText = 'Tomorrow';
    } else {
      dayText = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    const timeText = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });

    return { dayText, timeText };
  };

  if (sessions.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Upcoming Sessions</h3>
        <div className="bg-gray-50 rounded-xl p-8 text-center border border-dashed border-gray-200">
          <div className="bg-gray-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
            <Calendar size={24} className="text-gray-400" />
          </div>
          <p className="text-gray-500 text-sm">No upcoming sessions</p>
          <p className="text-gray-400 text-xs mt-1">
            Sessions will appear here once students book with you
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Upcoming Sessions</h3>
        <Link to="/sessions" className="text-primary-600 text-sm font-medium hover:text-primary-700 flex items-center gap-1">
          View All <ChevronRight size={16} />
        </Link>
      </div>

      <div className="space-y-3">
        {sessions.slice(0, 3).map((session) => {
          const { dayText, timeText } = formatDateTime(session.scheduled_at);

          return (
            <div
              key={session.id}
              className="flex items-center gap-4 p-4 bg-gray-50/80 rounded-xl hover:bg-gray-100/80 transition-colors"
            >
              {/* Student Avatar */}
              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <User size={18} className="text-primary-600" />
              </div>

              {/* Session Info */}
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-gray-900 truncate">
                    {session.student_name}
                  </h4>
                  {session.is_trial && (
                    <Badge variant="secondary">Trial</Badge>
                  )}
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-500 mt-0.5">
                  <span className="flex items-center gap-1">
                    <Calendar size={12} />
                    {dayText}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    {timeText}
                  </span>
                  <span className="text-gray-400">
                    {session.duration_minutes}min
                  </span>
                </div>
              </div>

              {/* Subject */}
              <div className="hidden sm:block">
                <span className="text-sm font-medium text-gray-600 bg-white px-3 py-1 rounded-lg border border-gray-100">
                  {session.subject}
                </span>
              </div>

              {/* Actions */}
              <div className="flex-shrink-0">
                <Button variant="primary" size="sm">
                  Join
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default UpcomingSessionsList;
