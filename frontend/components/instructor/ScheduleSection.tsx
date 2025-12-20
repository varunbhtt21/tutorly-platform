/**
 * ScheduleSection Component
 *
 * Displays instructor's available time slots in a weekly calendar format.
 * Designed to match the Preply-style schedule display on instructor profiles.
 *
 * Architecture:
 * - Uses the booking-slots API for fetching available slots
 * - Supports duration filtering (25 mins / 50 mins)
 * - Timezone-aware display with user's local timezone
 * - Weekly navigation with configurable visible days
 * - Reusable across different pages (profile, search results, etc.)
 *
 * Usage:
 *   <ScheduleSection
 *     instructorId={123}
 *     onSlotSelect={(slot) => handleBooking(slot)}
 *     showFullScheduleLink={true}
 *   />
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Info, Loader2 } from 'lucide-react';
import { calendarAPI } from '../../services';
import type { BookingSlotItem } from '../../types/api';

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface ScheduleSectionProps {
  /** Instructor ID to fetch availability for */
  instructorId: number;
  /** Callback when a slot is selected for booking */
  onSlotSelect?: (slot: BookingSlotItem) => void;
  /** Number of days to display (default: 7) */
  visibleDays?: number;
  /** Maximum slots to show per day in collapsed view (default: 9) */
  maxSlotsPerDay?: number;
  /** Whether to show the "View full schedule" button */
  showFullScheduleLink?: boolean;
  /** Custom class name for the container */
  className?: string;
}

export type LessonDuration = 25 | 50;

interface DaySlots {
  date: Date;
  dayName: string;
  dayNumber: number;
  slots: BookingSlotItem[];
  hasMore: boolean;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get the start of the week (Friday for current week display)
 * Adjusts to start from today if today is after Friday
 */
function getWeekStartDate(baseDate: Date): Date {
  const date = new Date(baseDate);
  date.setHours(0, 0, 0, 0);
  return date;
}

/**
 * Format date to YYYY-MM-DD string
 */
function formatDateString(date: Date): string {
  return date.toISOString().split('T')[0];
}

/**
 * Get user's timezone string (e.g., "Asia/Kolkata")
 */
function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Get timezone offset string (e.g., "GMT +5:30")
 */
function getTimezoneOffsetString(): string {
  const offset = new Date().getTimezoneOffset();
  const hours = Math.floor(Math.abs(offset) / 60);
  const minutes = Math.abs(offset) % 60;
  const sign = offset <= 0 ? '+' : '-';
  return `GMT ${sign}${hours}${minutes > 0 ? `:${minutes.toString().padStart(2, '0')}` : ''}`;
}

/**
 * Format time from ISO string to display format (e.g., "07:30")
 */
function formatSlotTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

/**
 * Format date range for header display
 */
function formatDateRange(startDate: Date, endDate: Date): string {
  const startMonth = startDate.toLocaleDateString('en-US', { month: 'short' });
  const endMonth = endDate.toLocaleDateString('en-US', { month: 'short' });
  const startDay = startDate.getDate();
  const endDay = endDate.getDate();
  const year = endDate.getFullYear();

  if (startMonth === endMonth) {
    return `${startMonth} ${startDay} – ${endDay}, ${year}`;
  }
  return `${startMonth} ${startDay} – ${endMonth} ${endDay}, ${year}`;
}

/**
 * Filter slots by duration
 */
function filterSlotsByDuration(slots: BookingSlotItem[], duration: LessonDuration): BookingSlotItem[] {
  // Allow slots that are at least the requested duration
  // 25 min slots: show all slots >= 25 mins
  // 50 min slots: show only slots >= 50 mins
  return slots.filter(slot => slot.duration_minutes >= duration);
}

// ============================================================================
// Sub-Components
// ============================================================================

interface DurationToggleProps {
  selected: LessonDuration;
  onChange: (duration: LessonDuration) => void;
}

const DurationToggle: React.FC<DurationToggleProps> = ({ selected, onChange }) => {
  return (
    <div className="flex rounded-lg border border-gray-200 overflow-hidden">
      <button
        onClick={() => onChange(25)}
        className={`px-6 py-2.5 text-sm font-medium transition-colors ${
          selected === 25
            ? 'bg-gray-100 text-gray-900'
            : 'bg-white text-gray-600 hover:bg-gray-50'
        }`}
      >
        25 mins
      </button>
      <button
        onClick={() => onChange(50)}
        className={`px-6 py-2.5 text-sm font-medium transition-colors border-l border-gray-200 ${
          selected === 50
            ? 'bg-gray-100 text-gray-900'
            : 'bg-white text-gray-600 hover:bg-gray-50'
        }`}
      >
        50 mins
      </button>
    </div>
  );
};

interface WeekNavigationProps {
  startDate: Date;
  endDate: Date;
  onPrevious: () => void;
  onNext: () => void;
  canGoPrevious: boolean;
}

const WeekNavigation: React.FC<WeekNavigationProps> = ({
  startDate,
  endDate,
  onPrevious,
  onNext,
  canGoPrevious,
}) => {
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={onPrevious}
        disabled={!canGoPrevious}
        className={`p-2 rounded-full transition-colors ${
          canGoPrevious
            ? 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            : 'bg-gray-50 text-gray-300 cursor-not-allowed'
        }`}
        aria-label="Previous week"
      >
        <ChevronLeft size={20} />
      </button>
      <span className="text-sm font-medium text-gray-900 min-w-[160px] text-center">
        {formatDateRange(startDate, endDate)}
      </span>
      <button
        onClick={onNext}
        className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
        aria-label="Next week"
      >
        <ChevronRight size={20} />
      </button>
    </div>
  );
};

interface TimezoneDisplayProps {
  timezone: string;
  offset: string;
}

const TimezoneDisplay: React.FC<TimezoneDisplayProps> = ({ timezone, offset }) => {
  return (
    <div className="flex items-center gap-2 px-3 py-2 border border-gray-200 rounded-lg">
      <span className="text-sm text-gray-900">{timezone.replace('_', '/')}</span>
      <span className="text-xs text-gray-500">{offset}</span>
      <ChevronRight size={16} className="text-gray-400 rotate-90" />
    </div>
  );
};

interface DayColumnProps {
  day: DaySlots;
  onSlotSelect?: (slot: BookingSlotItem) => void;
  maxSlots: number;
  isToday: boolean;
}

const DayColumn: React.FC<DayColumnProps> = ({ day, onSlotSelect, maxSlots, isToday }) => {
  const visibleSlots = day.slots.slice(0, maxSlots);
  const hiddenCount = day.slots.length - maxSlots;

  return (
    <div className="flex flex-col min-w-0">
      {/* Day Header */}
      <div className={`text-center pb-3 mb-3 border-b-2 ${
        isToday ? 'border-pink-400' : 'border-transparent'
      }`}>
        <div className="text-sm text-gray-500">{day.dayName}</div>
        <div className={`text-lg font-semibold ${isToday ? 'text-gray-900' : 'text-gray-700'}`}>
          {day.dayNumber}
        </div>
      </div>

      {/* Slots */}
      <div className="space-y-1.5 flex-1">
        {visibleSlots.length === 0 ? (
          <div className="text-center text-gray-400 text-sm py-4">—</div>
        ) : (
          visibleSlots.map((slot, index) => (
            <button
              key={slot.id ?? `${slot.start_at}-${index}`}
              onClick={() => onSlotSelect?.(slot)}
              className="w-full py-2 px-1 text-sm font-medium text-gray-900 hover:text-primary-600
                         underline underline-offset-2 decoration-gray-300 hover:decoration-primary-400
                         transition-colors text-center"
            >
              {formatSlotTime(slot.start_at)}
            </button>
          ))
        )}
        {hiddenCount > 0 && (
          <div className="text-center text-xs text-gray-400 pt-1">
            +{hiddenCount} more
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Main Component
// ============================================================================

export const ScheduleSection: React.FC<ScheduleSectionProps> = ({
  instructorId,
  onSlotSelect,
  visibleDays = 7,
  maxSlotsPerDay = 9,
  showFullScheduleLink = true,
  className = '',
}) => {
  // State
  const [duration, setDuration] = useState<LessonDuration>(25);
  const [weekOffset, setWeekOffset] = useState(0);
  const [allSlots, setAllSlots] = useState<BookingSlotItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // Computed values
  const timezone = useMemo(() => getUserTimezone(), []);
  const timezoneOffset = useMemo(() => getTimezoneOffsetString(), []);

  const startDate = useMemo(() => {
    const today = new Date();
    today.setDate(today.getDate() + (weekOffset * 7));
    return getWeekStartDate(today);
  }, [weekOffset]);

  const endDate = useMemo(() => {
    const end = new Date(startDate);
    end.setDate(end.getDate() + visibleDays - 1);
    return end;
  }, [startDate, visibleDays]);

  const canGoPrevious = weekOffset > 0;

  // Fetch slots
  const fetchSlots = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await calendarAPI.getAvailableBookingSlots(
        instructorId,
        formatDateString(startDate),
        formatDateString(endDate)
      );

      setAllSlots(response.slots);
    } catch (err) {
      console.error('Failed to fetch booking slots:', err);
      setError('Unable to load schedule. Please try again.');
      setAllSlots([]);
    } finally {
      setLoading(false);
    }
  }, [instructorId, startDate, endDate]);

  useEffect(() => {
    fetchSlots();
  }, [fetchSlots]);

  // Filter and organize slots by day
  const daySlots = useMemo((): DaySlots[] => {
    const filteredSlots = filterSlotsByDuration(allSlots, duration);
    const days: DaySlots[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 0; i < visibleDays; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      const dateStr = formatDateString(date);

      const slotsForDay = filteredSlots
        .filter(slot => slot.start_at.startsWith(dateStr))
        .sort((a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime());

      days.push({
        date,
        dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
        dayNumber: date.getDate(),
        slots: slotsForDay,
        hasMore: slotsForDay.length > maxSlotsPerDay,
      });
    }

    return days;
  }, [allSlots, duration, startDate, visibleDays, maxSlotsPerDay]);

  // Check if a day is today
  const isToday = useCallback((date: Date): boolean => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  }, []);

  // Navigation handlers
  const handlePrevious = () => {
    if (canGoPrevious) {
      setWeekOffset(prev => prev - 1);
    }
  };

  const handleNext = () => {
    setWeekOffset(prev => prev + 1);
  };

  // Toggle expanded view to show all slots
  const handleToggleExpand = () => {
    setIsExpanded(prev => !prev);
  };

  // Calculate effective max slots based on expanded state
  const effectiveMaxSlots = isExpanded ? Infinity : maxSlotsPerDay;

  return (
    <div className={`bg-white ${className}`}>
      {/* Header */}
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Schedule</h2>

      {/* Info Banner */}
      <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-xl mb-6">
        <Info size={20} className="text-blue-600 mt-0.5 shrink-0" />
        <p className="text-sm text-gray-700">
          Choose the time for your first lesson. The timings are displayed in your local timezone.
        </p>
      </div>

      {/* Controls Row */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <DurationToggle selected={duration} onChange={setDuration} />

        <div className="flex items-center gap-4">
          <WeekNavigation
            startDate={startDate}
            endDate={endDate}
            onPrevious={handlePrevious}
            onNext={handleNext}
            canGoPrevious={canGoPrevious}
          />
          <TimezoneDisplay timezone={timezone} offset={timezoneOffset} />
        </div>
      </div>

      {/* Schedule Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 size={32} className="animate-spin text-primary-500" />
        </div>
      ) : error ? (
        <div className="text-center py-16">
          <p className="text-gray-500 mb-4">{error}</p>
          <button
            onClick={fetchSlots}
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Try again
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-7 gap-4 mb-6">
          {daySlots.map((day) => (
            <DayColumn
              key={formatDateString(day.date)}
              day={day}
              onSlotSelect={onSlotSelect}
              maxSlots={effectiveMaxSlots}
              isToday={isToday(day.date)}
            />
          ))}
        </div>
      )}

      {/* View Full Schedule / Collapse Button */}
      {showFullScheduleLink && !loading && !error && (
        <div className="text-center pt-4 border-t border-gray-100">
          <button
            onClick={handleToggleExpand}
            className="text-gray-600 hover:text-gray-900 font-medium text-sm
                       border border-gray-200 rounded-lg px-6 py-2.5
                       hover:bg-gray-50 transition-colors"
          >
            {isExpanded ? 'Show less' : 'View full schedule'}
          </button>
        </div>
      )}
    </div>
  );
};

export default ScheduleSection;
