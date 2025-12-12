/**
 * Interactive Calendar Grid Component
 * Displays weekly calendar with click-to-add, click-to-delete, and resize functionality
 * Uses absolute positioning for slots to properly display multi-hour events
 */

import React, { useState, useRef, useEffect } from 'react';
import { X, Clock, Check, Trash2 } from 'lucide-react';
import type { CalendarDay, CalendarSlot } from '../../types/api';
import { formatTime, getSlotStatusColor, isSlotInPast } from '../../services/calendarAPI';

// Constants for grid layout
const HOUR_HEIGHT = 60; // pixels per hour
const START_HOUR = 6; // 6 AM
const END_HOUR = 22; // 10 PM
const TOTAL_HOURS = END_HOUR - START_HOUR;

// Allowed slot durations in minutes (session patterns: 25+5, 50+10, 80+10, etc.)
// These represent typical tutoring session lengths
const ALLOWED_DURATIONS = [
  25,   // Short session
  30,   // Short session + break
  50,   // Standard session
  60,   // Standard session + break (1 hour)
  80,   // Long session
  90,   // Long session + break (1.5 hours)
  110,  // Extended session
  120,  // Extended session + break (2 hours)
  150,  // Double session (2.5 hours)
  180,  // Double session + break (3 hours)
  240,  // Half day (4 hours)
];

// Snap a duration to the nearest allowed value
const snapToAllowedDuration = (durationMins: number): number => {
  if (durationMins <= ALLOWED_DURATIONS[0]) {
    return ALLOWED_DURATIONS[0];
  }
  if (durationMins >= ALLOWED_DURATIONS[ALLOWED_DURATIONS.length - 1]) {
    return ALLOWED_DURATIONS[ALLOWED_DURATIONS.length - 1];
  }

  // Find the closest allowed duration
  let closest = ALLOWED_DURATIONS[0];
  let minDiff = Math.abs(durationMins - closest);

  for (const allowed of ALLOWED_DURATIONS) {
    const diff = Math.abs(durationMins - allowed);
    if (diff < minDiff) {
      minDiff = diff;
      closest = allowed;
    }
  }

  return closest;
};

interface CalendarGridProps {
  days: CalendarDay[];
  onSlotClick?: (day: CalendarDay, slot: CalendarSlot) => void;
  onAddAvailability?: (data: {
    specific_date: string;
    start_time: string;
    end_time: string;
    slot_duration_minutes: number;
    break_minutes: number;
  }) => Promise<void>;
  onDeleteAvailability?: (availabilityId: number) => Promise<void>;
  onDeleteSlot?: (slotId: number) => Promise<void>;
  onUpdateSlot?: (slotId: number, data: { start_at?: string; end_at?: string }) => Promise<void>;
  isLoading?: boolean;
}

interface SelectionState {
  isSelecting: boolean;
  startDay: string | null;
  startHour: number | null;
  endHour: number | null;
}

interface PopoverState {
  isOpen: boolean;
  type: 'add' | 'delete';
  date: string;
  startHour: number;
  endHour: number;
  position: { top: number; left: number };
  availabilityId?: number;
  slotId?: number;
  slotInfo?: CalendarSlot;
}

interface ResizeState {
  isResizing: boolean;
  slot: CalendarSlot | null;
  slotDate: string | null;
  edge: 'top' | 'bottom' | null;
  startY: number;
  currentY: number;
  originalStart: Date | null;
  originalEnd: Date | null;
}

export const CalendarGrid: React.FC<CalendarGridProps> = ({
  days,
  onSlotClick,
  onAddAvailability,
  onDeleteAvailability,
  onDeleteSlot,
  onUpdateSlot,
  isLoading = false,
}) => {
  // Selection state for drag-to-add functionality
  const [selection, setSelection] = useState<SelectionState>({
    isSelecting: false,
    startDay: null,
    startHour: null,
    endHour: null,
  });

  // Popover state for slot configuration/deletion
  const [popover, setPopover] = useState<PopoverState>({
    isOpen: false,
    type: 'add',
    date: '',
    startHour: 0,
    endHour: 0,
    position: { top: 0, left: 0 },
  });

  // Resize state for individual slots
  const [resize, setResize] = useState<ResizeState>({
    isResizing: false,
    slot: null,
    slotDate: null,
    edge: null,
    startY: 0,
    currentY: 0,
    originalStart: null,
    originalEnd: null,
  });

  // Form state
  const [slotDuration, setSlotDuration] = useState(50);
  const [breakDuration, setBreakDuration] = useState(10);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const gridRef = useRef<HTMLDivElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<ResizeState>(resize);

  // Generate time slots from 6 AM to 10 PM
  const timeSlots = Array.from({ length: TOTAL_HOURS }, (_, i) => {
    const hour = i + START_HOUR;
    return `${hour.toString().padStart(2, '0')}:00`;
  });

  // Helper to parse time from ISO string without timezone issues
  const parseTimeFromISO = (iso: string): { hours: number; mins: number } => {
    const timePart = iso.split('T')[1];
    const [h, m] = timePart.split(':').map(Number);
    return { hours: h, mins: m };
  };

  // Calculate slot position (top) based on start time
  const getSlotTop = (slot: CalendarSlot): number => {
    const { hours, mins } = parseTimeFromISO(slot.start_at);
    const minutesFromStart = (hours - START_HOUR) * 60 + mins;
    return (minutesFromStart / 60) * HOUR_HEIGHT;
  };

  // Calculate slot height based on duration
  const getSlotHeight = (slot: CalendarSlot): number => {
    const start = parseTimeFromISO(slot.start_at);
    const end = parseTimeFromISO(slot.end_at);
    const durationMins = (end.hours * 60 + end.mins) - (start.hours * 60 + start.mins);
    return (durationMins / 60) * HOUR_HEIGHT;
  };

  // Get preview position and height during resize with duration snapping
  const getResizePreviewStyle = (slot: CalendarSlot): { top: number; height: number; display: string; snappedDuration: number; originalDuration: number } | null => {
    if (!resize.isResizing || resize.slot?.slot_id !== slot.slot_id) return null;

    const pixelDelta = resize.currentY - resize.startY;
    const minutesDelta = Math.round(pixelDelta); // 1px ≈ 1 minute

    const start = parseTimeFromISO(slot.start_at);
    const end = parseTimeFromISO(slot.end_at);

    const originalStartMins = start.hours * 60 + start.mins;
    const originalEndMins = end.hours * 60 + end.mins;
    const originalDuration = originalEndMins - originalStartMins;

    // Calculate raw new duration based on resize
    let rawNewDuration = originalDuration;
    if (resize.edge === 'top') {
      rawNewDuration = originalDuration - minutesDelta;
    } else if (resize.edge === 'bottom') {
      rawNewDuration = originalDuration + minutesDelta;
    }

    // Snap to allowed duration
    const snappedDuration = snapToAllowedDuration(rawNewDuration);

    // Calculate new start/end based on snapped duration
    let newStartMins = originalStartMins;
    let newEndMins = originalEndMins;

    if (resize.edge === 'top') {
      // When resizing from top, end stays fixed, start moves
      newStartMins = originalEndMins - snappedDuration;
      // Clamp to grid bounds
      if (newStartMins < START_HOUR * 60) {
        newStartMins = START_HOUR * 60;
        // Recalculate duration if clamped
      }
    } else if (resize.edge === 'bottom') {
      // When resizing from bottom, start stays fixed, end moves
      newEndMins = originalStartMins + snappedDuration;
      // Clamp to grid bounds
      if (newEndMins > END_HOUR * 60) {
        newEndMins = END_HOUR * 60;
      }
    }

    const newTop = ((newStartMins - START_HOUR * 60) / 60) * HOUR_HEIGHT;
    const newHeight = (snappedDuration / 60) * HOUR_HEIGHT;

    const formatTimePreview = (totalMins: number): string => {
      const hours = Math.floor(totalMins / 60);
      const mins = totalMins % 60;
      const period = hours >= 12 ? 'PM' : 'AM';
      const displayHours = hours % 12 || 12;
      return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
    };

    return {
      top: Math.max(0, newTop),
      height: Math.max(ALLOWED_DURATIONS[0] / 60 * HOUR_HEIGHT, newHeight),
      display: `${formatTimePreview(newStartMins)} - ${formatTimePreview(newEndMins)}`,
      snappedDuration,
      originalDuration,
    };
  };

  const formatDayHeader = (dateStr: string): { dayName: string; dayNum: string; isToday: boolean } => {
    const date = new Date(dateStr);
    const today = new Date();
    const isToday =
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear();

    return {
      dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
      dayNum: date.getDate().toString(),
      isToday,
    };
  };

  const getSlotDisplay = (slot: CalendarSlot): string => {
    const start = parseTimeFromISO(slot.start_at);
    const end = parseTimeFromISO(slot.end_at);
    const formatT = (h: number, m: number) => {
      const period = h >= 12 ? 'PM' : 'AM';
      const dh = h % 12 || 12;
      return `${dh}:${m.toString().padStart(2, '0')} ${period}`;
    };
    return `${formatT(start.hours, start.mins)} - ${formatT(end.hours, end.mins)}`;
  };

  // Check if a cell is in the current selection
  const isCellSelected = (date: string, hour: number): boolean => {
    if (!selection.startDay || selection.startHour === null) return false;
    if (date !== selection.startDay) return false;

    const minHour = Math.min(selection.startHour, selection.endHour ?? selection.startHour);
    const maxHour = Math.max(selection.startHour, selection.endHour ?? selection.startHour);

    return hour >= minHour && hour <= maxHour;
  };

  // Check if date is in the past
  const isDateInPast = (dateStr: string): boolean => {
    const date = new Date(dateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    date.setHours(0, 0, 0, 0);
    return date < today;
  };

  // Handle mouse down on a cell (start selection for adding)
  const handleMouseDown = (date: string, hour: number, e: React.MouseEvent) => {
    if (isDateInPast(date)) return;
    if ((e.target as HTMLElement).closest('.slot-container')) return;

    setSelection({
      isSelecting: true,
      startDay: date,
      startHour: hour,
      endHour: hour,
    });
  };

  // Handle mouse enter on a cell (extend selection)
  const handleMouseEnter = (date: string, hour: number) => {
    if (!selection.isSelecting) return;
    if (date !== selection.startDay) return;

    setSelection((prev) => ({
      ...prev,
      endHour: hour,
    }));
  };

  // Handle mouse up (end selection and show popover)
  const handleMouseUp = (e: React.MouseEvent) => {
    if (!selection.isSelecting || !selection.startDay || selection.startHour === null) {
      setSelection({ isSelecting: false, startDay: null, startHour: null, endHour: null });
      return;
    }

    const minHour = Math.min(selection.startHour, selection.endHour ?? selection.startHour);
    const maxHour = Math.max(selection.startHour, selection.endHour ?? selection.startHour);

    const gridRect = gridRef.current?.getBoundingClientRect();
    if (gridRect) {
      const popoverLeft = Math.min(e.clientX - gridRect.left + 10, gridRect.width - 280);
      const popoverTop = Math.min(e.clientY - gridRect.top + 10, gridRect.height - 200);

      setPopover({
        isOpen: true,
        type: 'add',
        date: selection.startDay,
        startHour: minHour,
        endHour: maxHour + 1,
        position: { top: Math.max(0, popoverTop), left: Math.max(0, popoverLeft) },
      });
    }

    setSelection({ isSelecting: false, startDay: null, startHour: null, endHour: null });
  };

  // Handle slot click for deletion
  const handleSlotClick = (e: React.MouseEvent, day: CalendarDay, slot: CalendarSlot) => {
    e.stopPropagation();

    if (resize.isResizing) return;

    if (slot.status !== 'available') {
      onSlotClick?.(day, slot);
      return;
    }

    if (!slot.slot_id && !slot.availability_id) {
      onSlotClick?.(day, slot);
      return;
    }

    const gridRect = gridRef.current?.getBoundingClientRect();
    if (gridRect) {
      const popoverLeft = Math.min(e.clientX - gridRect.left + 10, gridRect.width - 280);
      const popoverTop = Math.min(e.clientY - gridRect.top + 10, gridRect.height - 200);

      setPopover({
        isOpen: true,
        type: 'delete',
        date: day.date,
        startHour: parseTimeFromISO(slot.start_at).hours,
        endHour: parseTimeFromISO(slot.end_at).hours,
        position: { top: Math.max(0, popoverTop), left: Math.max(0, popoverLeft) },
        availabilityId: slot.availability_id ?? undefined,
        slotId: slot.slot_id ?? undefined,
        slotInfo: slot,
      });
    }
  };

  // Handle resize start
  const handleResizeStart = (e: React.MouseEvent, slot: CalendarSlot, edge: 'top' | 'bottom', dayDate: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (!slot.slot_id || slot.status !== 'available') return;

    setResize({
      isResizing: true,
      slot,
      slotDate: dayDate,
      edge,
      startY: e.clientY,
      currentY: e.clientY,
      originalStart: new Date(slot.start_at),
      originalEnd: new Date(slot.end_at),
    });
  };

  // Keep ref in sync with state
  resizeRef.current = resize;

  // Handle resize move
  const handleResizeMove = (e: MouseEvent) => {
    if (!resizeRef.current.isResizing) return;
    setResize(prev => ({ ...prev, currentY: e.clientY }));
    resizeRef.current.currentY = e.clientY;
  };

  // Helper to add minutes to an ISO datetime string without timezone conversion
  const addMinutesToISOString = (isoString: string, minutes: number): string => {
    const hasZ = isoString.endsWith('Z');
    const cleanISO = hasZ ? isoString.slice(0, -1) : isoString;

    const [datePart, timePart] = cleanISO.split('T');
    const [year, month, day] = datePart.split('-').map(Number);
    const [hours, mins, secs = '00'] = timePart.split(':');
    const [seconds] = secs.split('.');

    const utcDate = new Date(Date.UTC(year, month - 1, day, Number(hours), Number(mins), Number(seconds)));
    utcDate.setUTCMinutes(utcDate.getUTCMinutes() + minutes);

    const pad = (n: number) => n.toString().padStart(2, '0');
    const newYear = utcDate.getUTCFullYear();
    const newMonth = pad(utcDate.getUTCMonth() + 1);
    const newDay = pad(utcDate.getUTCDate());
    const newHours = pad(utcDate.getUTCHours());
    const newMins = pad(utcDate.getUTCMinutes());
    const newSecs = pad(utcDate.getUTCSeconds());

    return `${newYear}-${newMonth}-${newDay}T${newHours}:${newMins}:${newSecs}${hasZ ? 'Z' : ''}`;
  };

  // Handle resize end with duration snapping
  const handleResizeEnd = async () => {
    const r = resizeRef.current;
    if (!r.isResizing || !r.slot || !r.originalStart || !r.originalEnd) {
      setResize({ isResizing: false, slot: null, slotDate: null, edge: null, startY: 0, currentY: 0, originalStart: null, originalEnd: null });
      return;
    }

    const slotId = r.slot.slot_id;
    if (!slotId || !onUpdateSlot) {
      setResize({ isResizing: false, slot: null, slotDate: null, edge: null, startY: 0, currentY: 0, originalStart: null, originalEnd: null });
      return;
    }

    const pixelDelta = r.currentY - r.startY;
    const minutesDelta = Math.round(pixelDelta);

    // Need at least some movement to trigger resize
    if (Math.abs(minutesDelta) < 5) {
      setResize({ isResizing: false, slot: null, slotDate: null, edge: null, startY: 0, currentY: 0, originalStart: null, originalEnd: null });
      return;
    }

    const originalStartISO = r.slot.start_at;
    const originalEndISO = r.slot.end_at;

    const parseTimeMinutes = (iso: string): number => {
      const timePart = iso.split('T')[1];
      const [h, m] = timePart.split(':').map(Number);
      return h * 60 + m;
    };

    const originalStartMins = parseTimeMinutes(originalStartISO);
    const originalEndMins = parseTimeMinutes(originalEndISO);
    const originalDuration = originalEndMins - originalStartMins;

    // Calculate raw new duration based on resize direction
    let rawNewDuration = originalDuration;
    if (r.edge === 'top') {
      rawNewDuration = originalDuration - minutesDelta;
    } else if (r.edge === 'bottom') {
      rawNewDuration = originalDuration + minutesDelta;
    }

    // Snap to allowed duration
    const snappedDuration = snapToAllowedDuration(rawNewDuration);

    // If snapped duration equals original, no change needed
    if (snappedDuration === originalDuration) {
      setResize({ isResizing: false, slot: null, slotDate: null, edge: null, startY: 0, currentY: 0, originalStart: null, originalEnd: null });
      return;
    }

    // Calculate the difference between original and snapped duration
    const durationDiff = snappedDuration - originalDuration;

    let newStartISO = originalStartISO;
    let newEndISO = originalEndISO;

    if (r.edge === 'top') {
      // When resizing from top, end stays fixed, start moves
      // Negative durationDiff means shorter duration, so start moves later (positive minutes)
      newStartISO = addMinutesToISOString(originalStartISO, -durationDiff);
    } else if (r.edge === 'bottom') {
      // When resizing from bottom, start stays fixed, end moves
      newEndISO = addMinutesToISOString(originalEndISO, durationDiff);
    }

    setResize({ isResizing: false, slot: null, slotDate: null, edge: null, startY: 0, currentY: 0, originalStart: null, originalEnd: null });

    try {
      await onUpdateSlot(slotId, {
        start_at: newStartISO,
        end_at: newEndISO,
      });
    } catch (error) {
      console.error('Failed to resize slot:', error);
    }
  };

  // Add global mouse event listeners for resize
  useEffect(() => {
    if (resize.isResizing) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleResizeMove);
      window.removeEventListener('mouseup', handleResizeEnd);
    };
  }, [resize.isResizing]);

  // Handle click outside popover
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setPopover((prev) => ({ ...prev, isOpen: false }));
      }
    };

    if (popover.isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [popover.isOpen]);

  // Handle add availability submission
  const handleSubmitAdd = async () => {
    if (!onAddAvailability) return;

    setIsSubmitting(true);
    try {
      await onAddAvailability({
        specific_date: popover.date,
        start_time: `${popover.startHour.toString().padStart(2, '0')}:00`,
        end_time: `${popover.endHour.toString().padStart(2, '0')}:00`,
        slot_duration_minutes: slotDuration,
        break_minutes: breakDuration,
      });
      setPopover((prev) => ({ ...prev, isOpen: false }));
    } catch (error) {
      console.error('Failed to add availability:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    setIsSubmitting(true);
    try {
      if (popover.slotId && onDeleteSlot) {
        await onDeleteSlot(popover.slotId);
      } else if (popover.availabilityId && onDeleteAvailability) {
        await onDeleteAvailability(popover.availabilityId);
      }
      setPopover((prev) => ({ ...prev, isOpen: false }));
    } catch (error) {
      console.error('Failed to delete:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatHour = (hour: number): string => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    return `${displayHour}:00 ${period}`;
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="animate-pulse">
          <div className="grid grid-cols-8 border-b border-gray-200">
            <div className="p-3 bg-gray-50"></div>
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="p-3 text-center border-l border-gray-200">
                <div className="h-4 bg-gray-200 rounded w-12 mx-auto mb-2"></div>
                <div className="h-8 w-8 bg-gray-200 rounded-full mx-auto"></div>
              </div>
            ))}
          </div>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="grid grid-cols-8 border-b border-gray-100">
              <div className="p-2 bg-gray-50"></div>
              {Array.from({ length: 7 }).map((_, j) => (
                <div key={j} className="p-2 border-l border-gray-100 h-16"></div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden relative" ref={gridRef}>
      {/* CSS Animations */}
      <style>{`
        @keyframes fadeInScale {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        @keyframes resizePulse {
          0%, 100% { box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.5); }
          50% { box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.3); }
        }
        .resizing-slot {
          animation: resizePulse 0.5s ease-in-out infinite;
        }
      `}</style>

      {/* Header Row - Days */}
      <div className="grid grid-cols-8 border-b border-gray-200 sticky top-0 bg-white z-20">
        <div className="p-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase">Time</div>
        {days.map((day) => {
          const { dayName, dayNum, isToday } = formatDayHeader(day.date);
          const isPast = isDateInPast(day.date);
          return (
            <div
              key={day.date}
              className={`p-3 text-center border-l border-gray-200 ${
                isToday ? 'bg-blue-50' : isPast ? 'bg-gray-50' : ''
              }`}
            >
              <div className={`text-xs font-medium uppercase mb-1 ${isPast ? 'text-gray-400' : 'text-gray-500'}`}>
                {dayName}
              </div>
              <div
                className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold ${
                  isToday ? 'bg-blue-600 text-white' : isPast ? 'text-gray-400' : 'text-gray-900'
                }`}
              >
                {dayNum}
              </div>
            </div>
          );
        })}
      </div>

      {/* Time Grid with Absolute Positioned Slots */}
      <div
        className="max-h-[600px] overflow-y-auto select-none"
        onMouseUp={handleMouseUp}
        onMouseLeave={() => {
          if (selection.isSelecting) {
            setSelection({ isSelecting: false, startDay: null, startHour: null, endHour: null });
          }
        }}
      >
        <div className="grid grid-cols-8" style={{ height: `${TOTAL_HOURS * HOUR_HEIGHT}px` }}>
          {/* Time labels column */}
          <div className="bg-gray-50 relative">
            {timeSlots.map((timeSlot, idx) => (
              <div
                key={timeSlot}
                className="absolute left-0 right-0 p-2 text-xs text-gray-500 font-medium border-b border-gray-100"
                style={{ top: `${idx * HOUR_HEIGHT}px`, height: `${HOUR_HEIGHT}px` }}
              >
                {formatTime(timeSlot)}
              </div>
            ))}
          </div>

          {/* Day columns with slots */}
          {days.map((day) => {
            const { isToday } = formatDayHeader(day.date);
            const isPast = isDateInPast(day.date);

            return (
              <div
                key={day.date}
                className={`border-l border-gray-200 relative ${isToday ? 'bg-blue-50/30' : ''} ${isPast ? 'bg-gray-50/50' : ''}`}
              >
                {/* Hour grid lines (clickable for adding) */}
                {timeSlots.map((timeSlot, idx) => {
                  const hour = parseInt(timeSlot.split(':')[0]);
                  const isSelected = isCellSelected(day.date, hour);
                  return (
                    <div
                      key={timeSlot}
                      className={`absolute left-0 right-0 border-b border-gray-100 transition-colors ${
                        isPast ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-blue-50/50'
                      } ${isSelected ? 'bg-blue-100 ring-2 ring-blue-400 ring-inset' : ''}`}
                      style={{ top: `${idx * HOUR_HEIGHT}px`, height: `${HOUR_HEIGHT}px` }}
                      onMouseDown={(e) => handleMouseDown(day.date, hour, e)}
                      onMouseEnter={() => handleMouseEnter(day.date, hour)}
                    >
                      {!isPast && (
                        <div className="w-full h-full flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                          <span className="text-xs text-gray-400">+ Add</span>
                        </div>
                      )}
                    </div>
                  );
                })}

                {/* Absolutely positioned slots */}
                {day.slots.map((slot, idx) => {
                  const slotIsPast = isSlotInPast(slot.start_at);
                  const isAvailable = slot.status === 'available';
                  const isIndividualSlot = slot.slot_id !== null;
                  const canResize = isIndividualSlot && isAvailable && !slotIsPast && onUpdateSlot;
                  const resizePreview = getResizePreviewStyle(slot);
                  const isBeingResized = resizePreview !== null;

                  // Use preview values during resize, otherwise calculate from slot
                  const top = isBeingResized ? resizePreview.top : getSlotTop(slot);
                  const height = isBeingResized ? resizePreview.height : getSlotHeight(slot);
                  const displayText = isBeingResized ? resizePreview.display : getSlotDisplay(slot);

                  return (
                    <div
                      key={`${slot.slot_id || slot.availability_id}-${idx}`}
                      className={`slot-container absolute left-1 right-1 group ${isBeingResized ? 'resizing-slot z-30' : 'z-10'}`}
                      style={{
                        top: `${top}px`,
                        height: `${height}px`,
                        minHeight: '20px',
                      }}
                    >
                      {/* Top resize handle */}
                      {canResize && (
                        <div
                          className={`absolute top-0 left-0 right-0 h-3 cursor-ns-resize z-20 transition-opacity ${
                            isBeingResized ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                          }`}
                          onMouseDown={(e) => handleResizeStart(e, slot, 'top', day.date)}
                        >
                          <div className={`w-10 h-1.5 rounded mx-auto mt-0.5 ${
                            isBeingResized && resize.edge === 'top' ? 'bg-green-600' : 'bg-green-500'
                          }`} />
                        </div>
                      )}

                      {/* Slot content */}
                      <button
                        onClick={(e) => handleSlotClick(e, day, slot)}
                        disabled={slotIsPast}
                        className={`
                          w-full h-full rounded text-xs font-medium border transition-all overflow-hidden
                          flex flex-col justify-center px-2
                          ${isBeingResized ? 'bg-green-200 border-green-500 text-green-900 ring-2 ring-green-400' : getSlotStatusColor(slot.status)}
                          ${slotIsPast ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md cursor-pointer'}
                          ${isAvailable && !slotIsPast && !isBeingResized ? 'hover:border-green-500 group-hover:shadow-lg' : ''}
                        `}
                      >
                        <div className={`truncate ${isBeingResized ? 'font-semibold text-green-700' : ''}`}>
                          {displayText}
                        </div>
                        {height > 35 && (
                          <div className="text-[10px] opacity-75 capitalize flex items-center justify-between mt-0.5">
                            <span>
                              {isBeingResized ? (
                                <span className="text-green-600 font-medium">
                                  {resizePreview.snappedDuration} min
                                </span>
                              ) : (
                                <>
                                  {slot.status}
                                  {isIndividualSlot && <span className="ml-1 text-green-600">•</span>}
                                </>
                              )}
                            </span>
                            {isAvailable && !slotIsPast && !isBeingResized && (
                              <Trash2 className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-red-500" />
                            )}
                          </div>
                        )}
                      </button>

                      {/* Bottom resize handle */}
                      {canResize && (
                        <div
                          className={`absolute bottom-0 left-0 right-0 h-3 cursor-ns-resize z-20 transition-opacity ${
                            isBeingResized ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                          }`}
                          onMouseDown={(e) => handleResizeStart(e, slot, 'bottom', day.date)}
                        >
                          <div className={`w-10 h-1.5 rounded mx-auto mb-0.5 ${
                            isBeingResized && resize.edge === 'bottom' ? 'bg-green-600' : 'bg-green-500'
                          }`} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>

      {/* Popover for Add/Delete */}
      {popover.isOpen && (
        <div
          ref={popoverRef}
          className="absolute z-50 bg-white rounded-xl shadow-2xl border border-gray-200 p-4 w-72"
          style={{
            top: popover.position.top,
            left: popover.position.left,
            animation: 'fadeInScale 0.2s ease-out',
          }}
        >
          {popover.type === 'add' ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-600" />
                  Add Availability
                </h4>
                <button
                  onClick={() => setPopover((prev) => ({ ...prev, isOpen: false }))}
                  className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="h-4 w-4 text-gray-400" />
                </button>
              </div>

              <div className="bg-blue-50 rounded-lg p-3 mb-4">
                <div className="text-sm font-medium text-blue-900">
                  {new Date(popover.date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'short',
                    day: 'numeric',
                  })}
                </div>
                <div className="text-lg font-semibold text-blue-700">
                  {formatHour(popover.startHour)} - {formatHour(popover.endHour)}
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Session Duration</label>
                  <select
                    value={slotDuration}
                    onChange={(e) => setSlotDuration(parseInt(e.target.value))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={25}>25 minutes</option>
                    <option value={50}>50 minutes</option>
                    <option value={80}>80 minutes</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Break Between Sessions</label>
                  <select
                    value={breakDuration}
                    onChange={(e) => setBreakDuration(parseInt(e.target.value))}
                    className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={0}>No break</option>
                    <option value={5}>5 minutes</option>
                    <option value={10}>10 minutes</option>
                    <option value={15}>15 minutes</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => setPopover((prev) => ({ ...prev, isOpen: false }))}
                  className="flex-1 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitAdd}
                  disabled={isSubmitting}
                  className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Adding...
                    </>
                  ) : (
                    <>
                      <Check className="h-4 w-4" />
                      Add Slots
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Trash2 className="h-4 w-4 text-red-600" />
                  Delete Availability
                </h4>
                <button
                  onClick={() => setPopover((prev) => ({ ...prev, isOpen: false }))}
                  className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="h-4 w-4 text-gray-400" />
                </button>
              </div>

              <div className="bg-red-50 rounded-lg p-3 mb-4">
                <div className="text-sm font-medium text-red-900">
                  {new Date(popover.date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'short',
                    day: 'numeric',
                  })}
                </div>
                <div className="text-lg font-semibold text-red-700">
                  {popover.slotInfo && getSlotDisplay(popover.slotInfo)}
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">
                {popover.slotId
                  ? 'Are you sure you want to delete this individual time slot?'
                  : 'Are you sure you want to delete this availability slot? This will remove all slots generated from this availability rule.'}
              </p>

              <div className="flex gap-2">
                <button
                  onClick={() => setPopover((prev) => ({ ...prev, isOpen: false }))}
                  className="flex-1 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isSubmitting}
                  className="flex-1 px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4" />
                      Delete
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="p-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-green-100 border border-green-300"></div>
            <span className="text-gray-600">Available (click to delete)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-blue-100 border border-blue-300"></div>
            <span className="text-gray-600">Booked</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-gray-100 border border-gray-300"></div>
            <span className="text-gray-600">Blocked</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-green-600 font-bold">•</span>
            <span className="text-gray-600">Individual slot (resizable)</span>
          </div>
        </div>
        <div className="text-gray-400 italic">Click & drag to add availability</div>
      </div>
    </div>
  );
};

export default CalendarGrid;
