/**
 * API Type Definitions
 *
 * These types match the backend API schemas exactly.
 * Generated from: tutorly-platform/backend/app/routers/
 */

// ============================================================================
// Enums
// ============================================================================

export enum UserRole {
  STUDENT = 'student',
  INSTRUCTOR = 'instructor',
  ADMIN = 'admin',
}

export enum UserStatus {
  PENDING_VERIFICATION = 'pending_verification',
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  BANNED = 'banned',
  DELETED = 'deleted',
}

export enum InstructorStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  SUSPENDED = 'suspended',
}

export enum ProficiencyLevel {
  NATIVE = 'native',
  FLUENT = 'fluent',
  ADVANCED = 'advanced',
  INTERMEDIATE = 'intermediate',
  BEGINNER = 'beginner',
}

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone_number?: string;
  email_verified: boolean;
  is_active: boolean;
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  phone_number?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface EmailVerificationRequest {
  token: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthUserResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MessageResponse {
  message: string;
}

// ============================================================================
// Instructor Types
// ============================================================================

export interface LanguageInput {
  language: string;
  proficiency: string;
}

export interface LanguageResponse {
  language: string;
  proficiency: string;
}

export interface SubjectInput {
  subject_id: number;
  proficiency_level: string;
}

export interface SubjectResponse {
  id: number;
  name: string;
  proficiency_level: string;
}

export interface EducationInput {
  institution: string;
  degree: string;
  field_of_study: string;
  start_year: number;
  end_year?: number;
  description?: string;
}

export interface EducationResponse {
  id: number;
  institution: string;
  degree: string;
  field_of_study: string;
  start_year: number;
  end_year?: number;
  description?: string;
}

export interface ExperienceInput {
  company: string;
  position: string;
  start_year: number;
  end_year?: number;
  description?: string;
  is_current: boolean;
}

export interface ExperienceResponse {
  id: number;
  company: string;
  position: string;
  start_year: number;
  end_year?: number;
  description?: string;
  is_current: boolean;
}

// Onboarding Step Requests
export interface OnboardingStep1Request {
  first_name: string;
  last_name: string;
  country: string;
  languages: LanguageInput[];
  phone_number?: string;
}

export interface OnboardingStep2Request {
  photo_url: string;
}

export interface OnboardingStep3Request {
  bio: string;
  headline: string;
  years_of_experience: number;
  teaching_style: string;  // Required - students need to know teaching methodology
}

export interface OnboardingStep4Request {
  video_url: string;
}

export interface OnboardingStep5Request {
  subjects: SubjectInput[];
}

export interface OnboardingStep6Request {
  hourly_rate: number;
  trial_lesson_price?: number;
}

export interface OnboardingStep7Request {
  education: EducationInput[];
  experience: ExperienceInput[];
  certifications: string[];
}

// Onboarding Step Responses
export interface OnboardingStep1Response {
  profile_id: number;
  onboarding_step: number;
}

export interface OnboardingStep2Response {
  profile_id: number;
  onboarding_step: number;
  photo_url: string;
}

export interface OnboardingStep3Response {
  profile_id: number;
  onboarding_step: number;
}

export interface OnboardingStep4Response {
  profile_id: number;
  onboarding_step: number;
  video_url: string;
}

export interface OnboardingStep5Response {
  profile_id: number;
  onboarding_step: number;
  subjects_count: number;
}

export interface OnboardingStep6Response {
  profile_id: number;
  onboarding_step: number;
  hourly_rate: number;
  trial_lesson_price?: number;
}

export interface OnboardingStep7Response {
  profile_id: number;
  onboarding_step: number;
  profile_status: InstructorStatus;
}

// Instructor Profile
export interface InstructorProfile {
  id: number;
  user_id: number;
  status: InstructorStatus;
  country_of_birth?: string;
  languages: LanguageResponse[];
  profile_photo_url?: string;
  bio?: string;
  teaching_experience?: string;
  headline?: string;
  intro_video_url?: string;
  hourly_rate?: number | string; // Can be string from Decimal serialization
  trial_lesson_price?: number | string; // Can be string from Decimal serialization
  onboarding_step: number;
  is_onboarding_complete: boolean;
  education: EducationResponse[];
  experience: ExperienceResponse[];
}

// Instructor Search
export interface InstructorSearchParams {
  subject_id?: number;
  min_price?: number;
  max_price?: number;
  languages?: string;
  min_experience?: number;
  skip?: number;
  limit?: number;
}

export interface InstructorSearchResponse {
  instructors: InstructorProfile[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface APIError {
  error_code: string;
  message: string;
}

export interface APIErrorResponse {
  detail: APIError | string;
}

// ============================================================================
// File Upload Types
// ============================================================================

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  file_url: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardStats {
  upcoming_sessions_count: number;
  total_students: number;
  completed_sessions: number;
  total_earnings: number;
  profile_completion_percent: number;
}

export interface UserBasicInfo {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

export interface UpcomingSession {
  id: number;
  student_name: string;
  scheduled_at: string;
  duration_minutes: number;
  subject: string;
  is_trial: boolean;
}

export interface InstructorDashboardResponse {
  profile: InstructorProfile;
  user: UserBasicInfo;
  stats: DashboardStats;
  upcoming_sessions: UpcomingSession[];
}

// ============================================================================
// Calendar & Scheduling Types
// ============================================================================

export enum DayOfWeek {
  MONDAY = 0,
  TUESDAY = 1,
  WEDNESDAY = 2,
  THURSDAY = 3,
  FRIDAY = 4,
  SATURDAY = 5,
  SUNDAY = 6,
}

export enum AvailabilityType {
  RECURRING = 'recurring',
  ONE_TIME = 'one_time',
}

export enum SlotStatus {
  AVAILABLE = 'available',
  BOOKED = 'booked',
  BLOCKED = 'blocked',
}

// Availability Types

export interface SetRecurringAvailabilityRequest {
  day_of_week: number; // 0=Monday, 6=Sunday
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  slot_duration_minutes?: number; // default 50
  break_minutes?: number; // default 10
}

export interface SetOneTimeAvailabilityRequest {
  specific_date: string; // YYYY-MM-DD format
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  slot_duration_minutes?: number; // default 50
  break_minutes?: number; // default 10
}

export interface UpdateAvailabilityRequest {
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  slot_duration_minutes?: number;
  break_minutes?: number;
}

export interface Availability {
  id: number;
  instructor_id: number;
  availability_type: string;
  day_of_week: number | null;
  specific_date: string | null;
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
  break_minutes: number;
}

export interface AvailabilityListResponse {
  availabilities: Availability[];
  total: number;
}

// Time Off Types

export interface AddTimeOffRequest {
  start_at: string; // ISO datetime format
  end_at: string; // ISO datetime format
  reason?: string;
}

export interface TimeOff {
  id: number;
  instructor_id: number;
  start_at: string;
  end_at: string;
  reason: string | null;
  duration_hours: number;
}

export interface TimeOffListResponse {
  time_offs: TimeOff[];
  total: number;
}

// Calendar View Types

export interface CalendarSlot {
  start_at: string;
  end_at: string;
  status: string; // 'available' | 'booked' | 'blocked'
  slot_id: number | null; // Individual slot ID for one-time availability
  availability_id: number | null;
  session_id: number | null;
  time_off_id: number | null;
}

// Individual Slot Types (for one-time availability)

export interface UpdateSlotRequest {
  start_at?: string; // ISO datetime format
  end_at?: string; // ISO datetime format
}

export interface SlotResponse {
  id: number;
  instructor_id: number;
  start_at: string;
  end_at: string;
  duration_minutes: number;
  status: string;
  availability_rule_id: number | null;
}

export interface CalendarDay {
  date: string;
  slots: CalendarSlot[];
}

export interface CalendarViewResponse {
  start_date: string;
  end_date: string;
  instructor_id: number;
  days: CalendarDay[];
}

// Generic response types for calendar operations
export interface CalendarMessageResponse {
  message: string;
  success: boolean;
}

// ============================================================================
// Messaging Types
// ============================================================================

export enum MessageType {
  TEXT = 'text',
  IMAGE = 'image',
  FILE = 'file',
  SYSTEM = 'system',
}

export enum MessageStatus {
  SENT = 'sent',
  DELIVERED = 'delivered',
  READ = 'read',
}

// User info for messaging
export interface MessageUserInfo {
  id: number;
  first_name: string;
  last_name: string;
  profile_photo_url?: string | null;
  role: string;
}

// Conversation
export interface Conversation {
  id: number;
  participant_1_id: number;
  participant_2_id: number;
  other_participant?: MessageUserInfo | null;
  last_message_at?: string | null;
  unread_count: number;
  created_at: string;
}

// Message
export interface Message {
  id: number;
  conversation_id: number;
  sender: MessageUserInfo;
  content: string;
  message_type: MessageType | string;
  status: MessageStatus | string;
  reply_to_id?: number | null;
  created_at: string;
}

// Message Attachment
export interface MessageAttachment {
  id: number;
  message_id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  file_url: string;
}

// Feature Access (based on booking status)
export interface FeatureAccess {
  can_send_text: boolean;
  can_send_image: boolean;
  can_send_file: boolean;
  has_booking: boolean;
}

// Unread Count
export interface UnreadCountResponse {
  unread_count: number;
}

// Requests
export interface StartConversationRequest {
  recipient_id: number;
}

export interface SendMessageRequest {
  content: string;
  message_type?: string;
  reply_to_id?: number;
}

export interface MarkReadRequest {
  message_id: number;
}

// WebSocket Event Types
export interface WSConnectedEvent {
  type: 'connected';
  user_id: number;
}

export interface WSNewMessageEvent {
  type: 'new_message';
  message: Message;
}

export interface WSMessageSentEvent {
  type: 'message_sent';
  message: Message;
  temp_id?: string;
}

export interface WSMessageDeliveredEvent {
  type: 'message_delivered';
  message_id: number;
}

export interface WSMessageReadEvent {
  type: 'message_read';
  conversation_id: number;
  message_id: number;
  read_by: number;
}

export interface WSUserTypingEvent {
  type: 'user_typing';
  conversation_id: number;
  user_id: number;
}

export interface WSUserStoppedTypingEvent {
  type: 'user_stopped_typing';
  conversation_id: number;
  user_id: number;
}

export interface WSUserOnlineEvent {
  type: 'user_online';
  user_id: number;
}

export interface WSUserOfflineEvent {
  type: 'user_offline';
  user_id: number;
}

export interface WSErrorEvent {
  type: 'error';
  message: string;
}

export type WSEvent =
  | WSConnectedEvent
  | WSNewMessageEvent
  | WSMessageSentEvent
  | WSMessageDeliveredEvent
  | WSMessageReadEvent
  | WSUserTypingEvent
  | WSUserStoppedTypingEvent
  | WSUserOnlineEvent
  | WSUserOfflineEvent
  | WSErrorEvent;
