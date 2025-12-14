/**
 * Availability List Component
 * Shows list of configured availability slots
 */

import React from 'react';
import { Clock, Trash2, Calendar, RefreshCw } from 'lucide-react';
import type { Availability } from '../../types/api';
import { getDayName, formatTime, formatDate } from '../../services/calendarAPI';

/**
 * Format duration in minutes to human-readable string
 * e.g., 300 -> "5 hours", 90 -> "1.5 hours", 50 -> "50min"
 */
const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes}min`;
  }
  const hours = minutes / 60;
  if (hours === Math.floor(hours)) {
    return `${hours} hour${hours > 1 ? 's' : ''}`;
  }
  return `${hours.toFixed(1)} hours`;
};

/**
 * Calculate duration in minutes from start and end time strings (HH:MM format)
 * This is the source of truth for one-time availability duration,
 * as it reflects actual time range even after resizing.
 */
const calculateDurationFromTimeRange = (startTime: string, endTime: string): number => {
  const [startHour, startMin] = startTime.split(':').map(Number);
  const [endHour, endMin] = endTime.split(':').map(Number);
  return (endHour * 60 + endMin) - (startHour * 60 + startMin);
};

interface AvailabilityListProps {
  availabilities: Availability[];
  onDelete: (id: number) => Promise<void>;
  isLoading?: boolean;
}

export const AvailabilityList: React.FC<AvailabilityListProps> = ({
  availabilities,
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

  const recurringAvailabilities = availabilities.filter(
    (a) => a.availability_type === 'recurring'
  );
  const oneTimeAvailabilities = availabilities.filter(
    (a) => a.availability_type === 'one_time'
  );

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-5 bg-gray-200 rounded w-40"></div>
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-24"></div>
                  <div className="h-3 bg-gray-200 rounded w-32"></div>
                </div>
              </div>
              <div className="w-8 h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (availabilities.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <Clock className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">No availability configured yet</p>
        <p className="text-sm text-gray-400 mt-1">
          Add your available hours to let students book sessions
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Recurring Availability */}
      {recurringAvailabilities.length > 0 && (
        <div className="p-4 border-b border-gray-100">
          <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2 mb-3">
            <RefreshCw className="h-4 w-4 text-blue-600" />
            Weekly Schedule
          </h4>
          <div className="space-y-2">
            {recurringAvailabilities.map((avail) => (
              <div
                key={avail.id}
                className="flex items-center justify-between py-2 px-3 bg-blue-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-semibold text-blue-700">
                      {avail.day_of_week !== null
                        ? getDayName(avail.day_of_week).slice(0, 2)
                        : '??'}
                    </span>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {avail.day_of_week !== null
                        ? getDayName(avail.day_of_week)
                        : 'Unknown'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTime(avail.start_time)} - {formatTime(avail.end_time)}
                      <span className="mx-1.5">•</span>
                      {avail.slot_duration_minutes}min slots
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(avail.id)}
                  disabled={deletingId === avail.id}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Delete availability"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* One-Time Availability */}
      {oneTimeAvailabilities.length > 0 && (
        <div className="p-4">
          <h4 className="text-sm font-semibold text-gray-900 flex items-center gap-2 mb-3">
            <Calendar className="h-4 w-4 text-green-600" />
            One-Time Availability
          </h4>
          <div className="space-y-2">
            {oneTimeAvailabilities.map((avail) => (
              <div
                key={avail.id}
                className="flex items-center justify-between py-2 px-3 bg-green-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <Calendar className="h-4 w-4 text-green-700" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {avail.specific_date
                        ? formatDate(avail.specific_date)
                        : 'Unknown date'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTime(avail.start_time)} - {formatTime(avail.end_time)}
                      <span className="mx-1.5">•</span>
                      {formatDuration(calculateDurationFromTimeRange(avail.start_time, avail.end_time))}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(avail.id)}
                  disabled={deletingId === avail.id}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Delete availability"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AvailabilityList;
