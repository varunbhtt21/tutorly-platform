# Product Requirements Document (PRD)
## Tutorly Platform - Online Tutoring Marketplace

---

## 1. Product Overview

### 1.1 Vision
Build a two-sided marketplace platform that connects qualified instructors with students seeking personalized online tutoring across various subjects. The platform ensures quality through instructor verification, secure payment processing, and a seamless booking experience.

### 1.2 Product Goals
- **For Students**: Easy discovery of qualified tutors, safe booking experience, flexible scheduling, secure payments
- **For Instructors**: Professional platform to showcase expertise, manage sessions, receive reliable payments
- **For Platform**: Facilitate quality education, ensure trust and safety, generate revenue through commission

### 1.3 Target Users

#### Primary Users
1. **Students**: Individuals seeking personalized tutoring in various subjects
   - Age: 13-60+
   - Learning goals: Academic support, skill development, exam preparation, professional development
   - Tech savviness: Basic to advanced

2. **Instructors**: Educators offering tutoring services
   - Experience: University students to professional educators
   - Subjects: Academic subjects, languages, professional skills, test prep
   - Commitment: Part-time to full-time tutors

#### Secondary Users
3. **Platform Administrators**: Team managing verification, moderation, and dispute resolution

### 1.4 Success Criteria
- Instructor verification completion rate > 70%
- Student booking conversion rate > 15%
- Session completion rate > 90%
- Payment dispute rate < 2%
- Platform NPS score > 50

---

## 2. User Personas

### 2.1 Instructor Persona: "Sarah - Math Tutor"
**Background**:
- 28-year-old mathematics graduate student
- 3 years teaching experience
- Looking to supplement income with flexible tutoring

**Goals**:
- Build a tutoring business with minimal overhead
- Manage schedule around university commitments
- Receive reliable, timely payments
- Build reputation through positive reviews

**Pain Points**:
- Finding students without personal marketing
- Payment collection and tracking
- Managing scheduling conflicts
- Proving credibility to new students

**Platform Needs**:
- Simple onboarding process
- Professional profile showcase
- Calendar management tools
- Automatic payment processing
- Integrated video session platform

### 2.2 Student Persona: "Alex - High School Student"
**Background**:
- 16-year-old high school junior
- Struggling with calculus, preparing for SAT
- Parents willing to pay for quality tutoring

**Goals**:
- Find qualified tutor matching learning style
- Flexible scheduling around school hours
- Affordable pricing options
- Safe, reliable online platform

**Pain Points**:
- Difficulty finding qualified tutors in specific subjects
- Uncertainty about tutor quality before booking
- Inflexible scheduling with traditional tutoring centers
- Concerns about online payment security

**Platform Needs**:
- Clear tutor credentials and reviews
- Easy search and filtering
- Transparent pricing
- Secure booking and payment
- Reliable video platform

---

## 3. Feature Requirements

### 3.1 User Authentication & Roles

#### FR-AUTH-001: User Registration
**Priority**: P0 (Critical)
**Description**: Users can register as either Instructor or Student

**Requirements**:
- Registration form with role selection (Instructor/Student)
- Required fields:
  - Email address (verified)
  - Password (min 8 characters, must include number and special char)
  - First name, Last name
  - User type selection
- Email verification required before account activation
- Password reset functionality via email
- Social login (Google, Facebook) - Optional Phase 2

**Acceptance Criteria**:
- User receives verification email within 1 minute
- Account activated only after email verification
- Duplicate email addresses rejected
- Password meets security requirements

#### FR-AUTH-002: User Login
**Priority**: P0 (Critical)
**Description**: Secure login with JWT token-based authentication

**Requirements**:
- Login with email and password
- JWT access token (15 min expiration)
- JWT refresh token (7 day expiration)
- "Remember me" functionality
- Account lockout after 5 failed attempts (15 min cooldown)
- Session management across devices

**Acceptance Criteria**:
- Successful login redirects to appropriate dashboard (instructor/student)
- Failed login shows clear error message
- Account lockout triggers email notification
- Token refresh works seamlessly

---

### 3.2 Instructor Onboarding

#### FR-INST-001: Multi-Step Profile Creation
**Priority**: P0 (Critical)
**Description**: 7-step onboarding process for instructor profile completion

**Step 1: About**
- First name (public)
- Last name (private, only first name shown publicly)
- Country of birth (dropdown)
- Languages spoken (multi-select with proficiency: Native, Fluent, Conversational, Basic)
- Phone number (verified via OTP)

**Step 2: Photo Upload**
- Upload profile photo
- Requirements:
  - Format: JPG, PNG
  - Max size: 5MB
  - Min resolution: 400x400px
  - Clear face visible
- Photo guidelines displayed (professional, appropriate, clear)
- Preview before upload
- Crop/resize tool

**Step 3: Description**
- Introduce yourself (bio): 200-500 characters
- Teaching experience (narrative): 200-1000 characters
- Catchy headline: 50-100 characters (shown in search results)
- Examples provided for inspiration

**Step 4: Video Introduction**
- Upload 1-minute introduction video
- Requirements:
  - Format: MP4, MOV, AVI
  - Max size: 50MB
  - Duration: 30 seconds - 90 seconds
  - Clear audio and video quality
- Recording guidelines provided
- Option to record directly via webcam (browser-based)
- Video preview before upload

**Step 5: Subjects**
- Select subjects from categorized list:
  - Languages (English, Spanish, French, etc.)
  - Mathematics (Algebra, Calculus, Statistics, etc.)
  - Sciences (Physics, Chemistry, Biology, etc.)
  - Test Prep (SAT, GRE, IELTS, etc.)
  - Programming (Python, JavaScript, Java, etc.)
  - Business (Finance, Marketing, etc.)
  - Other (Music, Art, etc.)
- Set proficiency level for each subject:
  - Beginner (can teach basics)
  - Intermediate (can teach up to intermediate level)
  - Expert (can teach advanced topics)
  - Native (for languages only)
- Multiple subjects allowed (max 10)

**Step 6: Pricing**
- Set price for 50-minute regular lesson (USD)
- Pricing guidelines:
  - Minimum: $10
  - Maximum: $200
  - Suggested range based on subject and experience shown
- Optional: Set discounted price for 25-minute trial lesson (recommended 50-70% of regular price)
- Platform fee disclosure (20% commission)

**Step 7: Background**
- **Education** (multiple entries allowed):
  - Institution name
  - Degree/Certification
  - Field of study
  - Year of graduation
  - Upload degree certificate (optional, but increases trust)

- **Experience** (multiple entries allowed):
  - Company/Institution
  - Position/Role
  - Start date - End date (or "Present")
  - Brief description
  - Upload experience letter (optional)

**Requirements**:
- Progress saved after each step
- Can navigate back to edit previous steps
- All steps must be completed before submission
- "Save as draft" option available
- Final review screen before submission
- Cannot skip steps

**Acceptance Criteria**:
- Profile saved as draft after each step
- User can resume from last completed step
- All validations pass before submission
- Submission triggers verification workflow
- User receives confirmation email of submission

#### FR-INST-002: Profile Verification
**Priority**: P0 (Critical)
**Description**: Admin manual review and approval of instructor profiles

**Workflow**:
1. **Submission**: Instructor completes all 7 steps and submits
2. **Status**: Profile status changes to `PENDING_VERIFICATION`
3. **Queue**: Verification request added to admin queue
4. **Admin Review**: Admin reviews:
   - Photo appropriateness (professional, clear, appropriate)
   - Video quality and content (clear audio/video, professional presentation)
   - Description (professional, no contact info, appropriate language)
   - Background credentials (realistic, verifiable)
   - Pricing (within guidelines, not predatory)
5. **Decision**:
   - **Approve**: Status → `VERIFIED`, profile becomes visible to students, instructor notified via email
   - **Reject**: Status → `REJECTED`, rejection reasons provided, instructor can resubmit after corrections
   - **Request Changes**: Specific feedback on what needs improvement, status remains `PENDING_VERIFICATION`

**Admin Actions**:
- View all pending verifications in queue
- Sort by submission date, subject, price
- Bulk approve (for obviously qualified instructors)
- Add internal notes (visible only to admins)
- View verification history for instructor

**Rejection Reasons** (predefined):
- Photo does not meet guidelines
- Video quality too low / audio unclear
- Description contains contact information
- Background credentials appear falsified
- Pricing outside acceptable range
- Inappropriate content
- Other (custom reason)

**Re-verification on Updates**:
- Any profile edit triggers re-verification
- Profile becomes temporarily hidden from search
- Existing bookings remain valid
- Instructor notified of re-verification requirement
- Updates highlighted for admin review

**Acceptance Criteria**:
- Instructor cannot accept bookings until verified
- Profile visible in search only when status = `VERIFIED`
- Instructor receives email notification of verification decision
- Rejection includes clear, actionable feedback
- Re-verification completes within 48 hours (target SLA)

#### FR-INST-003: Instructor Profile Management
**Priority**: P0 (Critical)
**Description**: Instructors can view and update their profiles

**Requirements**:
- View own profile (as students see it)
- Edit any section (triggers re-verification)
- Update availability and pricing without re-verification
- Deactivate account temporarily (stop receiving bookings)
- Delete account (with data retention policy compliance)

**Acceptance Criteria**:
- Changes saved successfully
- Re-verification triggered for profile content changes
- Pricing/availability updates effective immediately
- Deactivated accounts hidden from search but preserve data

---

### 3.3 Instructor Availability & Calendar

#### FR-INST-004: Availability Management
**Priority**: P0 (Critical)
**Description**: Instructors set their teaching availability

**Requirements**:
- **Weekly Recurring Availability**:
  - Set available hours for each day of week
  - Multiple time slots per day
  - Session duration options: 25 min or 50 min (or both)
  - Buffer time between sessions: 5-10 minutes (auto-added)

- **Specific Date Overrides**:
  - Block specific dates (vacation, holidays)
  - Add extra availability for specific dates
  - Override recurring schedule for specific days

- **Timezone Handling**:
  - Instructor sets availability in their timezone
  - Students see slots in their own timezone
  - Automatic daylight saving time adjustment

- **Availability Display**:
  - Calendar view (weekly, monthly)
  - Next 30 days of availability shown to students
  - Color coding: Available, Booked, Blocked, Past

**Acceptance Criteria**:
- Availability updates reflected immediately on public profile
- Booked slots automatically blocked
- Timezone conversions accurate
- No double-booking possible
- Changes to availability don't affect existing bookings

#### FR-INST-005: Session Dashboard
**Priority**: P1 (High)
**Description**: Instructors see upcoming sessions and quick actions

**Requirements**:
- **Dashboard Overview**:
  - Next 3 upcoming sessions prominently displayed
  - Session details: Student first name, subject, date/time, duration
  - Quick actions: View student profile, Message, Start session, Cancel

- **Full Session List**:
  - All upcoming sessions (paginated)
  - Past sessions with status
  - Filter by: Upcoming, Completed, Cancelled
  - Search by student name, subject, date range

- **Session Reminders**:
  - In-app notification 12 hours before session
  - Email notification 12 hours before session
  - Option to opt-out of email reminders (in-app remains)

**Acceptance Criteria**:
- Dashboard loads within 2 seconds
- Next 3 sessions always visible on instructor home
- Clicking "Start session" opens Google Meet link
- Cancellation requires confirmation and reason

---

### 3.4 Student Features

#### FR-STU-001: Tutor Search & Discovery
**Priority**: P0 (Critical)
**Description**: Students can search and filter tutors based on criteria

**Search Filters**:
- **Subject**: Primary filter (required or "All Subjects")
- **Price Range**: Min-Max slider (default: $10-$200)
- **Languages Spoken**: Multi-select
- **Availability**:
  - Available now (has slots in next 24 hours)
  - Available this week
  - Specific day/time range
- **Rating**: Minimum rating filter (1-5 stars)
- **Experience Level**: Based on years teaching
- **Tutor Location/Timezone**: For timezone preference
- **Has Trial Session**: Show only tutors offering trial sessions

**Sorting Options**:
- Relevance (default, based on subject match and rating)
- Rating (highest first)
- Price (low to high)
- Price (high to low)
- Newest tutors
- Most sessions completed

**Search Results Display**:
- Card view with:
  - Profile photo
  - First name only
  - Catchy headline
  - Subjects (up to 3 shown)
  - Rating (stars + number of reviews)
  - Price per session (trial price if available)
  - Languages spoken
  - "View Profile" button
  - "Book Trial" / "Book Session" button
- Pagination: 20 results per page
- Skeleton loader while loading

**Acceptance Criteria**:
- Only `VERIFIED` instructors shown
- Search results return within 2 seconds
- Filters work in combination
- No instructors shown if all criteria exclude everyone (show "No results" message)
- Clicking instructor card opens full profile

#### FR-STU-002: Instructor Public Profile View
**Priority**: P0 (Critical)
**Description**: Students view detailed instructor profile before booking

**Profile Sections**:
1. **Header**:
   - Profile photo
   - First name only (last name hidden)
   - Headline
   - Rating (average + total reviews)
   - Response time (average time to reply to messages)
   - Total sessions completed

2. **Introduction Video**:
   - Embedded video player
   - Play/pause controls
   - Fullscreen option

3. **About**:
   - Bio
   - Teaching experience narrative
   - Languages spoken (with proficiency badges)
   - Country

4. **Subjects**:
   - All subjects with proficiency levels
   - Visual badges (Beginner, Intermediate, Expert, Native)

5. **Education**:
   - List of degrees/certifications
   - Institution, degree, year
   - Verified badge if certificate uploaded

6. **Experience**:
   - Work history
   - Company, position, duration
   - Description

7. **Pricing**:
   - 50-min session price (prominently displayed)
   - 25-min trial session price (if offered)
   - "Book Trial" / "Book Session" CTA

8. **Availability Calendar**:
   - Next 30 days
   - Available slots in student's timezone
   - Click slot to book directly

9. **Reviews & Ratings**:
   - Overall rating breakdown (5-star distribution)
   - Recent reviews (paginated)
   - Filter: All, 5-star, 4-star, etc.
   - Instructor responses to reviews (if any)

**Actions Available**:
- Send message (opens chat)
- Book trial session
- Book regular session
- Add to favorites (for logged-in students)
- Share profile (copy link)
- Report profile (inappropriate content)

**Acceptance Criteria**:
- Profile loads completely within 3 seconds
- Video autoplays on mute (or user preference)
- Availability calendar shows accurate timezone conversion
- Booking buttons disabled if no availability
- Message button works for logged-in users only

#### FR-STU-003: Student Profile
**Priority**: P1 (High)
**Description**: Students manage their profile and preferences

**Profile Information**:
- First name, Last name
- Email (verified)
- Phone number (optional)
- Timezone
- Preferred language
- Learning goals (optional narrative)
- Profile photo (optional)

**Preferences**:
- Email notification settings
- Default payment method
- Preferred session duration
- Timezone preference

**Acceptance Criteria**:
- Profile updates save successfully
- Email changes require re-verification
- Preferences applied to future bookings

---

### 3.5 Booking & Scheduling

#### FR-BOOK-001: Session Booking Flow
**Priority**: P0 (Critical)
**Description**: Students book tutoring sessions with instructors

**Booking Process**:

**Step 1: Select Availability**
- Student views instructor's calendar
- Clicks on available time slot
- Confirms session type: Trial (25 min) or Regular (50 min)

**Step 2: Add Details** (Optional)
- Add message to instructor (e.g., "I need help with quadratic equations")
- Specify learning goals for session
- Attach reference materials (if needed)

**Step 3: Payment**
- Review booking summary:
  - Instructor name
  - Subject
  - Date & time (in student's timezone)
  - Duration
  - Price
  - Platform fee (included in price, disclosed)
- Select payment method:
  - Credit/Debit card (Stripe)
  - PayPal
  - Wallet balance (if sufficient)
- Apply promo code (if any)
- Review cancellation policy

**Step 4: Confirm & Pay**
- Payment processed (held by platform, not transferred yet)
- Booking confirmed instantly
- Confirmation page with:
  - Booking ID
  - Session details
  - Google Meet link (generated)
  - Add to calendar options (Google, iCal, Outlook)

**Post-Booking Actions**:
- Confirmation email sent to student
- Notification email sent to instructor
- Instructor calendar automatically blocked
- Slot removed from instructor availability
- Google Meet event created (if integration enabled)
- Chat between student and instructor enabled (full features)

**Booking Constraints**:
- Minimum advance booking: 2 hours from now
- Maximum advance booking: 30 days from now
- Cannot book overlapping sessions with same instructor
- Cannot book if payment fails

**Acceptance Criteria**:
- Booking completes within 5 seconds after payment
- Payment held, not transferred to instructor yet
- Both parties receive confirmation emails within 1 minute
- Google Meet link works when clicked
- Slot immediately disappears from instructor availability
- Student can access booking from "My Bookings" page

#### FR-BOOK-002: Booking Management
**Priority**: P1 (High)
**Description**: Students and instructors manage existing bookings

**Student Actions**:
- **View Bookings**:
  - Upcoming bookings
  - Past bookings (with status)
  - Filter by: Subject, Instructor, Date range

- **Cancel Booking**:
  - Cancellation policy displayed
  - Requires confirmation
  - Refund amount shown based on timing:
    - >24h before: 100% refund
    - 12-24h before: 50% refund
    - <12h before: No refund
  - Cancellation reason required

- **Reschedule Booking**:
  - Available only if >12h before session
  - Select new slot from instructor availability
  - No additional charge if same session type
  - Instructor must approve (auto-approved if >24h)

**Instructor Actions**:
- **View Bookings**: Same as student
- **Cancel Booking**:
  - Requires approval from support team (to prevent abuse)
  - Valid reasons only: Emergency, Technical issue, Student request
  - Student automatically refunded 100% regardless of timing
  - Instructor penalized (warning/suspension for repeated cancellations)

**Acceptance Criteria**:
- Cancellation processed immediately
- Refund initiated within 1 hour
- Refund reaches student within 3-5 business days
- Cancelled slot becomes available again on instructor calendar
- Both parties notified of cancellation
- Reschedule requests sent to instructor for approval

---

### 3.6 Messaging System

#### FR-MSG-001: Pre-Booking Chat (Restricted)
**Priority**: P0 (Critical)
**Description**: Students can message instructors before booking with restrictions

**Allowed**:
- Text messages only
- Discuss learning goals, session topics
- Ask questions about instructor's teaching style
- Clarify availability

**Prohibited** (Violation Rules):
- Email addresses
- Phone numbers
- External links (http://, www., etc.)
- Social media handles (Instagram, Facebook, WhatsApp, etc.)
- Personal identifiable contact information
- Attempts to circumvent platform (e.g., "contact me at john [at] gmail")

**Violation Detection**:
- Real-time regex pattern matching:
  - Email: `.*@.*\..*`
  - Phone: `\+?\d{10,15}`, `\(\d{3}\)\s*\d{3}-\d{4}`, etc.
  - URLs: `https?://`, `www\.`, `.com`, `.net`, etc.
  - Social: "instagram", "facebook", "whatsapp", "telegram", "snapchat", "twitter", etc.
- Message blocked if violation detected
- User shown warning message: "Your message contains prohibited content. Please remove contact information."

**Violation Consequences** (Automated):
- **1st Violation**: Warning message, message not sent, logged
- **2nd Violation**: Warning + email notification to user about policy
- **3rd Violation**: 7-day temporary suspension, cannot send messages
- **4th Violation**: Permanent ban from platform, account deactivated

**Acceptance Criteria**:
- Messages containing violations are blocked immediately
- User receives clear explanation of what was detected
- Violation count tracked per user account
- Instructors notified if student attempts violation (to maintain trust)
- Admin dashboard shows all violations for review

#### FR-MSG-002: Post-Booking Chat (Full Features)
**Priority**: P0 (Critical)
**Description**: After booking confirmed, full messaging features enabled

**Allowed Features**:
- Text messages (unlimited)
- File attachments:
  - Documents: PDF, DOC, DOCX, TXT, PPT, PPTX
  - Images: JPG, PNG, GIF
  - Archives: ZIP (for multiple files)
  - Max size: 10MB per file
- External links (now allowed since session booked)
- No violations enforced (users have committed to platform)

**Message Features**:
- Real-time delivery (WebSocket)
- Read receipts ("Seen")
- Typing indicators
- Message timestamps
- File preview (images inline, documents as download)
- Search within conversation
- Delete message (within 5 minutes of sending)
- Edit message (within 5 minutes of sending)

**Conversation Management**:
- Conversations list (all active chats)
- Unread message counter
- Last message preview
- Archive conversation (hide from main list)
- Mute conversation (disable notifications)

**Acceptance Criteria**:
- File upload completes within 10 seconds for 10MB file
- Real-time message delivery (<1 second latency)
- Read receipts update immediately
- File downloads work for all supported types
- Search returns results within 1 second

#### FR-MSG-003: Message Notifications
**Priority**: P1 (High)
**Description**: Users notified of new messages

**Notification Channels**:
- **In-App**: Real-time notification badge + sound
- **Email**: If user offline for >5 minutes
- **Push** (Future): Mobile app notifications

**Email Notification**:
- Subject: "New message from [Instructor/Student Name]"
- Body: Sender name, message preview (first 100 chars), link to conversation
- Unsubscribe option (but recommended to keep enabled)
- Rate limit: Max 1 email every 5 minutes per conversation (batch multiple messages)

**Acceptance Criteria**:
- In-app notification appears within 1 second of message sent
- Email sent within 5 minutes if user offline
- Email contains correct message preview
- Clicking email link opens conversation in platform

---

### 3.7 Session Management

#### FR-SESS-001: Session Lifecycle
**Priority**: P0 (Critical)
**Description**: Complete session flow from start to completion

**Session States**:
- `SCHEDULED`: Booking confirmed, awaiting session start time
- `REMINDED`: 12-hour reminder sent (internal state)
- `IN_PROGRESS`: Session currently happening
- `PENDING_CONFIRMATION`: Session ended, awaiting student confirmation
- `COMPLETED`: Student confirmed, payment released
- `CANCELLED`: Cancelled by student or instructor
- `NO_SHOW_STUDENT`: Student didn't join within 10 minutes
- `NO_SHOW_INSTRUCTOR`: Instructor didn't join within 10 minutes
- `DISPUTED`: Under review by support team

**Session Flow**:

**T-12 Hours: Reminder**
- Automated task runs every hour to check sessions in next 12 hours
- Email sent to both student and instructor:
  - Subject: "Your tutoring session is starting in 12 hours"
  - Body: Session details, Google Meet link, preparation tips
  - Add to calendar reminder (if not already added)
- In-app notification with session details
- Session state: `REMINDED` (internal tracking)

**T-10 Minutes: Pre-Session**
- Google Meet link becomes active
- Notification: "Your session starts in 10 minutes. Join early to test your setup."
- Quick tech check reminder (camera, microphone, internet)

**T-0: Session Start Time**
- Both parties can join Google Meet
- Session state: `IN_PROGRESS` (when first person joins)
- Session timer starts (25 or 50 minutes)
- In-session features:
  - Video call (Google Meet)
  - Screen sharing
  - Chat (Google Meet native chat)
  - File sharing (optional, via Google Meet or platform)

**T+Duration: Session End**
- Timer expires (or instructor manually ends)
- Session state: `PENDING_CONFIRMATION`
- Both parties exit Google Meet
- Student immediately sees confirmation prompt (in-app + email)

**T+Duration to T+24h: Confirmation Window**
- **Student Confirmation Prompt**:
  - "Did your session with [Instructor Name] happen successfully?"
  - Options:
    - ✅ "Yes, confirm session" → `COMPLETED` state, payment released
    - ❌ "No, there was an issue" → Dispute form shown → `DISPUTED` state
  - Prompt shown:
    - Immediately after session end (in-app modal)
    - Email reminder if not confirmed within 2 hours
    - Email reminder if not confirmed within 12 hours
    - Final email reminder at 23 hours

**Automatic Confirmation**:
- If student doesn't respond within 24 hours, session auto-confirmed
- Session state: `COMPLETED`
- Payment released to instructor
- Student notified of auto-confirmation

**Payment Release**:
- When session `COMPLETED`:
  - Platform fee deducted (20% of session price)
  - Net amount credited to instructor wallet
  - Transaction recorded
  - Instructor notified: "You've been paid for your session with [Student Name]"
  - Instructor wallet balance updated

**Acceptance Criteria**:
- Reminders sent exactly 12 hours before (±5 min tolerance)
- Google Meet link works at session start time
- Session timer accurate to within 10 seconds
- Student confirmation prompt shows immediately after session
- Auto-confirmation triggers at exactly 24 hours
- Payment released within 1 hour of confirmation
- Instructor notified of payment via email and in-app

#### FR-SESS-002: No-Show Handling
**Priority**: P1 (High)
**Description**: Handle cases where student or instructor doesn't show up

**Student No-Show**:
- **Detection**: Instructor marks "Student didn't show up" after waiting 10 minutes
- **Process**:
  1. Instructor clicks "Report No-Show" in session
  2. Confirmation dialog: "Are you sure the student didn't join?"
  3. Session state: `NO_SHOW_STUDENT`
  4. Student notified and asked to confirm/dispute
  5. If student confirms: Payment released to instructor (student forfeits payment)
  6. If student disputes: Support team reviews (check Google Meet logs)
  7. Session slot freed up on instructor calendar

**Instructor No-Show**:
- **Detection**: Student marks "Instructor didn't show up" after waiting 10 minutes
- **Process**:
  1. Student clicks "Report No-Show" in session
  2. Confirmation dialog: "Are you sure the instructor didn't join?"
  3. Session state: `NO_SHOW_INSTRUCTOR`
  4. Instructor notified and asked to explain
  5. Automatic full refund to student (processed immediately)
  6. Additional credit/voucher offered to student for inconvenience
  7. Instructor penalized:
     - First offense: Warning
     - Second offense: 7-day suspension
     - Third offense: Permanent ban
  8. Support team reviews (check Google Meet logs)

**Acceptance Criteria**:
- No-show can only be reported after 10 minutes past start time
- Refunds processed immediately for instructor no-shows
- Payment released to instructor only after student no-show confirmed
- Repeated student no-shows flagged for review (potential abuse)
- Support team has access to session join logs for dispute resolution

#### FR-SESS-003: Session Disputes
**Priority**: P1 (High)
**Description**: Handle disputes about session quality, content, or completion

**Dispute Triggers**:
- Student clicks "No, there was an issue" on confirmation prompt
- Student/instructor reports issue during/after session
- Payment dispute raised

**Dispute Reasons** (Student):
- Session didn't happen (no-show)
- Instructor ended session early
- Poor audio/video quality (instructor's fault)
- Instructor was unprepared
- Inappropriate behavior
- Content not as expected
- Other (custom reason)

**Dispute Process**:
1. **Submission**: Student/instructor submits dispute with reason and details
2. **Payment Hold**: Payment remains held (not released to instructor)
3. **Support Queue**: Dispute added to admin queue
4. **Investigation**: Admin reviews:
   - Session join logs (who joined, when, duration)
   - Chat messages (if any)
   - Previous session history between parties
   - User's dispute history
5. **Resolution**:
   - **Favor Student**: Full/partial refund, instructor warned/penalized
   - **Favor Instructor**: Payment released, student warned (if abuse suspected)
   - **Compromise**: Partial refund to student, partial payment to instructor
   - **Inconclusive**: Platform absorbs cost, both parties made whole

**Acceptance Criteria**:
- Dispute form captures all necessary details
- Payment frozen until dispute resolved
- Admin has all information needed for fair judgment
- Resolution communicated clearly to both parties
- Repeated disputes flag users for additional scrutiny

---

### 3.8 Payment & Wallet System

#### FR-PAY-001: Student Payment Processing
**Priority**: P0 (Critical)
**Description**: Secure payment capture when student books session

**Payment Methods**:
1. **Credit/Debit Card** (via Stripe):
   - Major cards: Visa, Mastercard, Amex, Discover
   - Secure tokenization (no card details stored)
   - 3D Secure authentication (SCA compliance)
   - Save card for future bookings (optional)

2. **PayPal**:
   - PayPal account login
   - One-click checkout for returning users
   - PayPal balance or linked card/bank

3. **Wallet Balance** (future):
   - Students can preload wallet
   - Use wallet balance for bookings
   - Faster checkout

**Payment Flow**:
1. Student selects session and clicks "Book"
2. Booking summary shown with total price
3. Payment method selection
4. Payment details entered (or saved card selected)
5. Payment processed (authorization + capture)
6. If successful:
   - Payment held by platform (not transferred to instructor)
   - Booking confirmed
   - Confirmation shown
7. If failed:
   - Error message shown
   - Booking not created
   - User can retry with different method

**Payment Statuses**:
- `PENDING`: Payment initiated, awaiting confirmation
- `HELD`: Payment captured, held by platform
- `PROCESSING`: Payment being transferred (after session confirmation)
- `COMPLETED`: Payment successfully transferred to instructor
- `REFUNDED`: Payment returned to student
- `FAILED`: Payment failed, booking cancelled

**Acceptance Criteria**:
- Payment processed within 5 seconds
- Secure (PCI DSS compliant, no card details stored)
- Failed payments show clear error message
- Successful payment immediately confirms booking
- Payment held, not transferred until session confirmed

#### FR-PAY-002: Instructor Wallet & Payouts
**Priority**: P0 (Critical)
**Description**: Instructors accumulate earnings and request withdrawals

**Wallet Features**:
- **Balance Display**:
  - Total balance (available for withdrawal)
  - Pending balance (from sessions not yet confirmed)
  - Earnings this month
  - Lifetime earnings
  - Recent transactions (paginated)

- **Transaction Types**:
  - `SESSION_CREDIT`: Earnings from confirmed session (net after platform fee)
  - `REFUND_DEDUCTION`: Deduction due to refunded session
  - `WITHDRAWAL`: Money transferred out to bank/PayPal
  - `ADJUSTMENT`: Manual adjustment by admin (with reason)
  - `BONUS`: Platform bonus or promotion credit

**Withdrawal Options**:
1. **Bank Transfer** (ACH/Wire):
   - Minimum withdrawal: $50
   - Processing time: 3-5 business days
   - Fee: $0 (platform covers)
   - Bank details required: Account number, routing number, account holder name

2. **PayPal**:
   - Minimum withdrawal: $20
   - Processing time: 1-2 business days
   - Fee: $0 (platform covers)
   - PayPal email required

3. **Stripe Connect** (future):
   - Instant transfer (if supported)
   - Fee: Platform covers

**Withdrawal Process**:
1. Instructor clicks "Withdraw" in wallet
2. Select withdrawal method
3. Enter amount (must meet minimum)
4. Confirm bank/PayPal details (or use saved)
5. Review and confirm
6. Withdrawal request created
7. Status: `PENDING_REVIEW` (automatic approval for trusted instructors)
8. Admin approval (if flagged or first withdrawal)
9. Status: `PROCESSING`
10. Transfer initiated via Stripe/PayPal
11. Status: `COMPLETED` (or `FAILED` if error)

**Platform Fee Structure**:
- Standard: 20% of session price
- Platform fee deducted before crediting instructor
- Example: $100 session → $80 credited to instructor wallet
- Fee percentage shown during onboarding and on pricing page

**Acceptance Criteria**:
- Wallet balance updates immediately after session confirmation
- Transaction history accurate and complete
- Withdrawal requests processed within 24 hours
- Funds arrive in bank/PayPal within stated timeframe
- Failed withdrawals retry automatically or notify instructor

#### FR-PAY-003: Refund Processing
**Priority**: P1 (High)
**Description**: Handle refunds for cancelled or disputed sessions

**Refund Scenarios**:
1. **Student Cancellation**:
   - >24h before session: 100% refund
   - 12-24h before: 50% refund (50% to instructor as cancellation fee)
   - <12h before: 0% refund (100% to instructor)
   - No-show: 0% refund (100% to instructor)

2. **Instructor Cancellation**:
   - Any time: 100% refund to student
   - Instructor penalized (warning/suspension)

3. **Instructor No-Show**:
   - 100% refund + $10 credit to student
   - Instructor receives 0%

4. **Dispute Resolution**:
   - Admin determines refund percentage (0-100%)
   - Instructor receives remainder (100% - refund%)

**Refund Process**:
1. Refund initiated (automated or manual)
2. Payment gateway refund API called (Stripe/PayPal)
3. Refund status: `PROCESSING`
4. Funds returned to original payment method
5. Refund status: `COMPLETED`
6. Student notified via email
7. Transaction recorded in both student and instructor records

**Refund Timeline**:
- Credit card: 5-10 business days
- PayPal: 1-3 business days
- Wallet balance: Immediate

**Acceptance Criteria**:
- Refund initiated within 1 hour of cancellation/resolution
- Student receives email confirmation of refund
- Funds appear in original payment method within stated timeframe
- Refund amount accurate based on cancellation timing
- Transaction history shows refund details

---

### 3.9 Reviews & Ratings

#### FR-REV-001: Student Reviews
**Priority**: P1 (High)
**Description**: Students can review instructors after completed sessions

**Review Eligibility**:
- Only after session status = `COMPLETED`
- One review per session
- Review window: Within 30 days of session completion
- Cannot edit review after submission (but can delete within 24h)

**Review Components**:
- **Rating**: 1-5 stars (required)
  - Overall experience
  - Optional breakdown (future):
    - Teaching quality
    - Communication
    - Professionalism
    - Value for money

- **Written Review**: Optional, max 500 characters
  - What did you like?
  - What could be improved?
  - Would you recommend this instructor?

**Review Submission**:
- Prompt shown after session confirmation
- Can also access from booking history
- Review form: Rating slider + text area
- Preview before submit
- Content moderation (automated profanity filter)
- Publish immediately after submission

**Review Display**:
- Shown on instructor public profile
- Most recent reviews first
- Instructor can respond (once per review)
- Reviews can be filtered: All, 5-star, 4-star, 3-star, 2-star, 1-star
- Average rating calculated and displayed prominently

**Acceptance Criteria**:
- Review prompt shows after session confirmation
- Profanity filter blocks inappropriate content
- Review appears on instructor profile within 1 minute
- Average rating recalculated immediately
- Student cannot review until session confirmed

#### FR-REV-002: Instructor Responses
**Priority**: P2 (Medium)
**Description**: Instructors can respond to student reviews

**Response Rules**:
- Instructors can respond to any review (once)
- Response max 300 characters
- Must be professional and respectful
- Cannot edit response after submission
- Response shown below student review

**Response Moderation**:
- Automated profanity filter
- Admin can hide inappropriate responses
- Instructor warned/suspended for unprofessional responses

**Acceptance Criteria**:
- Response appears below review immediately
- Profanity filter blocks inappropriate content
- Student notified when instructor responds
- Only one response allowed per review

#### FR-REV-003: Review Moderation
**Priority**: P2 (Medium)
**Description**: Admin moderation of reviews and responses

**Reportable Reviews**:
- Student can report instructor response as inappropriate
- Instructor can report student review as false/malicious
- Anyone can report offensive content

**Admin Actions**:
- View reported reviews
- Hide review (removed from public view, but preserved in records)
- Delete response
- Warn user
- Ban user (for repeated violations)

**Moderation Criteria**:
- Offensive language
- Personal attacks
- False information
- Spam or irrelevant content
- Attempts to share contact info

**Acceptance Criteria**:
- Reports added to admin queue
- Admin can view review history and context
- Hidden reviews not visible to public but preserved in database
- Users notified when their review/response is moderated

---

### 3.10 Admin Panel

#### FR-ADMIN-001: Verification Management
**Priority**: P0 (Critical)
**Description**: Admin reviews and approves instructor profiles

**Requirements**:
- Queue of pending verification requests
- Sort by: Date submitted, Subject, Price, Priority
- Filter by: Subject category, Status
- Bulk actions: Approve multiple (if all meet criteria)

**Review Interface**:
- Instructor profile preview (as students see it)
- All 7 onboarding sections displayed
- Photo and video embedded
- Background credentials listed
- Admin actions:
  - ✅ Approve (with optional note)
  - ❌ Reject (with required reason)
  - 💬 Request Changes (with specific feedback)
- Internal notes (visible only to admins)
- Verification history (previous approvals/rejections)

**Acceptance Criteria**:
- All pending verifications visible in queue
- Admin can review all profile sections before decision
- Rejection reason required and sent to instructor
- Approval immediately makes profile visible
- SLA tracking: Target 48-hour review time

#### FR-ADMIN-002: Content Moderation
**Priority**: P1 (High)
**Description**: Admin moderates messages, reviews, and reports

**Violation Dashboard**:
- All messaging violations logged
- User details, violation count, violation text
- Sort by: Date, User, Violation count
- Actions: Warn, Suspend, Ban

**Reported Content**:
- Reported reviews, messages, profiles
- Reporter details (student/instructor)
- Report reason
- Content preview
- Actions: Dismiss, Hide content, Warn user, Ban user

**Acceptance Criteria**:
- All violations visible in admin dashboard
- Admin can take action on each violation
- Users notified of moderation actions
- Permanent log of all moderation actions

#### FR-ADMIN-003: Dispute Resolution
**Priority**: P1 (High)
**Description**: Admin resolves session disputes

**Dispute Queue**:
- All open disputes
- Dispute details: Student, Instructor, Session, Reason
- Evidence: Session logs, join times, chat history
- Priority flags (high-value disputes first)

**Resolution Interface**:
- View all session details
- View messages between student and instructor
- View session join logs (Google Meet)
- Decision options:
  - Full refund to student (0% to instructor)
  - Partial refund (specify percentage)
  - No refund (100% to instructor)
  - Custom resolution (manual adjustment)
- Resolution reason (sent to both parties)

**Acceptance Criteria**:
- All disputes visible in admin queue
- Admin has all necessary information for fair judgment
- Resolution applied immediately (payment/refund processed)
- Both parties notified of resolution with reason
- Dispute history preserved for future reference

#### FR-ADMIN-004: Analytics Dashboard
**Priority**: P2 (Medium)
**Description**: Platform metrics and analytics for business insights

**Key Metrics**:
- **User Metrics**:
  - Total users (instructors, students)
  - New signups (daily, weekly, monthly)
  - Active users (logged in last 30 days)
  - Instructor verification rate
  - Student retention rate

- **Session Metrics**:
  - Total sessions (scheduled, completed, cancelled)
  - Session completion rate
  - Average session price
  - Sessions by subject category
  - Peak booking times

- **Revenue Metrics**:
  - Gross revenue (total session prices)
  - Platform revenue (total fees collected)
  - Instructor payouts
  - Refunds issued
  - Revenue by subject, instructor, month

- **Quality Metrics**:
  - Average rating (overall, by subject)
  - Top-rated instructors
  - Dispute rate
  - Violation rate
  - Cancellation rate

**Visualizations**:
- Line charts (trends over time)
- Bar charts (comparisons)
- Pie charts (distributions)
- Tables (top instructors, subjects, etc.)

**Export Options**:
- Export data as CSV
- Generate PDF reports
- Scheduled email reports (weekly/monthly)

**Acceptance Criteria**:
- Dashboard loads within 3 seconds
- All metrics accurate and real-time
- Charts interactive and responsive
- Export functionality works correctly

---

## 4. User Flows

### 4.1 Instructor Onboarding Flow
```
START (New Instructor)
  │
  ├─> Register account (email, password, role: Instructor)
  │
  ├─> Email verification
  │
  ├─> Redirected to onboarding (7 steps)
  │   │
  │   ├─> Step 1: About (name, country, languages, phone)
  │   │   └─> Save as draft → Next
  │   │
  │   ├─> Step 2: Photo (upload profile photo)
  │   │   └─> Validate → Save → Next
  │   │
  │   ├─> Step 3: Description (bio, experience, headline)
  │   │   └─> Save → Next
  │   │
  │   ├─> Step 4: Video (upload 1-min intro video)
  │   │   └─> Validate → Save → Next
  │   │
  │   ├─> Step 5: Subjects (select subjects + proficiency)
  │   │   └─> Save → Next
  │   │
  │   ├─> Step 6: Pricing (set session price)
  │   │   └─> Save → Next
  │   │
  │   └─> Step 7: Background (education, experience)
  │       └─> Save → Final Review
  │
  ├─> Submit for Verification
  │   └─> Status: PENDING_VERIFICATION
  │
  ├─> Admin Reviews Profile
  │   │
  │   ├─> APPROVED → Status: VERIFIED → Profile visible to students → Email notification
  │   │
  │   └─> REJECTED → Status: REJECTED → Email with reasons → Can resubmit
  │
  ├─> Set Availability (weekly schedule, time slots)
  │
  └─> Ready to Receive Bookings

END (Instructor Active)
```

### 4.2 Student Booking Flow
```
START (Student looking for tutor)
  │
  ├─> Login/Register
  │
  ├─> Search for tutors
  │   │
  │   ├─> Apply filters (subject, price, rating, availability)
  │   │
  │   └─> View search results
  │
  ├─> Click on instructor profile
  │   │
  │   ├─> View intro video, bio, subjects, reviews
  │   │
  │   ├─> View availability calendar
  │   │
  │   └─> Decision: Message first OR Book directly
  │
  ├─> If MESSAGE FIRST:
  │   │
  │   ├─> Send message (text only, restricted)
  │   │   └─> Violation detection active
  │   │
  │   ├─> Instructor responds
  │   │
  │   └─> Decide to book → Continue to booking
  │
  ├─> SELECT AVAILABLE SLOT from calendar
  │
  ├─> Choose session type (Trial 25min or Regular 50min)
  │
  ├─> Add optional message/learning goals
  │
  ├─> PAYMENT
  │   │
  │   ├─> Review booking summary (instructor, date/time, price)
  │   │
  │   ├─> Select payment method (card, PayPal, wallet)
  │   │
  │   ├─> Enter payment details (or use saved)
  │   │
  │   └─> Confirm & Pay
  │       │
  │       ├─> Payment SUCCESS:
  │       │   │
  │       │   ├─> Booking confirmed
  │       │   ├─> Payment HELD by platform
  │       │   ├─> Confirmation email sent
  │       │   ├─> Google Meet link generated
  │       │   ├─> Instructor notified
  │       │   ├─> Slot blocked on instructor calendar
  │       │   └─> Full chat features enabled
  │       │
  │       └─> Payment FAILED:
  │           └─> Booking not created → Show error → Retry
  │
  ├─> BEFORE SESSION (T-12 hours):
  │   └─> Both receive reminder email + in-app notification
  │
  ├─> SESSION START TIME:
  │   │
  │   ├─> Both join Google Meet
  │   │
  │   ├─> Session status: IN_PROGRESS
  │   │
  │   ├─> Session timer starts (25 or 50 min)
  │   │
  │   └─> Tutoring session happens (video, screen share, chat)
  │
  ├─> SESSION END:
  │   │
  │   ├─> Timer expires (or manual end)
  │   │
  │   └─> Session status: PENDING_CONFIRMATION
  │
  ├─> STUDENT CONFIRMATION PROMPT:
  │   │
  │   ├─> "Did session happen successfully?"
  │   │   │
  │   │   ├─> YES, CONFIRM:
  │   │   │   │
  │   │   │   ├─> Session status: COMPLETED
  │   │   │   ├─> Payment released to instructor (minus 20% platform fee)
  │   │   │   ├─> Instructor wallet credited
  │   │   │   ├─> Instructor notified
  │   │   │   └─> Student prompted to leave review
  │   │   │
  │   │   └─> NO, ISSUE:
  │   │       │
  │   │       ├─> Dispute form shown
  │   │       ├─> Session status: DISPUTED
  │   │       ├─> Payment held
  │   │       └─> Support team reviews → Resolution
  │   │
  │   └─> If no response within 24h:
  │       └─> Auto-confirm → Payment released
  │
  └─> OPTIONAL: Leave review (rating + written review)

END (Booking Complete)
```

### 4.3 Messaging Violation Flow
```
START (Student/Instructor sends message)
  │
  ���─> Check: Is booking confirmed between these users?
  │   │
  │   ├─> YES (Post-booking):
  │   │   └─> Allow all content (text, files, links)
  │   │       └─> Send message → END
  │   │
  │   └─> NO (Pre-booking):
  │       │
  │       └─> Run violation detection (regex patterns)
  │           │
  │           ├─> NO VIOLATION:
  │           │   └─> Send message → END
  │           │
  │           └─> VIOLATION DETECTED:
  │               │
  │               ├─> Block message (do not send)
  │               │
  │               ├─> Show warning to user: "Message contains prohibited content"
  │               │
  │               ├─> Log violation (user_id, violation_type, message_text, timestamp)
  │               │
  │               ├─> Get user violation count
  │               │   │
  │               │   ├─> 1st Violation:
  │               │   │   └─> Show warning message only
  │               │   │
  │               │   ├─> 2nd Violation:
  │               │   │   ├─> Show warning message
  │               │   │   └─> Send policy email to user
  │               │   │
  │               │   ├─> 3rd Violation:
  │               │   │   ├─> 7-day temporary suspension
  │               │   │   ├─> Account status: SUSPENDED
  │               │   │   ├─> Cannot send messages for 7 days
  │               │   │   └─> Email notification of suspension
  │               │   │
  │               │   └─> 4th+ Violation:
  │               │       ├─> Permanent ban
  │               │       ├─> Account status: BANNED
  │               │       ├─> Cannot access platform
  │               │       └─> Email notification of ban
  │               │
  │               └─> Notify other party (if instructor):
  │                   └─> "Student attempted to share contact info (violation)"

END
```

### 4.4 Payment & Payout Flow
```
START (Booking Created)
  │
  ├─> Student pays for session
  │   │
  │   ├─> Payment processed via Stripe/PayPal
  │   │
  │   ├─> Payment status: HELD (not transferred yet)
  │   │
  │   └─> Funds held by platform in escrow
  │
  ├─> Session happens
  │
  ├─> Session ends
  │
  ├─> Student confirmation:
  │   │
  │   ├─> CONFIRMED (or auto-confirmed after 24h):
  │   │   │
  │   │   ├─> Calculate payout:
  │   │   │   │
  │   │   │   ├─> Session price: $100
  │   │   │   ├─> Platform fee (20%): -$20
  │   │   │   └─> Instructor payout: $80
  │   │   │
  │   │   ├─> Payment status: PROCESSING
  │   │   │
  │   │   ├─> Credit instructor wallet: +$80
  │   │   │
  │   │   ├─> Create transaction record
  │   │   │
  │   │   ├─> Payment status: COMPLETED
  │   │   │
  │   │   ├─> Notify instructor: "You've been paid $80 for session with [Student]"
  │   │   │
  │   │   └─> Instructor wallet balance updated
  │   │
  │   └─> DISPUTED:
  │       │
  │       ├─> Payment remains HELD
  │       │
  │       ├─> Support team reviews
  │       │
  │       └─> Resolution:
  │           │
  │           ├─> Full refund to student: $100 refunded, $0 to instructor
  │           │
  │           ├─> Partial refund: $50 to student, $50 to instructor
  │           │
  │           └─> No refund: $0 to student, $80 to instructor (after fee)
  │
  ├─> INSTRUCTOR WALLET:
  │   │
  │   ├─> Balance accumulates from multiple sessions
  │   │
  │   └─> Instructor requests withdrawal:
  │       │
  │       ├─> Choose method: Bank transfer or PayPal
  │       │
  │       ├─> Enter amount (must meet minimum: $50 bank, $20 PayPal)
  │       │
  │       ├─> Confirm bank/PayPal details
  │       │
  │       ├─> Withdrawal request status: PENDING_REVIEW
  │       │
  │       ├─> Admin approval (automatic for trusted instructors)
  │       │
  │       ├─> Status: PROCESSING
  │       │
  │       ├─> Transfer initiated via Stripe/PayPal
  │       │
  │       ├─> Status: COMPLETED (or FAILED)
  │       │
  │       ├─> Funds arrive in bank/PayPal (3-5 days bank, 1-2 days PayPal)
  │       │
  │       └─> Instructor notified of successful withdrawal

END
```

---

## 5. Business Rules

### 5.1 Messaging Rules
| Condition | Allowed Content | Prohibited Content | Enforcement |
|-----------|----------------|-------------------|-------------|
| **Pre-Booking** (no confirmed session) | Text messages, questions about tutoring | Email addresses, phone numbers, external links, social media handles | Automated violation detection, progressive penalties |
| **Post-Booking** (session confirmed) | Text messages, file attachments (PDF, images, documents), external links | None (all content allowed) | No restrictions, content logged for disputes |
| **Violation Penalties** | - | 1st: Warning, 2nd: Email warning, 3rd: 7-day suspension, 4th: Permanent ban | Automated enforcement based on violation count |

### 5.2 Payment Rules
| Event | Student | Instructor | Platform |
|-------|---------|-----------|----------|
| **Booking Created** | Pays full session price upfront | Receives nothing yet (payment held) | Holds payment in escrow |
| **Session Confirmed** | No further action | Receives 80% of session price (after 20% fee) | Retains 20% platform fee |
| **Student Cancellation (>24h)** | Full refund (100%) | Receives nothing (slot freed) | Refunds processing fee |
| **Student Cancellation (12-24h)** | 50% refund | Receives 50% as cancellation fee | Retains percentage of fee |
| **Student Cancellation (<12h)** | No refund (0%) | Receives 100% (80% after platform fee) | Retains 20% platform fee |
| **Instructor Cancellation (any time)** | Full refund (100%) | Receives nothing + penalty (warning/suspension) | Absorbs cancellation cost |
| **Instructor No-Show** | Full refund (100%) + $10 credit | Receives nothing + penalty | Absorbs cost + credit |
| **Student No-Show** | No refund (0%) | Receives 100% (80% after fee) | Retains 20% platform fee |
| **Disputed Session** | Refund based on admin decision (0-100%) | Payment based on admin decision (0-80%) | May absorb cost if inconclusive |

### 5.3 Session Confirmation Rules
| Timeframe | Action | Result |
|-----------|--------|--------|
| **Immediately after session** | Student shown confirmation prompt (in-app modal) | Encourages immediate confirmation |
| **Within 24 hours** | Student confirms or disputes | Payment released or held based on response |
| **After 24 hours (no response)** | Auto-confirmation triggered | Payment automatically released to instructor |
| **Dispute raised** | Payment held, support team reviews | Resolution based on evidence (join logs, history) |

### 5.4 Instructor Verification Rules
| Profile Change | Verification Required | Profile Visibility | Existing Bookings |
|---------------|----------------------|-------------------|------------------|
| **Initial submission** | Yes (manual admin review) | Hidden until approved | Cannot accept bookings |
| **Profile content edit** (bio, photo, video, background) | Yes (re-verification) | Hidden until re-approved | Existing bookings remain valid |
| **Availability change** | No | Remains visible | No impact |
| **Pricing change** | No | Remains visible | New price applies to new bookings only |
| **Subject addition/removal** | Yes (re-verification) | Hidden until re-approved | Existing bookings remain valid |

### 5.5 Booking Constraints
| Constraint | Value | Reason |
|-----------|-------|--------|
| **Minimum advance booking** | 2 hours | Allows instructor to prepare, reduces last-minute cancellations |
| **Maximum advance booking** | 30 days | Prevents calendar blocking too far in advance |
| **Session durations** | 25 min (trial), 50 min (regular) | Standard lesson lengths, aligned with pricing |
| **Buffer between sessions** | 5-10 minutes | Prevents back-to-back exhaustion, allows technical setup time |
| **No double-booking** | Enforced | Slot immediately blocked when booked |
| **Cancellation cutoff (full refund)** | 24 hours before | Balances student flexibility with instructor planning |

### 5.6 Review Rules
| Rule | Requirement | Reason |
|------|------------|--------|
| **Review eligibility** | Session status = `COMPLETED` | Only confirmed sessions can be reviewed |
| **Review window** | Within 30 days of session | Ensures reviews reflect recent experience |
| **Edits allowed** | Delete within 24h only, no edits | Prevents manipulation after instructor responds |
| **Instructor response** | One response per review, max 300 chars | Allows instructors to address concerns professionally |
| **Content moderation** | Automated profanity filter + manual review for reports | Maintains platform quality and professionalism |

---

## 6. Technical Requirements

### 6.1 Integrations

#### Google Meet API
**Purpose**: Video session platform
**Requirements**:
- Auto-generate Google Meet link at booking time
- Link active 10 minutes before session start
- Link expires after session end time + 30 minutes
- Calendar event creation (optional)

**Implementation**:
- Google Calendar API for event creation
- Google Meet link embedded in event
- Webhook for session start/end tracking (if available)

#### Stripe
**Purpose**: Payment processing (credit cards)
**Requirements**:
- Tokenization (no card storage on platform)
- Payment authorization + capture
- Refunds via API
- Stripe Connect for instructor payouts
- Webhook handlers for payment events:
  - `payment_intent.succeeded`
  - `payment_intent.failed`
  - `charge.refunded`
  - `payout.paid`

**Implementation**:
- Stripe Elements for secure card input
- Stripe Checkout (optional, for faster checkout)
- Stripe Dashboard for monitoring
- PCI DSS compliance (handled by Stripe)

#### PayPal
**Purpose**: Alternative payment method
**Requirements**:
- PayPal Checkout integration
- One-click checkout for returning users
- Refunds via API
- Payouts to instructor PayPal accounts

**Implementation**:
- PayPal JavaScript SDK
- Webhook handlers for payment events
- PayPal Sandbox for testing

#### SendGrid / AWS SES
**Purpose**: Transactional email service
**Requirements**:
- Email templates for:
  - Account verification
  - Booking confirmation
  - Session reminders
  - Payment notifications
  - Violation warnings
  - Verification decisions
- High deliverability rate (>95%)
- Bounce and complaint handling

**Implementation**:
- HTML email templates with dynamic content
- Unsubscribe management
- Email tracking (opens, clicks)
- Fallback SMTP provider (redundancy)

#### AWS S3 (or similar)
**Purpose**: File storage for photos, videos, documents
**Requirements**:
- Pre-signed URLs for secure uploads
- Public access for profile photos/videos (CDN)
- Private access for chat attachments (temporary URLs)
- Automatic file expiration for old chat attachments

**Implementation**:
- S3 buckets with appropriate permissions
- CloudFront CDN for fast delivery
- Lifecycle policies for old files
- Virus scanning (AWS GuardDuty or third-party)

### 6.2 Real-Time Features

#### WebSocket
**Purpose**: Real-time messaging and notifications
**Requirements**:
- Persistent connection for logged-in users
- Message delivery latency <1 second
- Typing indicators
- Read receipts
- Online/offline status
- Reconnection handling

**Implementation**:
- FastAPI WebSocket support
- Redis for WebSocket connection management (multi-server)
- Heartbeat/ping-pong for connection health
- Fallback to polling if WebSocket fails

#### Redis
**Purpose**: Caching and real-time data
**Use Cases**:
- Session data (JWT tokens, user sessions)
- WebSocket connection pool
- Rate limiting (API requests, messages)
- Caching frequently accessed data (instructor search results)
- Celery message broker

**Implementation**:
- Redis Cluster for high availability
- Appropriate TTLs for cached data
- Eviction policy: LRU (least recently used)

### 6.3 Background Jobs (Celery)

**Purpose**: Asynchronous task processing

**Scheduled Tasks**:
- **Session Reminders**: Every hour, check sessions starting in 12 hours, send emails/notifications
- **Auto-Confirmation**: Every hour, check sessions ended 24h ago without confirmation, auto-confirm and release payment
- **Payment Processing**: Daily, process pending payouts to instructors
- **Data Cleanup**: Weekly, archive old messages, delete expired files
- **Email Digests**: Weekly, send summary emails to instructors (earnings, upcoming sessions)

**On-Demand Tasks**:
- Send email notifications (booking, cancellation, payment)
- Process refunds
- Upload files to S3
- Generate thumbnails for videos

**Implementation**:
- Celery with Redis as broker
- Celery Beat for scheduled tasks
- Task retry logic (with exponential backoff)
- Task monitoring (Flower or similar)

### 6.4 Security Requirements

**Authentication**:
- JWT token-based (access token: 15 min, refresh token: 7 days)
- Password hashing: bcrypt with salt
- Account lockout: 5 failed attempts → 15 min cooldown
- Email verification required
- Password reset via secure token (expires in 1 hour)

**Authorization**:
- Role-based access control (RBAC)
- Endpoint protection: Decorators for role checking
- Resource ownership validation (users can only modify their own data)

**Data Protection**:
- HTTPS only (TLS 1.2+)
- Sensitive data encryption at rest (payment info, phone numbers)
- PII data handling compliance (GDPR, CCPA)
- Data anonymization in logs (mask emails, phone numbers)

**API Security**:
- Rate limiting: 100 requests/min per user, 10 requests/min for unauthenticated
- CORS: Whitelist trusted frontend origins
- Input validation: Pydantic schemas for all API requests
- SQL injection prevention: SQLAlchemy ORM (no raw SQL)
- XSS prevention: Sanitize user inputs, escape outputs

**File Upload Security**:
- File type validation (MIME type checking)
- File size limits enforced
- Virus scanning before storage
- Signed URLs for S3 uploads (prevent unauthorized uploads)

### 6.5 Performance Requirements

**Response Times** (95th percentile):
- API endpoints: <500ms
- Search results: <2 seconds
- File uploads: <10 seconds for 10MB file
- Real-time messages: <1 second delivery
- Payment processing: <5 seconds

**Scalability**:
- Support 10,000 concurrent users
- Handle 100 bookings/minute
- Database query optimization (indexes on frequently queried fields)
- Caching for expensive operations (Redis)
- Horizontal scaling for API servers (load balancer)

**Availability**:
- 99.9% uptime (target)
- Database replication (read replicas)
- Automated backups (daily full, hourly incremental)
- Disaster recovery plan (RTO: 4 hours, RPO: 1 hour)

---

## 7. Success Metrics (KPIs)

### 7.1 User Acquisition
- **New Instructor Signups**: Target 50/month (MVP), 200/month (6 months)
- **New Student Signups**: Target 200/month (MVP), 1000/month (6 months)
- **Instructor Verification Rate**: >70% of submitted profiles approved
- **Signup to First Booking (Students)**: <7 days average

### 7.2 Engagement
- **Active Instructors**: % of verified instructors with ≥1 session/month (Target: >50%)
- **Active Students**: % of registered students with ≥1 booking/month (Target: >30%)
- **Session Completion Rate**: >90% of scheduled sessions completed
- **Repeat Booking Rate**: % of students booking 2nd session (Target: >40%)

### 7.3 Quality
- **Average Instructor Rating**: >4.5 stars
- **Session Dispute Rate**: <2% of completed sessions
- **Messaging Violation Rate**: <5% of users with violations
- **Instructor No-Show Rate**: <1% of sessions
- **Student No-Show Rate**: <5% of sessions

### 7.4 Revenue
- **Gross Merchandise Value (GMV)**: Total session prices (Target: $10k/month MVP, $100k/month in 6 months)
- **Platform Revenue**: Total fees collected (20% of GMV)
- **Average Session Price**: $50-80 (varies by subject)
- **Payment Success Rate**: >98% of payment attempts successful
- **Refund Rate**: <5% of total revenue refunded

### 7.5 Operational
- **Verification Turnaround Time**: <48 hours (average)
- **Support Response Time**: <4 hours (business hours)
- **Dispute Resolution Time**: <72 hours (average)
- **Payout Processing Time**: <24 hours (approval to transfer)

---

## 8. Out of Scope (Future Enhancements)

### Phase 2 (Post-MVP)
- **Mobile Apps**: Native iOS and Android apps
- **Group Sessions**: Instructors can offer group classes (1-to-many)
- **Course Packages**: Students can buy bundles of sessions at discounted rates
- **Subscription Plans**: Students subscribe for regular weekly sessions
- **Advanced Search**: AI-powered tutor recommendations based on learning style
- **In-Platform Video**: Custom video platform (move away from Google Meet)
- **Whiteboard**: Interactive whiteboard for sessions
- **Session Recording**: Automatic recording with student consent
- **Gamification**: Badges, streaks, achievements for students and instructors
- **Referral Program**: Students and instructors refer friends for credits
- **Multi-Language Support**: Platform in multiple languages (Spanish, French, etc.)

### Phase 3 (Long-Term)
- **Corporate Accounts**: Companies buy bulk sessions for employees
- **School Partnerships**: Schools purchase platform access for students
- **Curriculum Builder**: Instructors create structured courses
- **Assignment Submission**: Students submit homework, instructors review
- **AI Teaching Assistant**: AI provides session summaries, learning insights
- **Marketplace for Materials**: Instructors sell study guides, worksheets
- **Live Chat Support**: Real-time customer support via chat
- **Automated Quality Assurance**: AI monitors session quality (audio/video issues)

---

## 9. Assumptions & Dependencies

### Assumptions
- Instructors have reliable internet and basic video setup (webcam, mic)
- Students are comfortable with online learning and basic tech
- Google Meet is acceptable for MVP (no need for custom video platform)
- Instructors are willing to wait 24h for payment after session (confirmation window)
- 20% platform fee is acceptable to instructors
- Email is primary communication channel (notifications)
- English is primary language for MVP

### Dependencies
- **Google Meet API**: Availability and stability
- **Stripe/PayPal**: API availability, compliance with payment regulations
- **AWS S3**: Uptime and performance for file storage
- **SendGrid/SES**: Email deliverability and sender reputation
- **Legal Compliance**: Privacy policies, terms of service, payment regulations
- **Support Team**: Availability for verification, moderation, dispute resolution (especially during early days)

---

## 10. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| **Low instructor signups** | High (no supply = no marketplace) | Medium | Aggressive instructor recruitment, reduce verification time, offer launch bonuses |
| **High verification rejection rate** | High (frustrates instructors) | Medium | Clear onboarding guidelines, examples, pre-submission checks, helpful rejection feedback |
| **Payment fraud** | High (financial loss) | Low | Stripe/PayPal fraud detection, manual review for high-value transactions, user reputation system |
| **Messaging violations** | Medium (platform reputation) | High | Robust automated detection, clear policies, progressive penalties, manual review |
| **Instructor no-shows** | High (student experience) | Low | Verification of credentials, reputation system, strict penalties, refunds + credits |
| **Session quality disputes** | Medium (support overhead) | Medium | Clear expectations set during booking, session logs for evidence, fair resolution process |
| **Google Meet outages** | High (sessions cannot happen) | Low | Monitor Google Meet status, have backup plan (Zoom integration), refund policy for outages |
| **Scalability issues** | High (platform downtime) | Medium | Load testing before launch, auto-scaling infrastructure, database optimization, caching |
| **Data breach** | Critical (legal/reputation) | Low | Security best practices, regular audits, encryption, compliance with GDPR/CCPA, cyber insurance |

---

## 11. Launch Checklist

### Pre-Launch (MVP)
- [ ] Core features implemented and tested
- [ ] Payment processing live (Stripe/PayPal)
- [ ] Google Meet integration working
- [ ] Email service configured (SendGrid/SES)
- [ ] File storage setup (AWS S3)
- [ ] Admin panel functional (verification, moderation)
- [ ] Terms of Service & Privacy Policy published
- [ ] Support email setup (support@platform.com)
- [ ] Load testing completed (handle expected traffic)
- [ ] Security audit completed
- [ ] Backup and disaster recovery tested

### Launch
- [ ] Soft launch with 10 beta instructors + 50 beta students
- [ ] Monitor errors, performance, user feedback
- [ ] Fix critical bugs
- [ ] Public launch announcement
- [ ] Marketing campaign (social media, ads, SEO)
- [ ] Instructor recruitment drive
- [ ] Student acquisition campaigns

### Post-Launch (First 30 Days)
- [ ] Daily monitoring of KPIs
- [ ] Collect user feedback (surveys, interviews)
- [ ] Prioritize bug fixes and UX improvements
- [ ] Weekly team retrospectives
- [ ] Iterate on verification process (reduce turnaround time)
- [ ] Optimize search and discovery (improve instructor visibility)
- [ ] Analyze payment success rate and refund reasons
- [ ] Build customer support knowledge base

---

## 12. Appendix

### A. Glossary
- **Instructor**: User providing tutoring services
- **Student**: User booking and receiving tutoring services
- **Session**: Scheduled tutoring appointment (25 or 50 minutes)
- **Trial Session**: Discounted 25-minute introductory session
- **Regular Session**: Standard 50-minute tutoring session
- **Verification**: Admin review and approval of instructor profile
- **Platform Fee**: Commission taken by platform (20% of session price)
- **Wallet**: Instructor account balance (accumulated earnings)
- **Payout**: Transfer of funds from wallet to instructor bank/PayPal
- **Violation**: Attempt to share contact info in pre-booking messages
- **Dispute**: Disagreement about session completion or quality
- **Confirmation**: Student acknowledgment that session happened (triggers payment)
- **No-Show**: When student or instructor doesn't join session
- **GMV**: Gross Merchandise Value (total session prices before fees)

### B. Example User Journeys

#### Journey 1: Sarah (New Instructor)
1. Signs up as instructor, verifies email
2. Completes 7-step onboarding (takes ~30 min)
3. Submits for verification
4. Waits 24 hours, receives approval email
5. Sets weekly availability (Mon-Fri 4-8pm)
6. Receives first booking from a student
7. Gets reminder 12h before session
8. Joins Google Meet, teaches 50-min Python lesson
9. Student confirms session after 2 hours
10. Sarah receives $80 in wallet (from $100 session, 20% fee)
11. After 5 sessions, Sarah withdraws $400 to PayPal

#### Journey 2: Alex (Student Seeking Calculus Help)
1. Signs up as student, verifies email
2. Searches for "Calculus" tutors
3. Filters by: Price <$50, Rating >4.5, Available this week
4. Clicks on instructor "Maria T."
5. Watches intro video, reads reviews (4.8 stars, 23 reviews)
6. Sends message: "Can you help with limits and derivatives?"
7. Maria responds in 30 min: "Absolutely! I specialize in Calculus 1."
8. Alex books a 25-min trial session for tomorrow 6pm
9. Pays $25 via credit card
10. Receives confirmation email with Google Meet link
11. Gets reminder 12h before
12. Joins session, gets helpful lesson on limits
13. Confirms session immediately after
14. Leaves 5-star review: "Great teacher! Very patient and clear."
15. Books 5 more sessions with Maria (now regular 50-min)

---

## Document Information

**Version**: 1.0
**Last Updated**: 2025-11-04
**Owner**: Product Team
**Status**: Approved for Development
**Next Review**: After MVP Launch

---

**End of PRD**
