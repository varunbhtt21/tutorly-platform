export interface User {
  id: number;
  email: string;
  role: 'student' | 'instructor' | 'admin';
  first_name: string;
  last_name: string;
  phone_number?: string;
  status: 'active' | 'pending' | 'suspended';
}

export interface Subject {
  id: number;
  name: string;
  slug: string;
  category?: string;
}

export interface InstructorProfile {
  id: number;
  user_id: number;
  user: User;
  headline: string;
  bio: string;
  country_of_birth?: string;
  languages: { language: string; proficiency: string }[];
  hourly_rate: number; // Simplified from regular/trial for UI
  trial_price: number;
  rating: number;
  review_count: number;
  total_sessions: number;
  subjects: { subject: Subject }[];
  is_onboarding_complete: boolean;
  photo_url?: string; // Mock field
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

// Form Types for Onboarding
export interface OnboardingData {
  step: number;
  about: {
    country: string;
    languages: { language: string; proficiency: string }[];
  };
  description: {
    headline: string;
    bio: string;
  };
  pricing: {
    regular: number;
    trial: number;
  };
  subjects: number[]; // IDs
  education: any[];
  experience: any[];
}