/**
 * Time Off List Component
 * Shows list of configured time off periods
 */

import React from 'react';
import { CalendarOff, Trash2, Clock } from 'lucide-react';
import type { TimeOff } from '../../types/api';
import { formatDateTime } from '../../services/calendarAPI';

interface TimeOffListProps {
  timeOffs: TimeOff[];
  onDelete: (id: number) => Promise<void>;
  isLoading?: boolean;
}

export const TimeOffList: React.FC<TimeOffListProps> = ({
  timeOffs,
  onDelete,
  isLoading = false,
}) => {
  const [deletingId, setDeletingId] = React.useState<number | null>(null);

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      await onDelete(id);
    } finally {
      setDeletingId(null);
    }
  };

  // Sort by start date, most recent first
  const sortedTimeOffs = [...timeOffs].sort(
    (a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime()
  );

  // Separate past and upcoming time offs
  const now = new Date();
  const upcomingTimeOffs = sortedTimeOffs.filter(
    (to) => new Date(to.end_at) > now
  );
  const pastTimeOffs = sortedTimeOffs.filter(
    (to) => new Date(to.end_at) <= now
  );

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-5 bg-gray-200 rounded w-32"></div>
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-40"></div>
                  <div className="h-3 bg-gray-200 rounded w-24"></div>
                </div>
              </div>
              <div className="w-8 h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (timeOffs.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <CalendarOff className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">No time off scheduled</p>
        <p className="text-sm text-gray-400 mt-1">
          Block time when you're unavailable for sessions
        </p>
      </div>
    );
  }

  const formatDuration = (hours: number): string => {
    if (hours < 1) {
      return `${Math.round(hours * 60)}min`;
    }
    if (hours < 24) {
      return `${hours.toFixed(1)}h`;
    }
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''}`;
  };

  const renderTimeOffItem = (timeOff: TimeOff, isPast: boolean) => (
    <div
      key={timeOff.id}
      className={`flex items-center justify-between py-3 px-3 rounded-lg ${
        isPast ? 'bg-gray-50 opacity-60' : 'bg-gray-100'
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isPast ? 'bg-gray-200' : 'bg-gray-200'
          }`}
        >
          <CalendarOff className={`h-4 w-4 ${isPast ? 'text-gray-400' : 'text-gray-600'}`} />
        </div>
        <div>
          <div className="text-sm font-medium text-gray-900">
            {formatDateTime(timeOff.start_at)}
          </div>
          <div className="text-xs text-gray-500">
            to {formatDateTime(timeOff.end_at)}
            <span className="mx-1.5">•</span>
            <span className="inline-flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDuration(timeOff.duration_hours)}
            </span>
            {timeOff.reason && (
              <>
                <span className="mx-1.5">•</span>
                <span className="italic">{timeOff.reason}</span>
              </>
            )}
          </div>
        </div>
      </div>
      {!isPast && (
        <button
          onClick={() => handleDelete(timeOff.id)}
          disabled={deletingId === timeOff.id}
          className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
          title="Delete time off"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Upcoming Time Off */}
      {upcomingTimeOffs.length > 0 && (
        <div className="p-4">
          <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2 mb-3">
            <CalendarOff className="h-4 w-4 text-gray-600" />
            Upcoming Time Off ({upcomingTimeOffs.length})
          </h4>
          <div className="space-y-2">
            {upcomingTimeOffs.map((to) => renderTimeOffItem(to, false))}
          </div>
        </div>
      )}

      {/* Past Time Off (collapsed by default) */}
      {pastTimeOffs.length > 0 && (
        <div className="p-4 border-t border-gray-100">
          <details>
            <summary className="text-sm font-medium text-gray-500 cursor-pointer hover:text-gray-700">
              Past Time Off ({pastTimeOffs.length})
            </summary>
            <div className="space-y-2 mt-3">
              {pastTimeOffs.slice(0, 5).map((to) => renderTimeOffItem(to, true))}
              {pastTimeOffs.length > 5 && (
                <p className="text-xs text-gray-400 text-center py-2">
                  And {pastTimeOffs.length - 5} more...
                </p>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
};

export default TimeOffList;
