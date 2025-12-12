/**
 * API Services Barrel Export
 *
 * Centralized export for all API services
 */

export { authAPI } from './authAPI';
export { instructorAPI } from './instructorAPI';
export { uploadAPI } from './uploadAPI';
export { calendarAPI } from './calendarAPI';
export { TokenManager, formatAPIError } from '../lib/axios';
export type { FormattedError } from '../lib/axios';

// Calendar utilities
export {
  getDayName,
  getShortDayName,
  formatTime,
  formatDate,
  formatDateTime,
  getWeekStart,
  getWeekEnd,
  toDateString,
  toISOString,
  getWeekDates,
  isSlotInPast,
  getSlotStatusColor,
} from './calendarAPI';
