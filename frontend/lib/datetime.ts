/**
 * DateTime Utilities
 *
 * Provides timezone-aware date/time formatting for the application.
 *
 * Architecture:
 * - Backend stores all times in UTC (best practice for databases)
 * - Backend returns UTC datetime + timezone string (e.g., "Asia/Kolkata")
 * - Frontend converts to the session's timezone for display
 *
 * This ensures consistent time display regardless of user's browser timezone,
 * showing times in the timezone the session was booked in.
 */

/**
 * Format a UTC datetime string to the specified timezone.
 *
 * @param utcDateString - ISO datetime string in UTC (from backend)
 * @param timezone - IANA timezone string (e.g., "Asia/Kolkata", "America/New_York")
 * @param options - Intl.DateTimeFormat options
 * @returns Formatted date/time string in the specified timezone
 */
export function formatInTimezone(
  utcDateString: string,
  timezone: string,
  options: Intl.DateTimeFormatOptions = {}
): string {
  const date = new Date(utcDateString);

  // Default options for time display
  const defaultOptions: Intl.DateTimeFormatOptions = {
    timeZone: timezone,
    ...options,
  };

  return date.toLocaleString('en-US', defaultOptions);
}

/**
 * Format time in specified timezone (e.g., "6:08 PM")
 */
export function formatTimeInTimezone(
  utcDateString: string,
  timezone: string
): string {
  return formatInTimezone(utcDateString, timezone, {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

/**
 * Format date in specified timezone (e.g., "Fri, Dec 19")
 */
export function formatDateInTimezone(
  utcDateString: string,
  timezone: string
): string {
  return formatInTimezone(utcDateString, timezone, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Check if a date is today in the specified timezone
 */
export function isTodayInTimezone(utcDateString: string, timezone: string): boolean {
  const date = new Date(utcDateString);
  const now = new Date();

  // Get date parts in the target timezone
  const dateStr = date.toLocaleDateString('en-US', { timeZone: timezone });
  const todayStr = now.toLocaleDateString('en-US', { timeZone: timezone });

  return dateStr === todayStr;
}

/**
 * Check if a date is tomorrow in the specified timezone
 */
export function isTomorrowInTimezone(utcDateString: string, timezone: string): boolean {
  const date = new Date(utcDateString);
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  // Get date parts in the target timezone
  const dateStr = date.toLocaleDateString('en-US', { timeZone: timezone });
  const tomorrowStr = tomorrow.toLocaleDateString('en-US', { timeZone: timezone });

  return dateStr === tomorrowStr;
}

/**
 * Format session datetime with smart day labels (Today, Tomorrow, or date)
 *
 * @param utcDateString - ISO datetime string in UTC
 * @param timezone - IANA timezone string
 * @returns Object with formatted day text, time text, and flags
 */
export function formatSessionDateTime(
  utcDateString: string,
  timezone: string
): {
  dayText: string;
  timeText: string;
  isToday: boolean;
  isTomorrow: boolean;
} {
  const isToday = isTodayInTimezone(utcDateString, timezone);
  const isTomorrow = isTomorrowInTimezone(utcDateString, timezone);

  let dayText: string;
  if (isToday) {
    dayText = 'Today';
  } else if (isTomorrow) {
    dayText = 'Tomorrow';
  } else {
    dayText = formatDateInTimezone(utcDateString, timezone);
  }

  const timeText = formatTimeInTimezone(utcDateString, timezone);

  return { dayText, timeText, isToday, isTomorrow };
}

/**
 * Get the user's browser timezone
 */
export function getBrowserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Common timezone mappings for display
 */
export const TIMEZONE_DISPLAY_NAMES: Record<string, string> = {
  'Asia/Kolkata': 'IST',
  'America/New_York': 'EST',
  'America/Los_Angeles': 'PST',
  'Europe/London': 'GMT',
  'UTC': 'UTC',
};

/**
 * Get short display name for a timezone (e.g., "IST" for "Asia/Kolkata")
 */
export function getTimezoneDisplayName(timezone: string): string {
  return TIMEZONE_DISPLAY_NAMES[timezone] || timezone;
}
