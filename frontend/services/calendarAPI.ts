/**
 * Calendar API Service
 *
 * All calendar and scheduling-related API calls:
 * - Availability management (recurring & one-time)
 * - Time off management
 * - Calendar view
 */

import apiClient from '../lib/axios';
import type {
  SetRecurringAvailabilityRequest,
  SetOneTimeAvailabilityRequest,
  UpdateAvailabilityRequest,
  UpdateSlotRequest,
  Availability,
  AvailabilityListResponse,
  AddTimeOffRequest,
  TimeOff,
  TimeOffListResponse,
  CalendarViewResponse,
  CalendarMessageResponse,
  SlotResponse,
  AvailableBookingSlotsResponse,
} from '../types/api';

// ============================================================================
// Calendar API
// ============================================================================

export const calendarAPI = {
  // ==========================================================================
  // Availability Management
  // ==========================================================================

  /**
   * Set recurring weekly availability
   * Creates an availability slot that repeats every week on the same day
   */
  async setRecurringAvailability(data: SetRecurringAvailabilityRequest): Promise<Availability> {
    const response = await apiClient.post<Availability>(
      '/calendar/availability/recurring',
      data
    );
    return response.data;
  },

  /**
   * Set one-time availability for a specific date
   * Creates a one-time availability slot for a particular date
   */
  async setOneTimeAvailability(data: SetOneTimeAvailabilityRequest): Promise<Availability> {
    const response = await apiClient.post<Availability>(
      '/calendar/availability/one-time',
      data
    );
    return response.data;
  },

  /**
   * Get all availability slots for the current instructor
   */
  async getMyAvailability(): Promise<AvailabilityListResponse> {
    const response = await apiClient.get<AvailabilityListResponse>('/calendar/availability');
    return response.data;
  },

  /**
   * Delete an availability slot
   */
  async deleteAvailability(availabilityId: number): Promise<CalendarMessageResponse> {
    const response = await apiClient.delete<CalendarMessageResponse>(
      `/calendar/availability/${availabilityId}`
    );
    return response.data;
  },

  /**
   * Update an existing availability slot
   * Updates the time range for an availability (e.g., when resizing)
   */
  async updateAvailability(
    availabilityId: number,
    data: UpdateAvailabilityRequest
  ): Promise<CalendarMessageResponse> {
    const response = await apiClient.put<CalendarMessageResponse>(
      `/calendar/availability/${availabilityId}`,
      data
    );
    return response.data;
  },

  // ==========================================================================
  // Time Off Management
  // ==========================================================================

  /**
   * Add a time off period
   * Blocks time when the instructor is unavailable
   */
  async addTimeOff(data: AddTimeOffRequest): Promise<TimeOff> {
    const response = await apiClient.post<TimeOff>('/calendar/time-off', data);
    return response.data;
  },

  /**
   * Get all time off periods for the current instructor
   */
  async getMyTimeOff(): Promise<TimeOffListResponse> {
    const response = await apiClient.get<TimeOffListResponse>('/calendar/time-off');
    return response.data;
  },

  /**
   * Delete a time off period
   */
  async deleteTimeOff(timeOffId: number): Promise<CalendarMessageResponse> {
    const response = await apiClient.delete<CalendarMessageResponse>(
      `/calendar/time-off/${timeOffId}`
    );
    return response.data;
  },

  // ==========================================================================
  // Calendar View
  // ==========================================================================

  /**
   * Get calendar view for the current instructor
   * Returns merged availability, sessions, and time off for a date range
   */
  async getCalendarView(startDate: string, endDate: string): Promise<CalendarViewResponse> {
    const response = await apiClient.get<CalendarViewResponse>('/calendar/view', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  /**
   * Get public calendar view for an instructor
   * Used by students to see available slots for booking
   */
  async getPublicCalendarView(
    instructorId: number,
    startDate: string,
    endDate: string
  ): Promise<CalendarViewResponse> {
    const response = await apiClient.get<CalendarViewResponse>(
      `/calendar/view/public/${instructorId}`,
      {
        params: { start_date: startDate, end_date: endDate },
      }
    );
    return response.data;
  },

  /**
   * Get available booking slots for an instructor
   * Optimized for student booking flow - returns a flat list of available slots
   * This is the proper endpoint for booking functionality
   */
  async getAvailableBookingSlots(
    instructorId: number,
    startDate: string,
    endDate: string
  ): Promise<AvailableBookingSlotsResponse> {
    const response = await apiClient.get<AvailableBookingSlotsResponse>(
      `/calendar/booking-slots/${instructorId}`,
      {
        params: { start_date: startDate, end_date: endDate },
      }
    );
    return response.data;
  },

  // ==========================================================================
  // Individual Slot Management (for one-time availability)
  // ==========================================================================

  /**
   * Update (resize) an individual booking slot
   * Only works for one-time availability slots
   */
  async updateSlot(slotId: number, data: UpdateSlotRequest): Promise<SlotResponse> {
    const response = await apiClient.put<SlotResponse>(
      `/calendar/slots/${slotId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete an individual booking slot
   * Only works for one-time availability slots that are not booked
   */
  async deleteSlot(slotId: number): Promise<CalendarMessageResponse> {
    const response = await apiClient.delete<CalendarMessageResponse>(
      `/calendar/slots/${slotId}`
    );
    return response.data;
  },
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get day name from day number (0=Monday, 6=Sunday)
 */
export const getDayName = (dayNumber: number): string => {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return days[dayNumber] || '';
};

/**
 * Get short day name from day number
 */
export const getShortDayName = (dayNumber: number): string => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days[dayNumber] || '';
};

/**
 * Format time string (HH:MM) to readable format (e.g., "9:00 AM")
 */
export const formatTime = (time: string): string => {
  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

/**
 * Format ISO datetime to readable date string
 */
export const formatDate = (isoDate: string): string => {
  const date = new Date(isoDate);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format ISO datetime to readable datetime string
 */
export const formatDateTime = (isoDateTime: string): string => {
  const date = new Date(isoDateTime);
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
};

/**
 * Get start of week (Monday) for a given date
 */
export const getWeekStart = (date: Date): Date => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
  return new Date(d.setDate(diff));
};

/**
 * Get end of week (Sunday) for a given date
 */
export const getWeekEnd = (date: Date): Date => {
  const start = getWeekStart(date);
  return new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
};

/**
 * Format date to YYYY-MM-DD string
 */
export const toDateString = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

/**
 * Format date to ISO datetime string
 */
export const toISOString = (date: Date): string => {
  return date.toISOString();
};

/**
 * Get dates for a week starting from a given date
 */
export const getWeekDates = (startDate: Date): Date[] => {
  const dates: Date[] = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    dates.push(date);
  }
  return dates;
};

/**
 * Check if a slot is in the past
 */
export const isSlotInPast = (slotStart: string): boolean => {
  return new Date(slotStart) < new Date();
};

/**
 * Get slot status color class
 */
export const getSlotStatusColor = (status: string): string => {
  switch (status) {
    case 'available':
      return 'bg-green-100 border-green-300 text-green-800';
    case 'booked':
      return 'bg-blue-100 border-blue-300 text-blue-800';
    case 'blocked':
      return 'bg-gray-100 border-gray-300 text-gray-500';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-400';
  }
};
