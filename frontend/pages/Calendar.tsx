/**
 * Calendar Page
 * Instructor's calendar for managing availability and viewing schedule
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  CalendarHeader,
  CalendarGrid,
  AvailabilityForm,
  AvailabilityList,
  TimeOffForm,
  TimeOffList,
} from '../components/calendar';
import {
  calendarAPI,
  getWeekStart,
  getWeekEnd,
  toDateString,
} from '../services/calendarAPI';
import { formatAPIError } from '../services';
import type {
  Availability,
  TimeOff,
  CalendarViewResponse,
} from '../types/api';

const CalendarPage: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // State
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(() =>
    getWeekStart(new Date())
  );
  const [calendarData, setCalendarData] = useState<CalendarViewResponse | null>(
    null
  );
  const [availabilities, setAvailabilities] = useState<Availability[]>([]);
  const [timeOffs, setTimeOffs] = useState<TimeOff[]>([]);
  const [isLoadingCalendar, setIsLoadingCalendar] = useState(true);
  const [isLoadingAvailability, setIsLoadingAvailability] = useState(true);
  const [isLoadingTimeOff, setIsLoadingTimeOff] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Computed values - memoize to prevent infinite re-renders
  const weekEnd = useMemo(() => getWeekEnd(currentWeekStart), [currentWeekStart]);

  // Redirect non-instructors
  useEffect(() => {
    if (!authLoading && (!user || user.role !== 'instructor')) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  // Fetch calendar data
  const fetchCalendarView = useCallback(async () => {
    setIsLoadingCalendar(true);
    setError(null);
    try {
      const data = await calendarAPI.getCalendarView(
        toDateString(currentWeekStart),
        toDateString(weekEnd)
      );
      setCalendarData(data);
    } catch (err) {
      const formatted = formatAPIError(err);
      setError(formatted.message);
    } finally {
      setIsLoadingCalendar(false);
    }
  }, [currentWeekStart, weekEnd]);

  // Fetch availability list
  const fetchAvailability = useCallback(async () => {
    setIsLoadingAvailability(true);
    try {
      const data = await calendarAPI.getMyAvailability();
      setAvailabilities(data.availabilities);
    } catch (err) {
      console.error('Failed to fetch availability:', err);
    } finally {
      setIsLoadingAvailability(false);
    }
  }, []);

  // Fetch time off list
  const fetchTimeOff = useCallback(async () => {
    setIsLoadingTimeOff(true);
    try {
      const data = await calendarAPI.getMyTimeOff();
      setTimeOffs(data.time_offs);
    } catch (err) {
      console.error('Failed to fetch time off:', err);
    } finally {
      setIsLoadingTimeOff(false);
    }
  }, []);

  // Load all data on mount and week change
  useEffect(() => {
    if (user?.role === 'instructor') {
      fetchCalendarView();
      fetchAvailability();
      fetchTimeOff();
    }
  }, [user, fetchCalendarView, fetchAvailability, fetchTimeOff]);

  // Navigation handlers
  const handlePreviousWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(newStart.getDate() - 7);
    setCurrentWeekStart(newStart);
  };

  const handleNextWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(newStart.getDate() + 7);
    setCurrentWeekStart(newStart);
  };

  const handleToday = () => {
    setCurrentWeekStart(getWeekStart(new Date()));
  };

  // Form submission handlers
  const handleAddRecurringAvailability = async (data: {
    day_of_week: number;
    start_time: string;
    end_time: string;
    slot_duration_minutes: number;
    break_minutes: number;
  }) => {
    setIsSubmitting(true);
    try {
      await calendarAPI.setRecurringAvailability(data);
      await Promise.all([fetchCalendarView(), fetchAvailability()]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddOneTimeAvailability = async (data: {
    specific_date: string;
    start_time: string;
    end_time: string;
    slot_duration_minutes: number;
    break_minutes: number;
  }) => {
    setIsSubmitting(true);
    try {
      await calendarAPI.setOneTimeAvailability(data);
      await Promise.all([fetchCalendarView(), fetchAvailability()]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteAvailability = async (id: number) => {
    try {
      await calendarAPI.deleteAvailability(id);
      await Promise.all([fetchCalendarView(), fetchAvailability()]);
    } catch (err) {
      const formatted = formatAPIError(err);
      setError(formatted.message);
    }
  };

  const handleAddTimeOff = async (data: {
    start_at: string;
    end_at: string;
    reason?: string;
  }) => {
    setIsSubmitting(true);
    try {
      await calendarAPI.addTimeOff(data);
      await Promise.all([fetchCalendarView(), fetchTimeOff()]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTimeOff = async (id: number) => {
    try {
      await calendarAPI.deleteTimeOff(id);
      await Promise.all([fetchCalendarView(), fetchTimeOff()]);
    } catch (err) {
      const formatted = formatAPIError(err);
      setError(formatted.message);
    }
  };

  // Delete individual slot
  const handleDeleteSlot = async (slotId: number) => {
    try {
      await calendarAPI.deleteSlot(slotId);
      // Refresh both calendar view and availability list (backend deletes availability rule if this was the last slot)
      await Promise.all([fetchCalendarView(), fetchAvailability()]);
    } catch (err) {
      const formatted = formatAPIError(err);
      setError(formatted.message);
    }
  };

  // Update individual slot (resize)
  const handleUpdateSlot = async (slotId: number, data: { start_at?: string; end_at?: string }) => {
    try {
      await calendarAPI.updateSlot(slotId, data);
      // Refresh both calendar view and availability list to keep sidebar in sync
      await Promise.all([fetchCalendarView(), fetchAvailability()]);
    } catch (err) {
      const formatted = formatAPIError(err);
      setError(formatted.message);
    }
  };

  // Refresh all data
  const handleRefresh = () => {
    fetchCalendarView();
    fetchAvailability();
    fetchTimeOff();
  };

  // Loading state
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <CalendarHeader
            weekStart={currentWeekStart}
            weekEnd={weekEnd}
            onPreviousWeek={handlePreviousWeek}
            onNextWeek={handleNextWeek}
            onToday={handleToday}
          />
          <button
            onClick={handleRefresh}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-600">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              &times;
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Calendar - 3 columns */}
          <div className="lg:col-span-3">
            <CalendarGrid
              days={calendarData?.days || []}
              isLoading={isLoadingCalendar}
              onAddAvailability={handleAddOneTimeAvailability}
              onDeleteAvailability={handleDeleteAvailability}
              onDeleteSlot={handleDeleteSlot}
              onUpdateSlot={handleUpdateSlot}
            />
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Add Availability */}
            <AvailabilityForm
              onSubmitRecurring={handleAddRecurringAvailability}
              onSubmitOneTime={handleAddOneTimeAvailability}
              isLoading={isSubmitting}
            />

            {/* Add Time Off */}
            <TimeOffForm onSubmit={handleAddTimeOff} isLoading={isSubmitting} />

            {/* Availability List */}
            <AvailabilityList
              availabilities={availabilities}
              onDelete={handleDeleteAvailability}
              isLoading={isLoadingAvailability}
            />

            {/* Time Off List */}
            <TimeOffList
              timeOffs={timeOffs}
              onDelete={handleDeleteTimeOff}
              isLoading={isLoadingTimeOff}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarPage;
