/**
 * API Services Barrel Export
 *
 * Centralized export for all API services
 */

export { authAPI } from './authAPI';
export { instructorAPI } from './instructorAPI';
export { uploadAPI } from './uploadAPI';
export { calendarAPI } from './calendarAPI';
export { messagingAPI } from './messagingAPI';
export { subjectsAPI } from './subjectsAPI';
export { adminAPI } from './adminAPI';
export { studentAPI } from './studentAPI';
export type { Subject, SubjectListResponse } from './subjectsAPI';
export type {
  UpcomingSession,
  StudentStats,
  MyInstructor,
  SessionHistory,
  PaymentHistory,
  StudentDashboardResponse,
} from './studentAPI';
export type {
  AdminDashboardStats,
  AdminUser,
  AdminInstructorProfile,
  PendingInstructor,
  ActionResponse,
} from './adminAPI';
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
