/**
 * Calendar Header Component
 * Shows week navigation and current date range
 */

import React from 'react';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { formatDate } from '../../services/calendarAPI';

interface CalendarHeaderProps {
  weekStart: Date;
  weekEnd: Date;
  onPreviousWeek: () => void;
  onNextWeek: () => void;
  onToday: () => void;
}

export const CalendarHeader: React.FC<CalendarHeaderProps> = ({
  weekStart,
  weekEnd,
  onPreviousWeek,
  onNextWeek,
  onToday,
}) => {
  const formatDateRange = () => {
    const startMonth = weekStart.toLocaleDateString('en-US', { month: 'short' });
    const endMonth = weekEnd.toLocaleDateString('en-US', { month: 'short' });
    const startDay = weekStart.getDate();
    const endDay = weekEnd.getDate();
    const year = weekEnd.getFullYear();

    if (startMonth === endMonth) {
      return `${startMonth} ${startDay} - ${endDay}, ${year}`;
    }
    return `${startMonth} ${startDay} - ${endMonth} ${endDay}, ${year}`;
  };

  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Calendar className="h-6 w-6 text-blue-600" />
          Calendar
        </h1>
        <span className="text-lg text-gray-600">{formatDateRange()}</span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onToday}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Today
        </button>
        <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
          <button
            onClick={onPreviousWeek}
            className="p-2 hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
            aria-label="Previous week"
          >
            <ChevronLeft className="h-5 w-5 text-gray-600" />
          </button>
          <button
            onClick={onNextWeek}
            className="p-2 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 border-l border-gray-300"
            aria-label="Next week"
          >
            <ChevronRight className="h-5 w-5 text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CalendarHeader;
