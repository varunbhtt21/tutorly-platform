/**
 * Slot Selector Component
 * Displays available time slots for booking a lesson
 */

import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import api from '../../lib/axios';

interface Slot {
  id: number;
  start_at: string;
  end_at: string;
  duration_minutes: number;
  status: string;
}

interface SlotSelectorProps {
  instructorId: number;
  onSlotSelect: (slot: Slot) => void;
  selectedSlotId?: number;
}

const SlotSelector: React.FC<SlotSelectorProps> = ({
  instructorId,
  onSlotSelect,
  selectedSlotId,
}) => {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [weekStart, setWeekStart] = useState<Date>(getWeekStart(new Date()));

  useEffect(() => {
    fetchSlots();
  }, [instructorId, weekStart]);

  function getWeekStart(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    d.setDate(diff);
    d.setHours(0, 0, 0, 0);
    return d;
  }

  function getWeekEnd(start: Date): Date {
    const end = new Date(start);
    end.setDate(end.getDate() + 6);
    return end;
  }

  const fetchSlots = async () => {
    try {
      setLoading(true);
      const startDate = weekStart.toISOString().split('T')[0];
      const endDate = getWeekEnd(weekStart).toISOString().split('T')[0];

      const response = await api.get(
        `/calendar/public/${instructorId}?start_date=${startDate}&end_date=${endDate}`
      );

      // Filter only available slots
      const availableSlots = (response.data.booking_slots || []).filter(
        (slot: Slot) => slot.status === 'available'
      );
      setSlots(availableSlots);
    } catch (error) {
      console.error('Error fetching slots:', error);
      setSlots([]);
    } finally {
      setLoading(false);
    }
  };

  const goToPreviousWeek = () => {
    const newStart = new Date(weekStart);
    newStart.setDate(newStart.getDate() - 7);
    if (newStart >= getWeekStart(new Date())) {
      setWeekStart(newStart);
    }
  };

  const goToNextWeek = () => {
    const newStart = new Date(weekStart);
    newStart.setDate(newStart.getDate() + 7);
    setWeekStart(newStart);
  };

  const getDaysOfWeek = () => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(weekStart);
      day.setDate(day.getDate() + i);
      days.push(day);
    }
    return days;
  };

  const getSlotsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return slots.filter((slot) => slot.start_at.startsWith(dateStr));
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatDateHeader = (date: Date) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const compareDate = new Date(date);
    compareDate.setHours(0, 0, 0, 0);

    if (compareDate.getTime() === today.getTime()) {
      return 'Today';
    }

    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (compareDate.getTime() === tomorrow.getTime()) {
      return 'Tomorrow';
    }

    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  const isPastDate = (date: Date) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const compareDate = new Date(date);
    compareDate.setHours(0, 0, 0, 0);
    return compareDate < today;
  };

  const canGoPrevious = () => {
    const currentWeekStart = getWeekStart(new Date());
    return weekStart > currentWeekStart;
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-primary-50 to-blue-50 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar size={20} className="text-primary-600" />
            <h3 className="font-semibold text-gray-900">Select a Time Slot</h3>
          </div>

          {/* Week Navigation */}
          <div className="flex items-center gap-2">
            <button
              onClick={goToPreviousWeek}
              disabled={!canGoPrevious()}
              className={`p-2 rounded-lg transition-colors ${
                canGoPrevious()
                  ? 'hover:bg-white/80 text-gray-600'
                  : 'text-gray-300 cursor-not-allowed'
              }`}
            >
              <ChevronLeft size={20} />
            </button>
            <span className="text-sm font-medium text-gray-700 min-w-[150px] text-center">
              {weekStart.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              })}{' '}
              -{' '}
              {getWeekEnd(weekStart).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              })}
            </span>
            <button
              onClick={goToNextWeek}
              className="p-2 rounded-lg hover:bg-white/80 transition-colors text-gray-600"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Slots Grid */}
      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 size={32} className="animate-spin text-primary-500" />
          </div>
        ) : (
          <div className="grid grid-cols-7 gap-2">
            {getDaysOfWeek().map((day) => {
              const daySlots = getSlotsForDate(day);
              const isPast = isPastDate(day);

              return (
                <div key={day.toISOString()} className="min-h-[200px]">
                  {/* Day Header */}
                  <div
                    className={`text-center p-2 rounded-lg mb-2 ${
                      isPast ? 'bg-gray-50 text-gray-400' : 'bg-gray-100'
                    }`}
                  >
                    <span className="text-xs font-medium">
                      {formatDateHeader(day)}
                    </span>
                  </div>

                  {/* Slots */}
                  <div className="space-y-1">
                    {daySlots.length === 0 ? (
                      <p className="text-xs text-gray-400 text-center py-4">
                        No slots
                      </p>
                    ) : (
                      daySlots.map((slot) => (
                        <button
                          key={slot.id}
                          onClick={() => onSlotSelect(slot)}
                          className={`
                            w-full p-2 rounded-lg text-xs font-medium
                            transition-all duration-200
                            ${
                              selectedSlotId === slot.id
                                ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                                : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
                            }
                          `}
                        >
                          <Clock size={12} className="inline mr-1" />
                          {formatTime(slot.start_at)}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SlotSelector;
